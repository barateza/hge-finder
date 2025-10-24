"""Material inference engine for HGE signals.

Determines what materials are likely to spawn based on system properties,
using the official Elite Dangerous HGE material spawning rules.
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

        # Rule 1: Federal systems
        if allegiance_norm and "federal" in allegiance_norm:
            materials.update(MaterialInference.FEDERAL_MATERIALS.keys())

        # Rule 2: Imperial systems
        if allegiance_norm and "empire" in allegiance_norm:
            materials.update(MaterialInference.IMPERIAL_MATERIALS.keys())

        # Rule 3: Civil Unrest faction state
        if state_norm and "civil unrest" in state_norm:
            materials.update(MaterialInference.CIVIL_UNREST_MATERIALS.keys())

        # Rule 4: War or Civil War faction states
        if state_norm and ("war" in state_norm or "civil war" in state_norm):
            materials.update(MaterialInference.WAR_MATERIALS.keys())

        # Rule 5: Outbreak state with population > 1,000,000
        if state_norm and "outbreak" in state_norm and population and population > 1_000_000:
            materials.update(MaterialInference.OUTBREAK_MATERIALS.keys())

        # Rule 6: Boom or Expansion faction states
        if state_norm and ("boom" in state_norm or "expansion" in state_norm):
            materials.update(MaterialInference.BOOM_EXPANSION_MATERIALS.keys())

        # Build result list
        all_material_dicts = [
            MaterialInference.FEDERAL_MATERIALS,
            MaterialInference.IMPERIAL_MATERIALS,
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
