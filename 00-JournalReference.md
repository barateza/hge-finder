# Elite:Dangerous - API Player Journal

-   [Login](?p=login)
-   [Register](?p=register)
-   [](?m=rss)
-   Theme: Darkside
-   Theme: Lightside

[Elite: Dangerous Codex](https://edcodex.info/)

**Search**  
community tools, threads...

**Share**  
your E:D project, website...

**Follow**  
your favorite tools

-   [Home](.)
-   [Tools](?m=tools)
-   [API](?m=api)
-   [Threads](?m=threads)
-   [Community](?m=community)
-   [Toolbox](?m=toolbox)
    -   [Elite: Dangerous Timeline](?m=toolbox&p=timeline)
    -   [Ships](?m=toolbox&p=ships)
    -   [Seasons](?m=toolbox&p=extensions)
    -   [Sig generator](?m=toolbox&p=sign)

# Elite:Dangerous - Player Journal (From official manual)

Check the [Official thread](https://forums.frontier.co.uk/showthread.php/275151-Commanders-log-manual-and-data-sample) for feedbacks.  

1.  [Introduction](#f.1)
    1.  [ChangeLog](#f.1.1)
2.  [File Format](#f.2)
    1.  [File Location](#f.2.1)
    2.  [Heading entry](#f.2.2)
    3.  [Event Records](#f.2.3)
    4.  [Localisation](#f.2.4)
3.  [Startup](#f.3)
    1.  [ClearSavedGame](#f.3.1)
    2.  [NewCommander](#f.3.2)
    3.  [LoadGame](#f.3.3)
    4.  [Progress](#f.3.4)
    5.  [Rank](#f.3.5)
4.  [Travel](#f.4)
    1.  [Docked](#f.4.1)
    2.  [DockingCancelled](#f.4.2)
    3.  [DockingDenied](#f.4.3)
    4.  [DockingGranted](#f.4.4)
    5.  [DockingRequested](#f.4.5)
    6.  [DockingTimeout](#f.4.6)
    7.  [FSDJump](#f.4.7)
    8.  [Liftoff](#f.4.8)
    9.  [Location](#f.4.9)
    10.  [SupercruiseEntry](#f.4.10)
    11.  [SupercruiseExit](#f.4.11)
    12.  [Touchdown](#f.4.12)
    13.  [Undocked](#f.4.13)
5.  [Combat](#f.5)
    1.  [Bounty](#f.5.1)
    2.  [CapShipBond](#f.5.2)
    3.  [Died](#f.5.3)
    4.  [Died](#f.5.4)
    5.  [EscapeInterdiction](#f.5.5)
    6.  [FactionKillBond](#f.5.6)
    7.  [HeatDamage](#f.5.7)
    8.  [HeatWarning](#f.5.8)
    9.  [HullDamage](#f.5.9)
    10.  [Interdicted](#f.5.10)
    11.  [Interdiction](#f.5.11)
    12.  [PVPKill](#f.5.12)
    13.  [ShieldState](#f.5.13)
6.  [Exploration](#f.6)
    1.  [Scan](#f.6.1)
    2.  [MaterialCollected](#f.6.2)
    3.  [MaterialDiscarded](#f.6.3)
    4.  [MaterialDiscovered](#f.6.4)
    5.  [BuyExplorationData](#f.6.5)
    6.  [SellExplorationData](#f.6.6)
    7.  [Screenshot](#f.6.7)
7.  [Trade](#f.7)
    1.  [BuyTradeData](#f.7.1)
    2.  [CollectCargo](#f.7.2)
    3.  [EjectCargo](#f.7.3)
    4.  [MarketBuy](#f.7.4)
    5.  [MarketSell](#f.7.5)
    6.  [MiningRefined](#f.7.6)
8.  [Station Services](#f.8)
    1.  [BuyAmmo](#f.8.1)
    2.  [BuyDrones](#f.8.2)
    3.  [CommunityGoalDiscard](#f.8.3)
    4.  [CommunityGoalJoin](#f.8.4)
    5.  [CommunityGoalReward](#f.8.5)
    6.  [CrewAssign](#f.8.6)
    7.  [CrewFire](#f.8.7)
    8.  [CrewHire](#f.8.8)
    9.  [EngineerApply](#f.8.9)
    10.  [EngineerCraft](#f.8.10)
    11.  [EngineerProgress](#f.8.11)
    12.  [FetchRemoteModule](#f.8.12)
    13.  [MassModuleStore](#f.8.13)
    14.  [MissionAbandoned](#f.8.14)
    15.  [MissionAccepted](#f.8.15)
    16.  [MissionCompleted](#f.8.16)
    17.  [MissionFailed](#f.8.17)
    18.  [ModuleBuy](#f.8.18)
    19.  [ModuleRetrieve](#f.8.19)
    20.  [ModuleSell](#f.8.20)
    21.  [ModuleSellRemote](#f.8.21)
    22.  [ModuleStore](#f.8.22)
    23.  [ModuleSwap](#f.8.23)
    24.  [PayFines](#f.8.24)
    25.  [PayLegacyFines](#f.8.25)
    26.  [RedeemVoucher](#f.8.26)
    27.  [RefuelAll](#f.8.27)
    28.  [RefuelPartial](#f.8.28)
    29.  [Repair](#f.8.29)
    30.  [RepairAll](#f.8.30)
    31.  [RestockVehicle](#f.8.31)
    32.  [ScientificResearch](#f.8.32)
    33.  [SellDrones](#f.8.33)
    34.  [ShipyardBuy](#f.8.34)
    35.  [ShipyardNew](#f.8.35)
    36.  [ShipyardSell](#f.8.36)
    37.  [ShipyardTransfer](#f.8.37)
    38.  [ShipyardSwap](#f.8.38)
9.  [Powerplay](#f.9)
    1.  [PowerplayCollect](#f.9.1)
    2.  [PowerplayDefect](#f.9.2)
    3.  [PowerplayDeliver](#f.9.3)
    4.  [PowerplayFastTrack](#f.9.4)
    5.  [PowerplayJoin](#f.9.5)
    6.  [PowerplayLeave](#f.9.6)
    7.  [PowerplaySalary](#f.9.7)
    8.  [PowerplayVote](#f.9.8)
    9.  [PowerplayVoucher](#f.9.9)
10.  [Other Events](#f.10)
    1.  [ApproachSettlement](#f.10.1)
    2.  [CockpitBreached](#f.10.2)
    3.  [CommitCrime](#f.10.3)
    4.  [Continued](#f.10.4)
    5.  [DatalinkScan](#f.10.5)
    6.  [DatalinkVoucher](#f.10.6)
    7.  [DataScanned](#f.10.7)
    8.  [DockFighter](#f.10.8)
    9.  [DockSRV](#f.10.9)
    10.  [FuelScoop](#f.10.10)
    11.  [JetConeBoost](#f.10.11)
    12.  [JetConeDamage](#f.10.12)
    13.  [LaunchFighter](#f.10.13)
    14.  [LaunchSRV](#f.10.14)
    15.  [Promotion](#f.10.15)
    16.  [RebootRepair](#f.10.16)
    17.  [ReceiveText](#f.10.17)
    18.  [Resurrect](#f.10.18)
    19.  [SelfDestruct](#f.10.19)
    20.  [SendText](#f.10.20)
    21.  [Synthesis](#f.10.21)
    22.  [USSDrop](#f.10.22)
    23.  [VehicleSwitch](#f.10.23)
    24.  [WingAdd](#f.10.24)
    25.  [WingJoin](#f.10.25)
    26.  [WingLeave](#f.10.26)
11.  [Appendix](#f.11)
    1.  [Ranks](#f.11.1)
    2.  [{{anchor|Ref462662854}} Star Descriptions](#f.11.2)
    3.  [{{anchor|Ref462662870}} Planet Classes](#f.11.3)
    4.  [{{anchor|Ref462662884}} Atmosphere Classes](#f.11.4)
    5.  [{{anchor|Ref462662904}} Volcanism classes](#f.11.5)
    6.  [{{anchor|Ref462662962}} Crime types](#f.11.6)
    7.  [BodyType values](#f.11.7)

  

## Introduction

Elite:Dangerous writes a network log file primarily to help when investigating problems.  
Third-party tools developers have been reading some of the entries in the network log file, mainly in order to track the player's location.  
There is a clear demand from players for third-party tools, and from tools developers for more information from the game and/or server api.  
The new Player Journal provides a stream of information about gameplay events which can be used by tools developers to provide richer, more detailed tools to enhance the player experience. The data records written to this journal are much more high-level then that written to the network log.  
A short example of a player journal file (**_out of date, some events may have additional data_**):  

{ "timestamp":"2016-06-10T14:31:00Z", "event":"FileHeader", "part":1, "gameversion":"2.2", "build":"r113684 " },
{ "timestamp":"2016-06-10T14:32:03Z", "event":"LoadGame", "Commander":"HRC1", "Ship":"SideWinder", "ShipID":1, "GameMode":"Open", "Credits":600120, "Loan":0 }  
{ "timestamp":"2016-06-10T14:32:03Z", "event":"Rank", "Combat":0, "Trade":0, "Explore":1, "Empire":0, "Federation":0, "CQC":0 }  
{ "timestamp":"2016-06-10T14:32:03Z", "event":"Progress", "Combat":0, "Trade":0, "Explore":73, "Empire":0, "Federation":0, "CQC":0 }  
{ "timestamp":"2016-06-10T14:32:15Z", "event":"Location", "StarSystem":"Asellus Primus", "StarPos":\[-23.938,40.875,-1.344\] }  
{ "timestamp":"2016-06-10T14:32:16Z", "event":"Docked", "StationName":"Beagle 2 Landing", "StationType":"Coriolis" }  
{ "timestamp":"2016-06-10T14:32:38Z", "event":"RefuelAll", "Cost":12, "Amount":0.234493 }  
{ "timestamp":"2016-06-10T14:34:25Z", "event":"Undocked", "StationName":"Beagle 2 Landing", "StationType":"Coriolis" }  
{ "timestamp":"2016-06-10T14:35:00Z", "event":"FSDJump", "StarSystem":"HIP 78085", "StarPos":\[120.250,40.219,268.594\], "JumpDist":36.034 }  
{ ""timestamp":"2016-06-10T14:35:22Z", event":"Scan", "BodyName":"HIP 78085 A", "StarType":"G" }  
{ "timestamp":"2016-06-10T14:36:10Z", "event":"FSDJump", "StarSystem":"Praea Euq NW-W b1-3", "StarPos":\[120.719,34.188,271.750\], "JumpDist":6.823 }  
{ "timestamp":"2016-06-10T14:36:42Z", "event":"Scan", "BodyName":"Praea Euq NW-W b1-3", "StarType":"M" }  
{ "timestamp":"2016-06-10T14:38:50Z", "event":"Scan", "BodyName":"Praea Euq NW-W b1-3 3", "Description":"Icy body with neon rich atmosphere and major water geysers volcanism" }  
{ "timestamp":"2016-06-10T14:39:08Z", "event":"Scan", "BodyName":"Praea Euq NW-W b1-3 3 a", "Description":"Tidally locked Icy body" }  
{ "timestamp":"2016-06-10T14:41:03Z", "event":"FSDJump", "StarSystem":"Asellus Primus", "StarPos":\[-23.938,40.875,-1.344\], "JumpDist":39.112 }  
{ "timestamp":"2016-06-10T14:41:26Z", "event":"SupercruiseExit", "StarSystem":"Asellus Primus", "Body":"Beagle 2 Landing" }  
{ "timestamp":"2016-06-10T14:41:29Z", "event":"Docked", "StationName":"Beagle 2 Landing", "StationType":"Coriolis" }  
{ "timestamp":"2016-06-10T14:41:58Z", "event":"SellExplorationData", "Systems":\[ "HIP 78085", "Praea Euq NW-W b1-3" \], "Discovered":\[ "HIP 78085 A", "Praea Euq NW-W b1-3", "Praea Euq NW-W b1-3 3 a", "Praea Euq NW-W b1-3 3" \], "BaseValue":10822, "Bonus":3959 }

  

### ChangeLog

**Version 6**_published 26/Oct/2016 (for 2.2 public release)_****

  

Update manual with CommunityGoalDiscard and RepairAll (already implemented)

  

Clarify the 'SharedWithOthers' property on the 'Bounty' event

Clarify that EjectCargo/PowerplayOrigin is only recorded for cargo from _outlying systems_

  

Version 5  published 5/Oct/2016 (for 2.2 beta 5)

  

Include lists of star, planet, atmosphere, vulcanism and crime strings in appendix

**In Beta 6:**

\* Add a "ScientificResearch" event  

**In Beta 5:**

  

-   MaterialCollected: add Count property
-   Scan: include star's age and temperature, include orbital parameters for stars and other bodies, increase number of significant figures for rings statistics
-   The "Bounty" event now lists rewards separately per Faction
-   The "ReceiveText" event now logs text chat from NPCs, and indicates whether chat from other players is from wing, local, friend, or direct from another player
-   Add a "BodyType" param to "Location" and "SupercruiseExit" events
-   Add CommodityReward data to MissionCompleted event
-   Add ModuleSellRemote, FetchRemoteModule, MassModuleStore

**In Beta 4:**

  

-   Include Body info in Location event (bug fix)
-   Always write Docked property in Location event (bug fix)
-   Include Powerplay info in the FSDJump and Location events
-   Include PowerplayOrigin in CargoDumped event if relevant

**Version 4**_published 19/Sep/2016 (for 2.2 beta 1)_**** 

  

-   Add extra parameters to MissionAccepted events: destination info, and passenger info
-   Interdiction events IsPlayer value is always a bool
-   Clean up "smart quotes" and convert to "straight quotes"
-   Add a note about the heading entry in every continuation of the file
-   Add ApproachSettlement event

**Version 3**_published 30/Aug/2016_****

  

-   Include ShipID in Module outfitting events
-   Change some bool values from 1/0 to true/false
    -   Resurrect/Bankrupt
    -   Scan/TidalLock,Landable
    -   Interdicted/Submitted
    -   LaunchFighter/PlayerControlled
    -   EjectCargo/Abandoned
    -   CollectCargo/Stolen
    -   ShieldState/ShieldsUp
-   Include Major faction "Alliegance" in Location/FSDjump/Docked events
-   Include surface gravity, pressure, temperature for a planet
-   Include more info about rings when scanning star or planet
-   Add events for NPC Crew interaction
-   Localised text is in UTF8 encoding
-   Added events DatalinkVoucher and DataScanned
-   Added events JetConeBoost and JetConeDamage
-   Added BrokerPercentage value to PayFines and RedeemVoucher
-   Added ModuleStore and ModuleRetrieve
-   Added the PVPKill event
-   File saved in SavedGames folder
-   Added "Continued" event
-   Added MissionID parameter in mission events

Version2 **published 26/July/2016**

  

-   File is formatted as line-delimited json
-   Timestamp inside event object, ISO 8601 format
-   Fileheader format changed
-   Include faction info and faction state, for Starsystem and Station
-   New event for dropping out of supercruise at a USS
-   Interdiction events include extra info about the other player/NPC
-   Remove PowerplayNominate (duplicate for PowerplayVote)
-   Include gameplay mode, and credit balance in LoadGame
-   Include station name and type in Location event if docked at startup
-   Include Economy, Government and Security info for Starsystem on jump
-   Include Economy, Government and Security info for Station when docking
-   Include ship ID in shipyard entries
-   Reorganised format for data when killed by a wing of players
-   Record latitude and longitude when landing on planet
-   Automatic localisation of text symbols
-   Improved granularity of data, and additional info, for star and planet scans
-   Planet Scan: Landable property is now 0 or 1, not a quoted string
-   New HeatWarning and HeatDamage events
-   New ShieldState and HullDamage events
-   Report fuel used and fuel level on each jump
-   RestockVehicle: added 'count' property for purchasing multiple vehicles
-   Add events for DockingRequested, Denied, Granted etc
-   Add mission expiry time

Version 1 **was published 20/July/2016**

  

## File Format

The Player Journal is written in line-delimited JSON format (see son.org and jsonlines.org), to provide a standard format for ease of machine parsing, while still being intelligible to the human reader.  
Each Journal file is a series of lines each containing one Json object.  

### File Location

The journal files are written into the user's Saved Games folder, eg, for Windows:  
C:\\Users\\User Name\\Saved Games\\Frontier Developments\\Elite Dangerous\\  
The filename is of the form Journal**_.._**.log**_, similar to network log files  
_**

### Heading entry

The Heading record has a Json object with the following values:  

-   timestamp: the time in GMT, ISO 8601
-   part: the file part number
-   language: the language code
-   gameversion: which version of the game produced the log (will indicate if beta)
-   build: game build number

**Example:**  

{ "timestamp":"2016-07-22T10:20:01Z", "event":"fileheader", "part":1, "language":"French/FR", "gameversion":"2.2 Beta 1", "build":"r114123 " }

(If the play session goes on a long time, and the journal gets very large, the file will be closed and a new file started with an increased part number: the heading entry is added at the beginning of every file. See also the "Continued" event)  

### Event Records

Each event record is a json object.  
The object has a "timestamp" value with the time in ISO 8601 format, an "event":"eventname_" key-value pair identifying the type of event, followed by other key-value pairs providing additional information.  
The rest of this document describes each type of event that might be written into the journal, and the data values for each event.  
_

### Localisation

Some values written into the log use internal symbol IDs, as used by the game to lookup localised text strings. These have the form "$symbolname;"  
When such values are written into the log, the iocalised version of the string will also be written (UTF8 encoded), _as a separate key-value pair, with "\_Localised" appended to the key name._Examples throughout this document have not been updated with this extra localised format**_  
"Government":"$government\_PrisonColony;", "Government\_Localised":"Colonie pénitentiaire"  
_**

## Startup

### ClearSavedGame

When written: If you should ever reset your game  
**Parameters:**\* Name: commander name  
**Example:**  

{ "timestamp":"2016-06-10T14:32:03Z", "event":"ClearSavedGame", "Name":"HRC1" }

### NewCommander

When written: Creating a new commander  
**Parameters:**  

-   Name: (new) commander name
-   Package: selected starter package

**Example:**  

{ "timestamp":"2016-06-10T14:32:03Z", "event":"NewCommander", "Name":"HRC1", "Package":"ImperialBountyHunter" }

### LoadGame

When written: at startup, when loading from main menu into game  
**Parameters:**  

-   Commander: commander name
-   Ship: current ship type
-   ShipID: ship id number
-   StartLanded: true (only present if landed)
-   StartDead:true (only present if starting dead: see "Resurrect")
-   GameMode: Open, Solo or Group
-   Group: name of group (if in a group)
-   Credits: current credit balance
-   Loan: current loan

**Example:**  

{ "timestamp":"2016-06-10T14:32:03Z", "event":"LoadGame", "Commander":"HRC1", "Ship":"CobraMkIII", "ShipID":1, "GameMode":"Group", "Group":"Mobius", "Credits":600120, "Loan":0 }

  

### Progress

When written: at startup  
**Parameters:**  

-   Combat: percent progress to next rank
-   Trade: "
-   Explore: "
-   Empire: "
-   Federation: "
-   CQC: "

**Example:**  

{ "timestamp":"2016-06-10T14:32:03Z", "event":"Progress", "Combat":77, "Trade":9, "Explore":93, "Empire":0, "Federation":0, "CQC":0 }

  

### Rank

When written: at startup  
**Parameters:**  

-   Combat: rank on scale 0-8
-   Trade: rank on scale 0-8
-   Explore: rank on scale 0-8
-   Empire: military rank
-   Federation: military rank
-   CQC: rank on scale 0-8

**Example:**  

{ "timestamp":"2016-06-10T14:32:03Z", "event":"Rank", "Combat":2, "Trade":2, "Explore":5, "Empire":1, "Federation":3, "CQC":0 }

  

## Travel

### Docked

When written: when landing at landing pad in a space station, outpost, or surface settlement  
**Parameters:**  

-   StationName: name of station
-   StationType: type of station
-   StarSystem: name of system
-   CockpitBreach:true (only if landing with breached cockpit)
-   Faction: station's controlling faction
-   FactionState
-   Allegiance
-   Economy
-   Government
-   Security

**Example:**  

{ "timestamp":"2016-06-10T14:32:03Z", "event":"Docked", "StationName":"Kotov Refinery", "StationType":"Outpost", "StarSystem":"Wolf 289", "Faction":"Wolf 289 Gold Federal Industry", "FactionState":"CivilWar", "Allegiance":"Federation", "Economy":"$economy\_Extraction", "Government":"$government\_Corporate", "Security":"$SYSTEM\_SECURITY\_high\_anarchy;" }

  

### DockingCancelled

When written: when the player cancels a docking request  
**Parameters:**\* StationName: name of station  

### DockingDenied

When written: when the station denies a docking request  
**Parameters:**  

-   StationName: name of station
-   Reason: reason for denial

Reasons include: NoSpace, TooLarge, Hostile, Offences, Distance, ActiveFighter, NoReason  

### DockingGranted

When written: when a docking request is granted  
**Parameters:**  

-   StationName: name of station
-   LandingPad: pad number

\*  

### DockingRequested

When written: when the player requests docking at a station  
**Parameters:**\* StationName: name of station  

### DockingTimeout

When written: when a docking request has timed out  
**Parameters:**\* StationName: name of station  

### FSDJump

When written: when jumping from one star system to another  
**Parameters:**  

-   StarSystem: name of destination starsystem
-   StarPos: star position, as a Json array \[x, y, z\], in light years
-   Body: star's body name
-   JumpDist: distance jumped
-   FuelUsed
-   FuelLevel
-   BoostUsed: whether FSD boost was used
-   Faction: system controlling faction
-   FactionState
-   Allegiance
-   Economy
-   Government
-   Security

If the player is pledged to a Power in Powerplay, and the star system is involved in powerplay,  

-   Powers: a json array with the names of any powers contesting the system, or the name of the controlling power
-   PowerplayState: the system state - one of ("InPrepareRadius", "Prepared", "Exploited", "Contested", "Controlled", "Turmoil", "HomeSystem")

**Examples:**  

{ "timestamp":"2016-07-21T13:16:49Z", "event":"FSDJump", "StarSystem":"LP 98-132", "StarPos":\[-26.781,37.031,-4.594\], "Economy":"$economy\_Extraction;", "Allegiance":"Federation", "Government":"$government\_Anarchy;", "Security":"$SYSTEM\_SECURITY\_high\_anarchy;", "JumpDist":5.230, "FuelUsed":0.355614, "FuelLevel":12.079949, "Faction":"Brotherhood of LP 98-132", "FactionState":"Outbreak" }

  

{ "timestamp":"2016-09-21T14:15:41Z", "event":"FSDJump", "StarSystem":"Tau Bootis", "StarPos":\[0.094,48.781,14.625\], "Allegiance":"Federation", "Economy":"$economy\_Agri;", "Economy\_Localised":"Agriculture", "Government":"$government\_Democracy;", "Government\_Localised":"Democracy", "Security":"$SYSTEM\_SECURITY\_high;", "Security\_Localised":"High Security", "Power":"Edmund Mahon", "PowerplayState":"Controlled", "JumpDist":38.182, "FuelUsed":8.000000, "FuelLevel":11.066821, "Faction":"Values Party of Tau Bootis" }

  

### Liftoff

When written: when taking off from planet surface  
**Parameters:**  

-   Latitude
-   Longitude

**Example:**  

{ "timestamp":"2016-07-22T10:53:19Z", "event":"Liftoff", "Latitude":63.468872, "Longitude":157.599380 }

### Location

When written: at startup, or when being resurrected at a station  
**Parameters:**  

-   StarSystem: name of destination starsystem
-   StarPos: star position, as a Json array \[x, y, z\], in light years
-   Body: star or planet's body name
-   BodyType
-   Docked: (bool)
-   StationName: station name, (if docked)
-   StationType: (if docked)
-   Faction: star system controlling faction
-   FactionState
-   Allegiance
-   Economy
-   Government
-   Security

If the player is pledged to a Power in Powerplay, and the star system is involved in powerplay,  

-   Powers: a json array with the names of any powers contesting the system, or the name of the controlling power
-   PowerplayState: the system state - one of ("InPrepareRadius", "Prepared", "Exploited", "Contested", "Controlled", "Turmoil", "HomeSystem")

**Examples:**  

{ "timestamp":"2016-07-21T13:14:25Z", "event":"Location", "Docked":true, "StationName":"Azeban City", "StationType":"Coriolis", "StarSystem":"Eranin", "StarPos":\[-22.844,36.531,-1.188\], "Allegiance":"Alliance", "Economy":"$economy\_Agri;", "Government":"$government\_Communism;", "Security":$SYSTEM\_SECURITY\_medium;, "Faction":"Eranin Peoples Party" }

  

{ "timestamp":"2016-09-21T14:11:22Z", "event":"Location", "Docked":false, "StarSystem":"Alpha Centauri", "StarPos":\[3.031,-0.094,3.156\], "Allegiance":"Independent", "Economy":"$economy\_Extraction;", "Economy\_Localised":"Extraction", "Government":"$government\_Cooperative;", "Government\_Localised":"Cooperative", "Security":"$SYSTEM\_SECURITY\_medium;", "Security\_Localised":"Medium Security", "Body":"Alpha Centauri B 1", "Powers":\["Zachary Hudson"\], "PowerplayState":"Exploited", "Faction":"Hutton Orbital Truckers Co-Operative", "FactionState":"Outbreak" }

  

### SupercruiseEntry

When written: entering supercruise from normal space  
**Parameters:**\* Starsystem  
**Example:**  

{"timestamp":"2016-06-10T14:32:03Z", "event":"SupercruiseEntry", "StarSystem":"Yuetu" }

  

### SupercruiseExit

When written: leaving supercruise for normal space  
**Parameters:**  

-   Starsystem
-   Body
-   BodyType

**Example:**  

{ "timestamp":"2016-06-10T14:32:03Z", "event":"SupercruiseExit", "StarSystem":"Yuetu", "Body":"Yuetu B" }

  

### Touchdown

When written: landing on a planet surface  
**Parameters:**  

-   Latitude
-   Longitude

**Example:**  

{ "timestamp":"2016-07-22T10:38:46Z", "event":"Touchdown", "Latitude":63.468872, "Longitude":157.599380 }

### Undocked

When written: liftoff from a landing pad in a station, outpost or settlement  
**Parameters:**\* StationName: name of station  
**Example:**  

{ "timestamp":"2016-06-10T14:32:03Z", "event":"Undocked", "StationName":"Long Sight Base" }

## Combat

### Bounty

When written: player is awarded a bounty for a kill  
**Parameters:**  

-   Rewards: an array of Faction names and the Reward values, as the target can have multiple bounties payable by different factions
-   VictimFaction: the victim's faction
-   TotalReward
-   SharedWithOthers: if credit for the kill is shared with other players, this has the number of other players involved

**Example:**  

{ "timestamp":"2016-06-10T14:32:03Z", "event":"Bounty", "Rewards": \[ {"Faction":"Federation", "Reward":1000 }, {"Faction":"Nuenets Corp.", "Reward": 10280} \],"Target":"Skimmer", "TotalReward":11280, "VictimFaction":"MMU" }

### CapShipBond

When written: The player has been rewarded for a capital ship combat  
**Parameters:**  

-   Reward: value of award
-   AwardingFaction
-   VictimFaction

### Died

When written: player was killed  
**Parameters:**  

-   KillerName
-   KillerShip
-   KillerRank

**Example:**  

{ "timestamp":"2016-06-10T14:32:03Z", "event":"Died", "KillerName":"$ShipName\_Police\_Independent;", "KillerShip":"viper", "KillerRank":"Deadly" }

### Died

When written: player was killed by a wing  
**Parameters:**\* Killers: a JSON array of objects containing player name, ship, and rank  
**Example:**  

{ "timestamp":"2016-06-10T14:32:03Z", "event":"Died", "Killers":\[ { "Name":"Cmdr HRC1", "Ship":"Vulture", "Rank":"Competent" }, { "Name":"Cmdr HRC2", "Ship":"Python", "Rank":"Master" } \] }

### EscapeInterdiction

When written: Player has escaped interdiction  
**Parameters:**  

-   Interdictor: interdicting pilot name
-   IsPlayer: whether player or npc

**Example:**

{"timestamp":"2016-06-10T14:32:03Z", "event":"EscapeInterdiction", "Interdictor":"Hrc1", "IsPlayer":true }

### FactionKillBond

When written: Player rewarded for taking part in a combat zone  
**Parameters:**  

-   Reward
-   AwardingFaction
-   VictimFaction

**Example:**  

{"timestamp":"2016-06-10T14:32:03Z", "event":"FactionKillBond", "Reward": 500, "AwardingFaction":"Jarildekald Public Industry", "VictimFaction": "Lencali Freedom Party" }

### HeatDamage

When written: when taking damage due to overheating  
**Parameters:**none  

### HeatWarning

When written: when heat exceeds 100%  
**Parameters:** none  

### HullDamage

When written: when hull health drops below a threshold (20% steps)  
**Parameters:**\* Health  
**Example:**  

{ "timestamp":"2016-07-25T14:46:23Z", "event":"HullDamage", "Health":0.798496 }

{ "timestamp":"2016-07-25T14:46:23Z", "event":"HullDamage", "Health":0.595611 }

{ "timestamp":"2016-07-25T14:46:23Z", "event":"HullDamage", "Health":0.392725 }

{ "timestamp":"2016-07-25T14:46:26Z", "event":"HullDamage", "Health":0.188219 }

### Interdicted

When written: player was interdicted by player or npc  
**Parameters:**  

-   Submitted: true or false
-   Interdictor: interdicting pilot name
-   IsPlayer: whether player or npc
-   CombatRank: if player
-   Faction: if npc
-   Power: if npc working for a power

**Example:**  

{ "timestamp":"2016-06-10T14:32:03Z", "event":"interdicted", "Submitted":false, "Interdictor":"Dread Pirate Roberts", "IsPlayer":false, "Faction": "Timocani Purple Posse" }

### Interdiction

When written: player has (attempted to) interdict another player or npc  
**Parameters:**  

-   Success : true or false
-   Interdicted: victim pilot name
-   IsPlayer: whether player or npc
-   CombatRank: if a player
-   Faction: if an npc
-   Power: if npc working for power

**Example:**  

{ "timestamp":"2016-06-10T14:32:03Z", "event":"interdiction", "Success":true, "Interdicted":"Fred Flintstone", "IsPlayer":true, "CombatRank":5 }

### PVPKill

When written: when this player has killed another player  
**Parameters:**  

-   Victim: name of victim
-   CombatRank: victim's rank in range 0..8

### ShieldState

When written: when shields are disabled in combat, or recharged  
**Parameters:**\* ShieldsUp 0 when disabled, 1 when restored  
**Examples:**  

{ "timestamp":"2016-07-25T14:45:48Z", "event":"ShieldState", "ShieldsUp":false }

{ "timestamp":"2016-07-25T14:46:36Z", "event":"ShieldState", "ShieldsUp":true }

## Exploration

### Scan

**When Written:** detailed discovery scan of a star, planet or moon  
Parameters(star)  

-   Bodyname: name of body
-   DistanceFromArrivalLS
-   StarType: Stellar classification (for a star) - see 11.2
-   StellarMass: mass as multiple of Sol's mass
-   Radius
-   AbsoluteMagnitude
-   RotationPeriod (seconds)
-   SurfaceTemperature
-   Age\_MY: age in missions of years
-   Rings: \[ array \] - if present

Parameters(Planet/Moon)  

-   Bodyname: name of body
-   DistanceFromArrivalLS
-   TidalLock: 1 if tidally locked
-   TerraformState: Terraformable, Terraforming, Terraformed, or null
-   PlanetClass - see 11.3
-   Atmosphere - see 11.4
-   Volcanism - see 11.5
-   SurfaceGravity
-   SurfaceTemperature
-   SurfacePressure
-   Landable: true (if landable)
-   Materials: JSON object with material names and percentage occurrence
-   RotationPeriod (seconds)
-   Rings: \[ array of info \] - if rings present

Orbital Parameters for any Star/Planet/Moon (except main star of single-star system)  

-   SemiMajorAxis
-   Eccentricity
-   OrbitalInclination
-   Periapsis
-   OrbitalPeriod

Rings properties  

-   Name
-   RingClass
-   MassMT - ie in megatons
-   InnerRad
-   OuterRad

**Example:**  

{ "timestamp":"2016-09-22T10:40:44Z", "event":"Scan", "BodyName":"Bei Dou Sector JH-V b2-1 1", "DistanceFromArrivalLS":392.607605, "TidalLock":false, "TerraformState":"", "PlanetClass":"Icy body", "Atmosphere":"thin neon rich atmosphere", "Volcanism":"", "MassEM":0.190769, "Radius":4412562.000000, "SurfaceGravity":3.905130, "SurfaceTemperature":64.690628, "SurfacePressure":321.596558, "Landable":false, "SemiMajorAxis":117704065024.000000, "Eccentricity":0.000033, "Periapsis":5.692884, "OrbitalPeriod":43704092.000000, "RotationPeriod":104296.351563 }

  

### MaterialCollected

**When Written:** whenever materials are collected  
**Parameters:**  

-   Category: type of material (Raw/Encoded/Manufactured)
-   Name: name of material
-   Count: number of units collected

**Examples:**  

{ "timestamp":"2016-06-10T14:32:03Z", "event":"MaterialCollected", "Category":"Raw", "Name":"sulphur", "Count":2 }

{ "timestamp":"2016-06-10T14:32:03Z", "event":"MaterialCollected", "Category":"Encoded", "Name":"disruptedwakeechoes", "Count":1 }

### MaterialDiscarded

**When Written:** if materials are discarded  
**Parameters:**  

-   Category
-   Name
-   Count

**Example:**  

{ "timestamp":"2016-06-10T14:32:03Z", "event":"MaterialDiscarded", "Category":"Raw", "Name":"sulphur", "Count": 5 }

### MaterialDiscovered

**When Written:** when a new material is discovered  
**Parameters:**  

-   Category
-   Name
-   DiscoveryNumber

**Example:**  

{ "timestamp":"2016-06-10T14:32:03Z", "event":"MaterialDiscovered", "Category":"Manufactured", "Name":"focuscrystals", "DiscoveryNumber":3 }

### BuyExplorationData

**When Written:** when buying system data via the galaxy map  
**Parameters:**  

-   System
-   Cost

**Example:**  

{ "timestamp":"2016-06-10T14:32:03Z", "event":"BuyExplorationData", "System":"Styx", "Cost":352 }

  

### SellExplorationData

**When Written:** when selling exploration data in Cartographics  
**Parameters:**  

-   Systems: JSON array of system names
-   Discovered: JSON array of discovered bodies
-   BaseValue: value of systems
-   Bonus: bonus for first discoveries

**Example:**  

{ "timestamp":"2016-06-10T14:32:03Z", "event":"SellExplorationData", "Systems":\[ "HIP 78085", "Praea Euq NW-W b1-3" \], "Discovered":\[ "HIP 78085 A", "Praea Euq NW-W b1-3", "Praea Euq NW-W b1-3 3 a", "Praea Euq NW-W b1-3 3" \], "BaseValue":10822, "Bonus":3959 }

  

### Screenshot

**When Written:** when a screen snapshot is saved  
**Parameters:**  

-   Filename: filename of screenshot
-   Width: size in pixels
-   Height: size in pixels
-   System: current star system
-   Body: name of nearest body

**Example:**  

{ "timestamp":"2016-06-10T14:32:03Z", "event":"Screenshot", "Filename":"\_Screenshots/Screenshot\_0151.bmp", "Width":1600, "Height":900, "System":"Shinrarta Dezhra", "Body":"Founders World" }

  

## Trade

### BuyTradeData

**When Written:** when buying trade data in the galaxy map  
**Parameters:**  

-   System: star system requested
-   Cost: cost of data

**Example:**  

{ "timestamp":"2016-06-10T14:32:03Z", "event":"BuyTradeData", "System":"i Bootis", "Cost":100 }

  

### CollectCargo

**When Written:** when scooping cargo from space or planet surface  
**Parameters:**  

-   Type: cargo type
-   Stolen: whether stolen goods

**Example:**  

{ "timestamp":"2016-06-10T14:32:03Z", "event":"CollectCargo", "Type":"agriculturalmedicines", "Stolen":false }

### EjectCargo

**When Written:**  
**Parameters:**  

-   Type: cargo type
-   Count: number of units
-   Abandoned: whether 'abandoned'

If the cargo is related to powerplay delivery from outlying systems back to the centre_:\* PowerplayOrigin: starsystem name  
**Examples:**

{ "timestamp":"2016-06-10T14:32:03Z", "event":"EjectCargo", "Type":"tobacco", "Count":1, "Abandoned":true }

{ "timestamp":"2016-09-21T14:18:23Z", "event":"EjectCargo", "Type":"alliancelegaslativerecords", "Count":2, "Abandoned":true, "PowerplayOrigin":"Tau Bootis" }

_

### MarketBuy

**When Written:** when purchasing goods in the market  
**Parameters:**  

-   Type: cargo type
-   Count: number of units
-   BuyPrice: cost per unit
-   TotalCost: total cost

**Example:**  

{ "timestamp":"2016-06-10T14:32:03Z", "event":"MarketBuy", "Type":"foodcartridges", "Count":10, "BuyPrice":39, "TotalCost":390 }

### MarketSell

**When Written:** when selling goods in the market  
**Parameters:**  

-   Type: cargo type
-   Count: number of units
-   SellPrice: price per unit
-   TotalSale: total sale value
-   AvgPricePaid: average price paid
-   IllegalGoods: (not always present) whether goods are illegal here
-   StolenGoods: (not always present) whether goods were stolen
-   BlackMarket: (not always present) whether selling in a black market

**Examples:**  

{ "timestamp":"2016-06-10T14:32:03Z", "event":"MarketSell", "Type":"agriculturalmedicines", "Count":3, "SellPrice":1360, "TotalSale":4080, "AvgPricePaid":304 }

{ "event":"MarketSell", "Type":"mineraloil", "Count":9, "SellPrice":72, "TotalSale":648, "AvgPricePaid":0, "StolenGoods":true, "BlackMarket":true }

### MiningRefined

**When Written:** when mining fragments are converted unto a unit of cargo by refinery  
**Parameters:**\* Type: cargo type  
**Example:**  

{ "timestamp":"2016-06-10T14:32:03Z", "event":"MiningRefined", "Type:"Gold" }

## Station Services

### BuyAmmo

**When Written:** when purchasing ammunition  
**Parameters:**\* Cost  
**Example:**  

{ "timestamp":"2016-06-10T14:32:03Z", "event":"BuyAmmo", "Cost":80 }

### BuyDrones

**When Written:** when purchasing drones  
**Parameters:**  

-   Type
-   Count
-   BuyPrice
-   TotalCost

**Example:**  

{ "timestamp":"2016-06-10T14:32:03Z", "event":"BuyDrones", "Type":"Drones", "Count":2, "SellPrice":101, "TotalCost":202 }

### CommunityGoalDiscard

When written: when opting out of a community goal  
**Parameters:**  

-   Name
-   System

### CommunityGoalJoin

**When Written:** when signing up to a community goal  
**Parameters:**  

-   Name
-   System

### CommunityGoalReward

**When Written:** when receiving a reward for a community goal  
**Parameters:**  

-   Name
-   System
-   Reward

### CrewAssign

When written: when changing the task assignment of a member of crew  
**Parameters:**  

-   Name
-   Role

**Example:**  

{ "timestamp":"2016-08-09T08:45:31Z", "event":"CrewAssign", "Name":"Dannie Koller", "Role":"Active" }

### CrewFire

When written: when dismissing a member of crew  
**Parameters:**\* Name  
**Example:**  

{ "timestamp":"2016-08-09T08:46:11Z", "event":"CrewFire", "Name":"Whitney Pruitt-Munoz" }

### CrewHire

When written: when engaging a new member of crew  
**Parameters:**  

-   Name
-   Faction
-   Cost
-   Combat Rank

**Example:**  

{ "timestamp":"2016-08-09T08:46:29Z", "event":"CrewHire", "Name":"Margaret Parrish", "Faction":"The Dark Wheel", "Cost":15000, "CombatRank":1 }

### EngineerApply

**When Written:** when applying an engineer's upgrade to a module  
**Parameters:**  

-   Engineer: name of engineer
-   Blueprint: blueprint being applied
-   Level: crafting level
-   Override: whether overriding special effect

**Example:**  

{ "timestamp":"2016-06-10T14:32:03Z", "event":"EngineerApply", "Engineer":"Elvira Martuuk", "Blueprint":"ShieldGenerator\_Reinforced", "Level":1 }

### EngineerCraft

**When Written:** when requesting an engineer upgrade  
**Parameters:**  

-   Engineer: name of engineer
-   Blueprint: name of blueprint
-   Level: crafting level
-   Ingredients: JSON object with names and quantities of materials required

**Example:**  

{ "timestamp":"2016-06-10T14:32:03Z", "event":"EngineerCraft", "Engineer":"Elvira Martuuk", "Blueprint":"FSD\_LongRange", "Level":2, "Ingredients":{"praseodymium":1, "disruptedwakeechoes":3, "chemicalprocessors":2, "arsenic":2 } }

  

### EngineerProgress

**When Written:** when a player increases their access to an engineer  
Parameters  

-   Engineer: name of engineer
-   Rank: rank reached (when unlocked)
-   Progress: progress stage (Invited/Acquainted/Unlocked/Barred)

**Examples:**  

{ "timestamp":"2016-06-10T14:32:03Z", "event":"EngineerProgress", "Progress":"Unlocked", "Engineer":"Elvira Martuuk" }

{ "timestamp":"2016-06-10T14:32:03Z", "event":"EngineerProgress", "Engineer":"Elvira Martuuk", "Rank":2 }

### FetchRemoteModule

  
When written: when requesting a module is transferred from storage at another station  
**Parameters:**  

-   StorageSlot
-   StoredItem
-   ServerId
-   TransferCost
-   Ship
-   ShipId

### MassModuleStore

When written: when putting multiple modules into storage  
**Parameters:**  

-   Ship
-   ShipId
-   Items: Array of records
    -   Slot
    -   Name
    -   EngineerModifications (only present if modified)

### MissionAbandoned

**When Written:** when a mission has been abandoned  
**Parameters:**  

-   Name: name of mission
-   MissionID

**Example:**  

{ "timestamp":"2016-06-10T14:32:03Z", "event":"MissionAbandoned", "Name":"Mission\_Collect\_name", "MissionID":65343025 }

### MissionAccepted

**When Written:** when starting a mission  
**Parameters:**  

-   Name: name of mission
-   Faction: faction offering mission
-   MissionID

Optional Parameters (depending on mission type)  

-   Commodity: commodity type
-   Count: number required / to deliver
-   Target: name of target
-   TargetType: type of target
-   TargetFaction: target's faction
-   Expiry: mission expiry time, in ISO 8601
-   DestinationSystem
-   DestinationStation
-   PassengerCount
-   PassengerVIPs: bool
-   PassengerWanted: bool
-   PassengerType: eg Tourist, Soldier, Explorer,...

**Example:**  

{ "timestamp":"2016-07-26T11:36:44Z", "event":"MissionAccepted", "Faction":"Tsu Network", "Name":"Mission\_Collect", "MissionID":65343026, "Commodity":"$Fish\_Name;", "Commodity\_Localised":"Fish", "Count":2, "Expiry":"2016-07-27T15:56:23Z" }

### MissionCompleted

**When Written:** when a mission is completed  
**Parameters:**  

-   Name: mission type
-   Faction: faction name
-   MissionID

Optional parameters (depending on mission type)  

-   Commodity
-   Count
-   Target
-   TargetType
-   TargetFaction
-   Reward: value of reward
-   Donation: donation offered (for altruism missions)
-   PermitsAwarded:\[\] (names of any permits awarded, as a JSON array)
-   CommodityReward:\[\] (names and counts of any commodity rewards)

**Example:**  

{ "timestamp":"2016-09-30T08:37:38Z", "event":"MissionCompleted", "Faction":"Maljenni Inc", "Name":"Mission\_Delivery\_name", "MissionID":65347208, "Commodity":"$Cobalt\_Name;", "Commodity\_Localised":"Cobalt", "Count":14, "DestinationSystem":"Maljenni", "DestinationStation":"Bowersox Enterprise", "Reward":0, "CommodityReward":\[ { "Name": "ArticulationMotors", "Count": 2 } \] }

  

### MissionFailed

**When Written:** when a mission has failed  
**Parameters:**  

-   Name: name of mission
-   MissionID

### ModuleBuy

**When Written:** when buying a module in outfitting  
**Parameters:**  

-   Slot: the outfitting slot
-   BuyItem: the module being purchased
-   BuyPrice: price paid
-   Ship: the players ship
-   ShipID

If replacing an existing module:  

-   SellItem: item being sold
-   SellPrice: sale price

**Example:**  

{ "timestamp":"2016-06-10T14:32:03Z", "event":"ModuleBuy", "Slot":"MediumHardpoint2", "SellItem":"hpt\_pulselaser\_fixed\_medium", "SellPrice":0, "BuyItem":"hpt\_multicannon\_gimbal\_medium", "BuyPrice":50018, "Ship":"cobramkiii","ShipID":1 }

  

### ModuleRetrieve

When written: when fetching a previously stored module  
**Parameters:**  

-   Slot
-   Ship
-   ShipID
-   RetrievedItem
-   EngineerModifications: name of modification blueprint, if any
-   SwapOutItem (if slot was not empty)
-   Cost

### ModuleSell

**When Written:** when selling a module in outfitting  
**Parameters:**  

-   Slot
-   SellItem
-   SellPrice
-   Ship
-   ShipID

**Example:**

{ "timestamp":"2016-06-10T14:32:03Z", "event":"ModuleSell", "Slot":"Slot06\_Size2", "SellItem":"int\_cargorack\_size1\_class1", "SellPrice":877, "Ship":"asp", "ShipID":1 }

  

### ModuleSellRemote

  
When written: when selling a module in storage at another station  
**Parameters:**  

-   StorageSlot
-   SellItem
-   ServerId
-   SellPrice
-   Ship
-   ShipId

### ModuleStore

When written: when storing a module in Outfitting  
**Parameters:**  

-   Slot
-   Ship
-   ShipID
-   StoredItem
-   EngineerModifications: name of modification blueprint, if any
-   ReplacementItem (if a core module)
-   Cost (if any)

### ModuleSwap

**When Written:** when moving a module to a different slot on the ship  
**Parameters:**  

-   FromSlot
-   ToSlot
-   FromItem
-   ToItem
-   Ship
-   ShipID

**Examples:**  

{ "timestamp":"2016-06-10T14:32:03Z", "event":"ModuleSwap", "FromSlot":"MediumHardpoint1", "ToSlot":"MediumHardpoint2", "FromItem":"hpt\_pulselaser\_fixed\_medium", "ToItem":"hpt\_multicannon\_gimbal\_medium", "Ship":"cobramkiii", "ShipID":1 }

  

{ "timestamp":"2016-06-10T14:32:03Z", "event":"ModuleSwap", "FromSlot":"SmallHardpoint2", "ToSlot":"SmallHardpoint1", "FromItem":"hpt\_pulselaserburst\_fixed\_small\_scatter", "ToItem":"Null", "Ship":"cobramkiii", "ShipID":1 }

  

### PayFines

**When Written:** when paying fines  
**Parameters:**  

-   Amount: (total amount paid , including any broker fee)
-   BrokerPercentage (present if paid via a Broker)

**Example:**

{ "timestamp":"2016-06-10T14:32:03Z", "event":"PayFines", "Amount":1791 }

### PayLegacyFines

**When Written:** when paying legacy fines  
**Parameters:**  

-   Amount (total amount paid, including any broker fee)
-   BrokerPercentage (present if paid through a broker)

### RedeemVoucher

  
**When Written:** when claiming payment for combat bounties and bonds  
**Parameters:**  

-   Type
-   Amount: (Net amount received, after any broker fee)
-   BrokerPercenentage (if redeemed through a broker)

**Example:**

{ "timestamp":"2016-06-10T14:32:03Z", "event":"RedeemVoucher", "Type":"bounty", "Amount":1000 }

  

### RefuelAll

**When Written:** when refuelling (full tank)  
**Parameters:**  

-   Cost: cost of fuel
-   Amount: tons of fuel purchased

**Example:**  

{ "timestamp":"2016-06-10T14:32:03Z", "event":"RefuelAll", "Cost":317, "Amount":6.322901 }

### RefuelPartial

**When Written:** when refuelling (10%)  
**Parameters:**  

-   Cost: cost of fuel
-   Amount: tons of fuel purchased

**Example:**  

{ "timestamp":"2016-06-10T14:32:03Z", "event":"RefuelPartial", "Cost":83, "Amount":1.649000 }

### Repair

**When Written:** when repairing the ship  
**Parameters:**  

-   Item: all, wear, hull, paint, or name of module
-   Cost: cost of repair

**Example:**  

{ "timestamp":"2016-06-10T14:32:03Z", "event":"Repair", "Item":"int\_powerplant\_size3\_class5", "Cost":1100 }

  

### RepairAll

When written: when repairing everything  
**Parameters:**\* Cost  
\*  

### RestockVehicle

**When Written:** when purchasing an SRV or Fighter  
**Parameters:**  

-   Type: type of vehicle being purchased (SRV or fighter model)
-   Loadout: variant
-   Cost: purchase cost
-   Count: number of vehicles purchased

**Example:**  

{ "timestamp":"2016-06-10T14:32:03Z", "event":"RestockVehicle", "Type":"SRV", "Loadout":"starter", "Cost":1030, "Count":1 }

### ScientificResearch

When written: when contributing materials to a "research" community goal  
**Parameters:**  

-   Name: material name
-   Category
-   Count

\*  

### SellDrones

**When Written:** when selling unwanted drones back to the market  
**Parameters:**  

-   Type
-   Count
-   SellPrice
-   TotalSale

**Example:**  

{ "timestamp":"2016-06-10T14:32:03Z", "event":"SellDrones", "Type":"Drones", "Count":1, "SellPrice":91, "TotalSale":91 }

### ShipyardBuy

**When Written:** when buying a new ship in the shipyard  
**Parameters:**  

-   ShipType: ship being purchased
-   ShipPrice: purchase cost
-   StoreOldShip: (if storing old ship) ship type being stored
-   StoreShipID
-   SellOldShip: (if selling current ship) ship type being sold
-   SellShipID
-   SellPrice: (if selling current ship) ship sale price

Note: the new ship's ShipID will be logged in a separate event after the purchase  
**Example:**  

{ "timestamp":"2016-07-21T14:36:38Z", "event":"ShipyardBuy", "ShipType":"hauler", "ShipPrice":46262, "StoreOldShip":"SideWinder", "StoreShipID":2 }

### ShipyardNew

When written: after a new ship has been purchased  
**Parameters:**  

-   ShipType
-   ShipID

**Example:**  

{ "timestamp":"2016-07-21T14:36:38Z", "event":"ShipyardNew", "ShipType":"hauler", "ShipID":4 }

### ShipyardSell

**When Written:** when selling a ship stored in the shipyard  
**Parameters:**  

-   ShipType: type of ship being sold
-   SellShipID
-   ShipPrice: sale price
-   System: (if ship is in another system) name of system

**Example:**  

{ "timestamp":"2016-07-21T15:12:19Z", "event":"ShipyardSell", "ShipType":"Adder", "SellShipID":6, "ShipPrice":79027, "System":"Eranin" }

  

### ShipyardTransfer

**When Written:** when requesting a ship at another station be transported to this station  
**Parameters:**  

-   ShipType: type of ship
-   ShipID
-   System: where it is
-   Distance: how far away
-   TransferPrice: cost of transfer

**Example:**  

{ "timestamp":"2016-07-21T15:19:49Z", "event":"ShipyardTransfer", "ShipType":"SideWinder", "ShipID":7, "System":"Eranin", "Distance":85.639145, "TransferPrice":580 }

  

### ShipyardSwap

**When Written:** when switching to another ship already stored at this station  
**Parameters:**  

-   ShipType: type of ship being switched to
-   ShipID
-   StoreOldShip: (if storing old ship) type of ship being stored
-   StoreShipID
-   SellOldShip: (if selling old ship) type of ship being sold
-   SellShipID

Example  

{ "timestamp":"2016-07-21T14:36:06Z", "event":"ShipyardSwap", "ShipType":"sidewinder", "ShipID":10, "StoreOldShip":"Asp", "StoreShipID":2 }

## Powerplay

### PowerplayCollect

When written: when collecting powerplay commodities for delivery  
**Parameters:**  

-   Power: name of power
-   Type: type of commodity
-   Count: number of units

**Example:**  

{ "timestamp":"2016-06-10T14:32:03Z", "event":"PowerplayCollect", "Power":"Li Yong-Rui", "Type":"siriusfranchisepackage", "Count":10 }

### PowerplayDefect

When written: when a player defects from one power to another  
**Parameters:**  

-   FromPower
-   ToPower

**Example:**  

{ "timestamp":"2016-06-10T14:32:03Z", "event":"PowerplayDefect", "FromPower":"Zachary Hudson", "ToPower":"Li Yong-Rui" }

### PowerplayDeliver

When written: when delivering powerplay commodities  
**Parameters:**  

-   Power
-   Type
-   Count

**Example:**  

{ "timestamp":"2016-06-10T14:32:03Z", "event":"PowerplayDeliver", "Power":"Li Yong-Rui", "Type":"siriusfranchisepackage", "Count":10 }

### PowerplayFastTrack

When written: when paying to fast-track allocation of commodities  
**Parameters:**  

-   Power
-   Cost

### PowerplayJoin

When written: when joining up with a power  
**Parameters:**\* Power  
**Example:**  

{ "timestamp":"2016-06-10T14:32:03Z", "event":"PowerplayJoin", "Power":"Zachary Hudson" }

### PowerplayLeave

When written: when leaving a power  
**Parameters:**\* Power  
**Example:**  

{ "timestamp":"2016-06-10T14:32:03Z", "event":"PowerplayLeave", "Power":"Li Yong-Rui" }

### PowerplaySalary

When written: when receiving salary payment from a power  
**Parameters:**  

-   Power
-   Amount

### PowerplayVote

When written: when voting for a system expansion  
**Parameters:**  

-   Power
-   Votes
-   System

### PowerplayVoucher

When written: when receiving payment for powerplay combat  
**Parameters:**  

-   Power
-   Systems:\[name,name\]

## Other Events

### ApproachSettlement

  
When written: when approaching a planetary settlement  
**Parameters:**\* Name  

### CockpitBreached

When written: when cockpit canopy is breached  
**Parameters:** none  
**Example:**  

{ "timestamp":"2016-06-10T14:32:03Z", "event":"CockpitBreached" }

### CommitCrime

When written: when a crime is recorded against the player  
**Parameters:**  

-   CrimeType - see 11.6
-   Faction

Optional parameters (depending on crime)  

-   Victim
-   Fine
-   Bounty

**Examples:**  

{ "timestamp":"2016-06-10T14:32:03Z", "event":"CommitCrime", "CrimeType":"assault", "Faction":"The Pilots Federation", "Victim":"Potapinski", "Bounty":210 }

{ "timestamp":"2016-06-10T14:32:03Z", "event":"CommitCrime", "CrimeType":"fireInNoFireZone", "Faction":"Jarildekald Public Industry", "Fine":100 }

### Continued

When written: if the journal file grows to 500k lines, we write this event, close the file, and start a new one  
**Parameters:**\* Part: next part number  

### DatalinkScan

When written: when scanning a data link  
**Parameters:**\* Message: message from data link  

### DatalinkVoucher

When written: when scanning a datalink generates a reward  
**Parameters:**  

-   Reward: value in credits
-   VictimFaction
-   PayeeFaction

### DataScanned

When written: when scanning some types of data links  
**Parameters:**\* Type  
Type will typically be one of "DataLink", "DataPoint", "ListeningPost", "AbandonedDataLog", "WreckedShip", etc  

### DockFighter

When written: when docking a fighter back with the mothership  
**Parameters:** none  
**Example:**  

{ "timestamp":"2016-06-10T14:32:03Z", "event":"DockFighter" }

### DockSRV

When written: when docking an SRV with the ship  
**Parameters:** none  

### FuelScoop

When written: when scooping fuel from a star  
**Parameters:**  

-   Scooped: tons fuel scooped
-   Total: total fuel level after scooping

**Example:**  

{ "timestamp":"2016-06-10T14:32:03Z", "event":"FuelScoop", "Scooped":0.498700, "Total":16.000000 }

### JetConeBoost

When written: when enough material has been collected from a solar jet code (at a white dwarf or neutron star) for a jump boost  
**Parameters:**\* BoostValue  

### JetConeDamage

When written: when passing through the jet code from a white dwarf or neutron star has caused damage to a ship module  
**Parameters:**\* Module: the name of the module that has taken some damage  

### LaunchFighter

When written: when launching a fighter  
**Parameters:**  

-   Loadout
-   PlayerControlled: whether player is controlling the fighter from launch

{ "timestamp":"2016-06-10T14:32:03Z", "event":"LaunchFighter", "Loadout":"starter", "PlayerControlled":true }

### LaunchSRV

When written: deploying the SRV from a ship onto planet surface  
**Parameters:**\* Loadout  

### Promotion

When written: when the player's rank increases  
**Parameters:** one of the following  

-   Combat: new rank
-   Trade: new rank
-   Explore: new rank
-   CQC: new rank

**Example:**  

{ "timestamp":"2016-06-10T14:32:03Z", "event":"Promotion", "Explore":2 }

### RebootRepair

When written: when the 'reboot repair' function is used  
**Parameters:**\* Modules: JSON array of names of modules repaired  
**Example:**  

{ "timestamp":"2016-06-10T14:32:03Z", "event":"RebootRepair", "Modules":\[ "MainEngines", "TinyHardpoint1" \] }

### ReceiveText

When written: when a text message is received from another player or npc  
**Parameters:**  

-   From
-   Message
-   Channel: (wing/local/voicechat/friend/player/npc)

### Resurrect

When written: when the player restarts after death  
**Parameters:**  

-   Option: the option selected on the insurance rebuy screen
-   Cost: the price paid
-   Bankrupt: whether the commander declared bankruptcy

### SelfDestruct

When written: when the 'self destruct' function is used  
**Parameters:** none  

### SendText

When written: when a text message is sent to another player  
**Parameters:**  

-   To
-   Message

**Example:**  

{ "timestamp":"2016-06-10T14:32:03Z", "event":"SendText", "To":"HRC-2", "Message":"zoom" }

### Synthesis

When written: when synthesis is used to repair or rearm  
**Parameters:**  

-   Name: synthesis blueprint
-   Materials: JSON object listing materials used and quantities
    

**Example:**  

{ "timestamp":"2016-06-10T14:32:03Z", "event":"Synthesis", "Name":"Repair Basic", "Materials":{ "iron":2, "nickel":1 } }

### USSDrop

When written: when dropping from Supercruise at a USS  
**Parameters:**  

-   USSType: description of USS
-   USSThreat: threat level

**Example:**  

{ "timestamp":"2016-06-10T14:32:03Z", "event":"USSDrop", "USSType":"Disrupted wake echoes", "USSThreat": 0 }

### VehicleSwitch

When written: when switching control between the main ship and a fighter  
**Parameters:**\* To: ( Mothership/Fighter)  
**Examples:**  

{ "timestamp":"2016-06-10T14:32:03Z", "event":"VehicleSwitch", "To":"Fighter" }

{ "timestamp":"2016-06-10T14:32:03Z", "event":"VehicleSwitch", "To":"Mothership" }

### WingAdd

When written: another player has joined the wing  
**Parameters:**\* Name  
**Example:**  

{ "timestamp":"2016-06-10T14:32:03Z", "event":"WingAdd", "Name":"HRC-2" }

### WingJoin

When written: this player has joined a wing  
**Parameters:**\* Others: JSON array of other player names already in wing  
**Example:**  

{ "timestamp":"2016-06-10T14:32:03Z", "event":"WingJoin", "Others":\[ "HRC1" \] }

### WingLeave

When written: this player has left a wing  
**Parameters:** none  
**Example:**  

{ "timestamp":"2016-06-10T14:32:03Z", "event":"WingLeave" }

## Appendix

### Ranks

Combat ranks**_: 0='Harmless', 1='Mostly Harmless', 2='Novice', 3='Competent', 4='Expert', 5='Master', 6='Dangerous', 7='Deadly', 8='Elite'  
_**Trade ranks**_: 0='Penniless', 1='Mostly Pennliess', 2='Peddler', 3='Dealer', 4='Merchant', 5='Broker', 6='Entrepreneur', 7='Tycoon', 8='Elite'  
_**Exploration ranks**_: 0='Aimless', 1='Mostly Aimless', 2='Scout', 3='Surveyor', 4='Explorer', 5='Pathfinder', 6='Ranger', 7='Pioneer', 8='Elite'  
_**Federation ranks**_: 0='None', 1='Recruit', 2='Cadet', 3='Midshipman', 4='Petty Officer', 5='Chief Petty Officer', 6='Warrant Officer', 7='Ensign', 8='Lieutenant', 9='Lt. Commander', 10='Post Commander', 11= 'Post Captain', 12= 'Rear Admiral', 13='Vice Admiral', 14='Admiral'  
_**Empire ranks**_: 0='None', 1='Outsider', 2='Serf', 3='Master', 4='Squire', 5='Knight', 6='Lord', 7='Baron', 8='Viscount ', 9='Count', 10= 'Earl', 11='Marquis' 12='Duke', 13='Prince', 14='King'  
_**CQC ranks: 0='Helpless', 1='Mostly Helpless', 2='Amateur', 3='Semi Professional', 4='Professional', 5='Champion', 6='Hero', 7='Legend', 8='Elite'  

### {{anchor|Ref462662854}} Star Descriptions

(_Main sequence_:) O B A F G K M L T Y  
(_Proto stars_:) TTS AeBe  
(_Wolf-Rayet_:) W WN WNC WC WO  
(_Carbon stars_:) CS C CN CJ CH CHd  
MS S  
(_white dwarfs_:) D DA DAB DAO DAZ DAV DB DBZ DBV DO DOV DQ DC DCV DX  
N (=_Neutron_)  
H (=_Black Hole_)  
X (=_exotic_)  
SupermassiveBlackHole  
A\_BlueWhiteSuperGiant  
F\_WhiteSuperGiant  
M\_RedSuperGiant  
M\_RedGiant  
K\_OrangeGiant  
RoguePlanet  
Nebula  
StellarRemnantNebula  

### {{anchor|Ref462662870}} Planet Classes

Metal rich body  
High metal content body  
Rocky body  
Icy body  
Rocky ice body  
Earthlike body  
Water world  
Ammonia world  
Water giant  
Water giant with life  
Gas giant with water based life  
Gas giant with ammonia based life  
Sudarsky class I gas giant (also class II, III, IV, V)  
Helium rich gas giant  
Helium gas giant  

### {{anchor|Ref462662884}} Atmosphere Classes

No atmosphere  
Suitable for water-based life  
Ammonia and oxygen  
Ammonia  
Water  
Carbon dioxide  
Sulphur dioxide  
Nitrogen  
Water-rich  
Methane-rich  
Ammonia-rich  
Carbon dioxide-rich  
Methane  
Helium  
Silicate vapour  
Metallic vapour  
Neon-rich  
Argon-rich  
Neon  
Argon  
Oxygen  

### {{anchor|Ref462662904}} Volcanism classes

(all with possible 'minor' or 'major' qualifier)  
None  
Water Magma  
Sulphur Dioxide Magma  
Ammonia Magma  
Methane Magma  
Nitrogen Magma  
Silicate Magma  
Metallic Magma  
Water Geysers  
Carbon Dioxide Geysers  
Ammonia Geysers  
Methane Geysers  
Nitrogen Geysers  
Helium Geysers  
Silicate Vapour Geysers  

### {{anchor|Ref462662962}} Crime types

Assault  
Murder  
Piracy  
Interdiction  
IllegalCargo  
DisobeyPolice  
FireInNoFireZone  
FireInStation  
DumpingDangerous  
DumpingNearStation  
DockingMinor\_BlockingAirlock  
DockingMajor\_BlockingAirlock  
DockingMinor\_BlockingLandingPad  
DockingMajor\_BlockingLandingPad  
DockingMinor\_Trespass  
DockingMajor\_Trespass  
CollidedAtSpeedInNoFireZone  
CollidedAtSpeedInNoFireZone\_HullDamage  

### BodyType values

"Null" (eg the barycentre of a binary star system)  
"Star"  
"Planet"  
"PlanetaryRing"  
"StellarRing"  
"Station"  
"AsteroidCluster"  

## About

-   [Who we are](?m=who)
-   [Contact us](?m=contact)

## EDCodex

-   [Sitemap](?m=sitemap)
-   [Rss feeds](?m=rss)
-   [EDCodex stats](?m=stats)

## Privacy

-   [Legal & Privacy policy](?m=privacy)

> EDCodex is an unofficial website about the game Elite: Dangerous (property of Frontier Developments)

  <script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.4/jquery.min.js" type="text/javascript"></script><script src="https://ajax.googleapis.com/ajax/libs/jqueryui/1.11.4/jquery-ui.min.js" type="text/javascript"></script><script src="js/main.js?v=5.35" type="text/javascript"></script>

![](chrome-extension://llimhhconnjiflfimocjggfjdlmlhblm/img/svg/view-selection.svg)

![](chrome-extension://llimhhconnjiflfimocjggfjdlmlhblm/img/svg/play-round.svg)

![](chrome-extension://llimhhconnjiflfimocjggfjdlmlhblm/img/svg/google-translate.svg)

![](chrome-extension://llimhhconnjiflfimocjggfjdlmlhblm/img/svg/twitter.svg)

![](chrome-extension://llimhhconnjiflfimocjggfjdlmlhblm/img/svg/settings.svg)

![](chrome-extension://llimhhconnjiflfimocjggfjdlmlhblm/img/svg/pencil.svg)

![](chrome-extension://llimhhconnjiflfimocjggfjdlmlhblm/img/svg/folder.svg)

Everything

Update

![](chrome-extension://llimhhconnjiflfimocjggfjdlmlhblm/img/png/icon.png)

![](chrome-extension://llimhhconnjiflfimocjggfjdlmlhblm/img/svg/headphones.svg)

![](chrome-extension://llimhhconnjiflfimocjggfjdlmlhblm/img/svg/edit-text-file-2.svg)

![](chrome-extension://llimhhconnjiflfimocjggfjdlmlhblm/img/svg/erase.svg)

![](chrome-extension://llimhhconnjiflfimocjggfjdlmlhblm/img/svg/translation.svg)

![](chrome-extension://llimhhconnjiflfimocjggfjdlmlhblm/img/svg/print.svg)

![](chrome-extension://llimhhconnjiflfimocjggfjdlmlhblm/img/svg/scroll-down.svg)

![](chrome-extension://llimhhconnjiflfimocjggfjdlmlhblm/img/svg/tune.svg)

![](chrome-extension://llimhhconnjiflfimocjggfjdlmlhblm/img/svg/bookmark-2.svg)

![](chrome-extension://llimhhconnjiflfimocjggfjdlmlhblm/img/svg/expand.svg)

![](chrome-extension://llimhhconnjiflfimocjggfjdlmlhblm/img/svg/close.svg)

![](chrome-extension://llimhhconnjiflfimocjggfjdlmlhblm/img/svg/skip-to-start.svg)

![](chrome-extension://llimhhconnjiflfimocjggfjdlmlhblm/img/svg/play.svg) ![](chrome-extension://llimhhconnjiflfimocjggfjdlmlhblm/img/svg/pause.svg)

![](chrome-extension://llimhhconnjiflfimocjggfjdlmlhblm/img/svg/end.svg)

![](chrome-extension://llimhhconnjiflfimocjggfjdlmlhblm/img/svg/audio.svg)Voice options

![](chrome-extension://llimhhconnjiflfimocjggfjdlmlhblm/img/svg/close.svg)

**Aa** TYPOGRAPHY

Font Arial Arial Black Athelas Comic Sans MS Courier New Courier Didot Georgia Gill Sans Helvetica Impact Iowan Old Style Palatino Optima Sans-serif Sassoon Primary Seravek Serif Times New Roman Trebuchet MS OpenDyslexic OpenDyslexic Mono OpenDyslexic Bold OpenDyslexic Italic OpenDyslexic BoldItalic LexendDeca Lexend Exa Lexend Giga Lexend Mega Lexend Peta Lexend Tera Lexend Zetta LexieReadable LexieReadable Bold Lora Lora Bold Lora Italic Lora BoldItalic Verdana Text Align

  

  

  

  

Text Size

19

Line Height

30

Letter Spacing

0.2

Width

Save

THEMES

Current Theme Delete

To change the extension and app theme, go to the [**Settings page**](#/)

DISPLAY

 Outline Images  Meta  Author  Reading Time  Source URL

Save

READING RULER

 Display Ruler

Color

Opacity

0.5

Height

40

Position

45

Save

AUTO-RUN RULES PREMIUM

Automatically activate Reader Mode on specific websites by using regex. [**Learn more**](https://readermode.io/features/auto-run)

Save

{ } CUSTOM CSS PREMIUM

 Use custom css

Add your own CSS to customize the article's layout or design [**Learn more**](https://help.readermode.io/using-reader-mode/custom-css)

Save

TRANSLATE

Default translation language: 🇿🇦 Afrikaans 🇦🇱 Albanian 🇸🇦 Arabic 🇦🇿 Azerbaijani 🏴󠁥󠁳󠁰󠁶󠁿 Basque 🇧🇩 Bengali 🇧🇾 Belarusian 🇧🇬 Bulgarian 🏴󠁥󠁳󠁰󠁶󠁿 Catalan 🇨🇳 Chinese Simplified 🇨🇳 Chinese Traditional 🇭🇷 Croatian 🇨🇿 Czech 🇩🇰 Danish 🇳🇱 Dutch 🇬🇧 English 🏴󠁥󠁳󠁰󠁶󠁿 Esperanto 🇪🇪 Estonian 🇵🇭 Filipino 🇫🇮 Finnish 🇫🇷 French 🇪🇸 Galician 🇬🇪 Georgian 🇩🇪 German 🇬🇷 Greek 🇮🇳 Gujarati 🇭🇹 Haitian Creole 🇮🇱 Hebrew 🇮🇳 Hindi 🇭🇺 Hungarian 🇮🇸 Icelandic 🇮🇩 Indonesian 🇮🇪 Irish 🇮🇹 Italian 🇯🇵 Japanese 🇮🇳 Kannada 🇰🇷 Korean 🏴󠁥󠁳󠁰󠁶󠁿 Latin 🇱🇻 Latvian 🇱🇹 Lithuanian 🇲🇰 Macedonian 🇲🇾 Malay 🇲🇹 Maltese 🇳🇴 Norwegian 🇮🇷 Persian 🇵🇱 Polish 🇵🇹 Portuguese 🇷🇴 Romanian 🇷🇺 Russian 🇷🇸 Serbian 🇸🇰 Slovak 🇸🇮 Slovenian 🇪🇸 Spanish 🏴󠁥󠁳󠁰󠁶󠁿 Swahili 🇸🇪 Swedish 🇮🇳 Tamil 🇮🇳 Telugu 🇹🇭 Thai 🇹🇷 Turkish 🇺🇦 Ukrainian 🇵🇰 Urdu 🇻🇳 Vietnamese 🇬🇧 Welsh 🇮🇱 Yiddish

Set

Translate

[](#/ "Undo")

Cancel

Save

Cancel

Save

OUTLINE