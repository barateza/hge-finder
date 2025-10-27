"""Material inference engine for HGE signals.

Determines what materials are likely to spawn based on system properties,
using the official Elite Dangerous HGE material spawning rules.

IMPORTANT: Data Freshness Notes
================================

System properties come from two sources:
1. Real-time: system_name, timestamp, coordinates (from EDDN)
2. Cached: allegiance, state, government, population (from EDSM)

EDSM data may be up to 24 hours stale after server ticks. This affects
material inference accuracy when Famine/Boom/War states change post-tick
but before EDSM updates.

Impact on material inference:
- Pre-tick: Material inference is 100% accurate
- Post-tick (first 24h): May infer wrong materials if state changed
- The app shows best-guess materials based on last-known state
- Users will see correct materials once EDSM syncs (usually < 1h)
- Multiple reports in same system average out inaccuracy

Example scenario:
- 14:00 - Boom ends, state changes to "None", EDDN reports system
- 14:05 - App gets "Proto Alloys" via material inference (old state)
- 15:30 - EDSM updates state to "None"
- 15:31 - Next report infers correct materials, corrects display

This is acceptable because:
1. It only happens post-tick (usually daily, known window)
2. Multiple players report same system, old guess gets overwritten
3. EDSM syncs relatively quickly (within an hour usually)
4. Better to show best-guess than nothing
"""

import logging
from typing import List, Optional, Set
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class MaterialInfo:
    """Information about a specific material."""
    
    name: str
    """Material name."""
    
    category: str
    """Category: Manufactured, Raw, Encoded, etc."""
    
    rarity: str
    """Rarity level."""
    
    source: str
    """Why this material spawns (e.g., 'Federal system', 'Civil Unrest')."""


class MaterialInference:
    """Infer HGE spawned materials from system state and allegiance.
    
    Based on official Elite Dangerous HGE material table:
    https://elite-dangerous.fandom.com/wiki/Unidentified_Signal_Source#High_Grade_Emissions
    """

    # Material definitions
    FEDERAL_MATERIALS = {
        "Core Dynamics Composites": MaterialInfo(
            name="Core Dynamics Composites",
            category="Manufactured",
            rarity="Very Rare",
            source="Federal systems"
        ),
        "Proprietary Composites": MaterialInfo(
            name="Proprietary Composites",
            category="Manufactured",
            rarity="Very Rare",
            source="Federal systems"
        ),
    }

    IMPERIAL_MATERIALS = {
        "Imperial Shielding": MaterialInfo(
            name="Imperial Shielding",
            category="Manufactured",
            rarity="Very Rare",
            source="Imperial systems"
        ),
    }

    CIVIL_UNREST_MATERIALS = {
        "Improvised Components": MaterialInfo(
            name="Improvised Components",
            category="Manufactured",
            rarity="Very Rare",
            source="Civil Unrest faction state"
        ),
    }

    WAR_MATERIALS = {
        "Military Grade Alloys": MaterialInfo(
            name="Military Grade Alloys",
            category="Manufactured",
            rarity="Very Rare",
            source="War or Civil War faction state"
        ),
        "Military Supercapacitors": MaterialInfo(
            name="Military Supercapacitors",
            category="Manufactured",
            rarity="Very Rare",
            source="War or Civil War faction state"
        ),
    }

    OUTBREAK_MATERIALS = {
        "Pharmaceutical Isolators": MaterialInfo(
            name="Pharmaceutical Isolators",
            category="Manufactured",
            rarity="Very Rare",
            source="Outbreak state (pop > 1M)"
        ),
    }

    BOOM_EXPANSION_MATERIALS = {
        "Proto Heat Radiators": MaterialInfo(
            name="Proto Heat Radiators",
            category="Manufactured",
            rarity="Very Rare",
            source="Boom or Expansion faction state"
        ),
        "Proto Light Alloys": MaterialInfo(
            name="Proto Light Alloys",
            category="Manufactured",
            rarity="Very Rare",
            source="Boom or Expansion faction state"
        ),
        "Proto Radiolic Alloys": MaterialInfo(
            name="Proto Radiolic Alloys",
            category="Manufactured",
            rarity="Very Rare",
            source="Boom or Expansion faction state"
        ),
    }

    # Alliance/Independent default materials (Proto Light Alloys, Proto Radiolic Alloys)
    # These are part of BOOM_EXPANSION_MATERIALS but also the default for Alliance/Independent
    ALLIANCE_INDEPENDENT_MATERIALS = {
        "Proto Light Alloys": MaterialInfo(
            name="Proto Light Alloys",
            category="Manufactured",
            rarity="Very Rare",
            source="Alliance or Independent systems"
        ),
        "Proto Radiolic Alloys": MaterialInfo(
            name="Proto Radiolic Alloys",
            category="Manufactured",
            rarity="Very Rare",
            source="Alliance or Independent systems"
        ),
    }

    @staticmethod
    def infer_materials(
        allegiance: Optional[str] = None,
        state: Optional[str] = None,
        population: Optional[int] = None,
    ) -> List[MaterialInfo]:
        """
        Infer HGE spawned materials from system properties.

        Multiple conditions can apply, in which case materials from all applicable
        categories are combined and randomly chosen in-game.

        Args:
            allegiance: System allegiance (Federation, Empire, Alliance, Independent)
            state: Current faction state (War, Civil Unrest, Outbreak, Boom, Expansion, Civil War)
            population: System population

        Returns:
            List of possible materials that could spawn
        """
        materials: Set[str] = set()

        # Normalize inputs
        allegiance_norm = (allegiance or "").lower() if allegiance else None
        state_norm = (state or "").lower() if state else None

        # Rule 1: Federal systems (allegiance = "Federation")
        if allegiance_norm == "federation":
            materials.update(MaterialInference.FEDERAL_MATERIALS.keys())

        # Rule 2: Imperial systems (allegiance = "Empire")
        if allegiance_norm == "empire":
            materials.update(MaterialInference.IMPERIAL_MATERIALS.keys())

        # Rule 3: Alliance or Independent systems (default materials)
        if allegiance_norm in ("alliance", "independent"):
            materials.update(MaterialInference.ALLIANCE_INDEPENDENT_MATERIALS.keys())

        # Rule 4: Civil Unrest faction state
        if state_norm and "civil unrest" in state_norm:
            materials.update(MaterialInference.CIVIL_UNREST_MATERIALS.keys())

        # Rule 5: War or Civil War faction states
        if state_norm and ("war" in state_norm or "civil war" in state_norm):
            materials.update(MaterialInference.WAR_MATERIALS.keys())

        # Rule 6: Outbreak state with population > 1,000,000
        if state_norm and "outbreak" in state_norm and population and population > 1_000_000:
            materials.update(MaterialInference.OUTBREAK_MATERIALS.keys())

        # Rule 7: Boom or Expansion faction states
        if state_norm and ("boom" in state_norm or "expansion" in state_norm):
            materials.update(MaterialInference.BOOM_EXPANSION_MATERIALS.keys())

        # Build result list
        all_material_dicts = [
            MaterialInference.FEDERAL_MATERIALS,
            MaterialInference.IMPERIAL_MATERIALS,
            MaterialInference.ALLIANCE_INDEPENDENT_MATERIALS,
            MaterialInference.CIVIL_UNREST_MATERIALS,
            MaterialInference.WAR_MATERIALS,
            MaterialInference.OUTBREAK_MATERIALS,
            MaterialInference.BOOM_EXPANSION_MATERIALS,
        ]

        result = []
        for material_name in materials:
            for material_dict in all_material_dicts:
                if material_name in material_dict:
                    result.append(material_dict[material_name])
                    break

        return sorted(result, key=lambda m: m.name)

    @staticmethod
    def format_materials(materials: List[MaterialInfo]) -> dict:
        """
        Format materials for JSON output.

        Args:
            materials: List of MaterialInfo objects

        Returns:
            Dictionary with material count and list of material details
        """
        return {
            "count": len(materials),
            "materials": [
                {
                    "name": m.name,
                    "rarity": m.rarity,
                    "source": m.source,
                }
                for m in materials
            ]
        }
