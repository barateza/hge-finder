# HGE Notifier - System Architecture

This document provides a comprehensive overview of the HGE Notifier system architecture, including data flow, component interactions, and module dependencies.

## Table of Contents

1. [System Overview](#system-overview)
2. [Data Flow](#data-flow)
3. [Component Architecture](#component-architecture)
4. [Module Dependencies](#module-dependencies)
5. [User Interface Architecture](#user-interface-architecture)
6. [Real-Time Communication](#real-time-communication)
7. [Notification Pipeline](#notification-pipeline)
8. [Deployment Model](#deployment-model)

---

## System Overview

The HGE Notifier is a Python application that monitors Elite Dangerous EDDN for High Grade Emission (HGE) signals and displays their distance from the player's current location.

```mermaid
graph TB
    subgraph "Data Sources"
        EDDN["EDDN Network<br/>(ZMQ Stream)"]
        Journal["Elite Dangerous<br/>Journal Files"]
        EDSM["EDSM API<br/>(System Coordinates)"]
    end
    
    subgraph "Core Engine"
        Manager["HGENotifierManager<br/>(Orchestrator)"]
        EDDNMon["EDDNMonitor"]
        JournalParse["JournalParser"]
        DistCalc["DistanceCalculator"]
        SysInfo["SystemInfoLookup"]
    end
    
    subgraph "Data Storage"
        CoordDB["CoordinateDatabase<br/>(Local Cache)"]
        SignalHist["Signal History<br/>(In-Memory)"]
    end
    
    subgraph "User Interfaces"
        CLI["CLI Interface<br/>(Terminal UI)"]
        Web["Web Dashboard<br/>(Flask)"]
    end
    
    subgraph "Notifications"
        NotifMgr["NotificationManager"]
        Discord["Discord Webhook"]
    end
    
    EDDN -->|HGE Signals| EDDNMon
    Journal -->|Location Events| JournalParse
    EDSM -->|Coordinates| SysInfo
    
    EDDNMon -->|Signals| Manager
    JournalParse -->|Locations| Manager
    
    Manager -->|Query| CoordDB
    Manager -->|Store| SignalHist
    Manager -->|Lookup| SysInfo
    Manager -->|Calculate| DistCalc
    
    Manager -->|Updates| CLI
    Manager -->|Updates| Web
    Manager -->|Alert| NotifMgr
    
    NotifMgr -->|Send| Discord
    
    EDSM -->|Cache| CoordDB
```

---

## Data Flow

### Signal Processing Pipeline

```mermaid
sequenceDiagram
    participant EDDN as EDDN Stream
    participant EDDNMon as EDDNMonitor
    participant Manager as HGENotifierManager
    participant SysInfo as SystemInfoLookup
    participant CoordDB as CoordinateDatabase
    participant DistCalc as DistanceCalculator
    participant UI as User Interface

    EDDN->>EDDNMon: HGE USS Signal
    EDDNMon->>Manager: _on_new_hge_signal()
    
    Manager->>SysInfo: get_system_info()
    SysInfo->>EDSM: Query system data
    SysInfo->>Manager: Return allegiance, state, etc.
    
    Manager->>CoordDB: lookup_system_coordinates()
    CoordDB->>Manager: Return x, y, z coordinates
    
    Manager->>DistCalc: calculate_distance()
    DistCalc->>Manager: Return distance in light-years
    
    Manager->>Manager: Append to signal_history
    Manager->>UI: Emit WebSocket event
    UI->>UI: Display signal & distance
```

### Location Update Pipeline

```mermaid
sequenceDiagram
    participant Journal as Journal File
    participant Parser as JournalParser
    participant Watcher as Watchdog
    participant Manager as HGENotifierManager
    participant CoordDB as CoordinateDatabase
    participant UI as User Interface

    Journal->>Watcher: File modification
    Watcher->>Parser: _on_modified()
    Parser->>Parser: Parse JSON events
    
    alt Location Event Detected
        Parser->>CoordDB: lookup_system_coordinates()
        CoordDB->>Parser: Return coordinates
        Parser->>Manager: _on_location_change()
        Manager->>Manager: Update current_location
        Manager->>UI: Emit location update
    end
    
    alt HGE Event Detected (in journal)
        Parser->>Manager: _on_new_hge_signal()
        Manager->>Manager: Process HGE
    end
```

---

## Component Architecture

### Core Components

```mermaid
graph LR
    subgraph "EDDN Module"
        EDDNMon["EDDNMonitor"]
        EDDNClient["ZMQ Client"]
        HGESig["HGESignal<br/>Data Model"]
    end
    
    subgraph "Journal Module"
        JournalParse["JournalParser"]
        Watcher["File Watcher"]
        CmdLoc["CommanderLocation<br/>Data Model"]
    end
    
    subgraph "Distance Module"
        DistCalc["DistanceCalculator"]
        CoordDB["CoordinateDatabase"]
        Coords["System Coordinates<br/>Data Model"]
    end
    
    subgraph "Core Module"
        Manager["HGENotifierManager"]
    end
    
    subgraph "Notifications"
        NotifMgr["NotificationManager"]
        Alert["Alert<br/>Config Model"]
        Discord["DiscordNotifier"]
    end
    
    subgraph "Web Interface"
        Flask["Flask Server"]
        WebSocket["WebSocketManager"]
        Routes["API Routes"]
        Templates["HTML Templates"]
    end
    
    subgraph "CLI Interface"
        CLI["CLI Manager"]
        TUI["Terminal UI<br/>Dashboard"]
    end
    
    EDDNClient -->|Parse| EDDNMon
    EDDNMon -->|Create| HGESig
    
    Watcher -->|Monitor| JournalParse
    JournalParse -->|Create| CmdLoc
    
    DistCalc -->|Use| CoordDB
    CoordDB -->|Cache| Coords
    
    Manager -->|Use| EDDNMon
    Manager -->|Use| JournalParse
    Manager -->|Use| DistCalc
    Manager -->|Use| NotifMgr
    
    NotifMgr -->|Check| Alert
    NotifMgr -->|Send| Discord
    
    Manager -->|Broadcast| WebSocket
    Flask -->|Use| WebSocket
    Flask -->|Serve| Routes
    Routes -->|Render| Templates
    
    Manager -->|Update| CLI
    CLI -->|Display| TUI
```

---

## Module Dependencies

### Import Dependencies

```mermaid
graph TB
    Main["__main__"]
    
    CLI["cli.py"]
    Core["core.py"]
    Web["web/__init__.py"]
    WebSocket["web/websocket.py"]
    
    EDDN["eddn/__init__.py"]
    Journal["journal/__init__.py"]
    Distance["distance/coordinates.py"]
    Notifications["notifications/manager.py"]
    Config["config/settings.py"]
    
    Main -->|imports| CLI
    Main -->|imports| Core
    Main -->|imports| Web
    Main -->|imports| Config
    
    Core -->|imports| EDDN
    Core -->|imports| Journal
    Core -->|imports| Distance
    Core -->|imports| Notifications
    Core -->|imports| Config
    Core -->|imports| WebSocket
    
    Web -->|imports| Core
    Web -->|imports| WebSocket
    Web -->|imports| Config
    
    WebSocket -->|imports| Config
    
    CLI -->|imports| Core
    CLI -->|imports| Config
    
    EDDN -->|imports| Config
    Journal -->|imports| Config
    Distance -->|imports| Config
    Notifications -->|imports| Config
```

### External Dependencies

```mermaid
graph LR
    App["HGE Notifier"]
    
    subgraph "Web Framework"
        Flask["Flask"]
        SocketIO["python-socketio"]
        EngineIO["python-engineio"]
    end
    
    subgraph "Data Streaming"
        ZMQ["pyzmq"]
        Watchdog["watchdog"]
    end
    
    subgraph "Network"
        Requests["requests"]
    end
    
    subgraph "Config Management"
        DotEnv["python-dotenv"]
    end
    
    subgraph "Server"
        Uvicorn["uvicorn"]
        ASGI["asgiref"]
    end
    
    App -->|uses| Flask
    App -->|uses| ZMQ
    App -->|uses| Watchdog
    App -->|uses| Requests
    App -->|uses| DotEnv
    
    Flask -->|uses| SocketIO
    SocketIO -->|uses| EngineIO
    
    App -->|uses| Uvicorn
    Uvicorn -->|uses| ASGI
```

---

## User Interface Architecture

### Web Dashboard Architecture

```mermaid
graph TB
    subgraph "Frontend (Browser)"
        HTML["HTML Template"]
        CSS["Styling<br/>Terminal Theme"]
        JS["JavaScript<br/>Interactivity"]
        SocketIO_Client["Socket.IO Client"]
    end
    
    subgraph "Backend (Flask)"
        Flask_App["Flask App"]
        API_Routes["API Routes<br/>/api/status<br/>/api/timeline<br/>/api/timeline/summary"]
        WebSocket_Manager["WebSocketManager"]
    end
    
    subgraph "Core Engine"
        Manager["HGENotifierManager"]
        Signal_History["Signal History"]
    end
    
    HTML -->|styles| CSS
    HTML -->|interacts| JS
    JS -->|opens connection| SocketIO_Client
    
    SocketIO_Client -->|real-time events| WebSocket_Manager
    
    Flask_App -->|serves| HTML
    Flask_App -->|routes| API_Routes
    Flask_App -->|manages| WebSocket_Manager
    
    API_Routes -->|queries| Signal_History
    API_Routes -->|queries| Manager
    
    WebSocket_Manager -->|receives events from| Manager
    WebSocket_Manager -->|broadcasts to| SocketIO_Client
    
    SocketIO_Client -->|updates| JS
    JS -->|renders| HTML
```

### Dashboard Views

```mermaid
graph TB
    Dashboard["Main Dashboard"]
    
    subgraph "Components"
        StatusCard["Status Card<br/>Latest HGE Signal"]
        LocationCard["Location Card<br/>Commander Location"]
        DistanceCard["Distance Card<br/>Distance in ly"]
        HistorySection["History Section<br/>Recent Signals"]
        NotificationsSection["Notifications<br/>Alert Log"]
    end
    
    subgraph "Timeline View"
        TimelineMain["Timeline Dashboard"]
        DistanceTrends["📈 Distance Trends"]
        HourlyDist["⏱️ Hourly Distribution"]
        SignalList["📋 Signal List"]
    end
    
    subgraph "Notifications View"
        NotificationsPage["Notifications Page"]
        NotificationCards["Notification Cards"]
        ClearButton["Clear History"]
    end
    
    Dashboard -->|contains| StatusCard
    Dashboard -->|contains| LocationCard
    Dashboard -->|contains| DistanceCard
    Dashboard -->|contains| HistorySection
    Dashboard -->|contains| NotificationsSection
    
    Dashboard -->|link to| TimelineMain
    Dashboard -->|link to| NotificationsPage
    
    TimelineMain -->|shows| DistanceTrends
    TimelineMain -->|shows| HourlyDist
    TimelineMain -->|shows| SignalList
    
    NotificationsPage -->|displays| NotificationCards
    NotificationsPage -->|action| ClearButton
```

---

## Real-Time Communication

### WebSocket Event Flow

```mermaid
graph LR
    Manager["HGENotifierManager"]
    
    subgraph "Events Emitted"
        E1["signal_detected"]
        E2["location_updated"]
        E3["distance_calculated"]
    end
    
    subgraph "WebSocketManager"
        WS["WebSocketManager"]
        Broadcast["broadcast()"]
    end
    
    subgraph "Browser"
        Socket["Socket.IO Client"]
        Listeners["Event Listeners"]
        Renderers["DOM Renderers"]
    end
    
    Manager -->|emit| E1
    Manager -->|emit| E2
    Manager -->|emit| E3
    
    E1 -->|send| WS
    E2 -->|send| WS
    E3 -->|send| WS
    
    WS -->|broadcast| Broadcast
    Broadcast -->|transmit| Socket
    
    Socket -->|trigger| Listeners
    Listeners -->|update| Renderers
    Renderers -->|display| UI["User Sees Updates"]
```

### Connection States

```mermaid
stateDiagram-v2
    [*] --> Connecting
    
    Connecting --> Connected: Success
    Connecting --> Disconnected: Timeout/Error
    
    Connected --> Processing: Receive Event
    Processing --> Connected: Event Complete
    
    Connected --> Reconnecting: Connection Lost
    Reconnecting --> Connected: Reconnect Success
    Reconnecting --> Disconnected: Max Retries
    
    Disconnected --> Connecting: User Refresh
    Disconnected --> [*]: User Exit
```

---

## Notification Pipeline

### Alert Processing Flow

```mermaid
graph TB
    Signal["New HGE Signal"]
    
    Signal -->|trigger| Check1{"Distance<br/>within<br/>threshold?"}
    Check1 -->|no| Ignore["Ignore Signal"]
    Check1 -->|yes| Check2
    
    Check2{"Signal Age<br/>within<br/>threshold?"}
    Check2 -->|no| Ignore
    Check2 -->|yes| Check3
    
    Check3{"Cooldown<br/>period<br/>elapsed?"}
    Check3 -->|no| Queue["Queue for Later"]
    Check3 -->|yes| Check4
    
    Check4{"Notifications<br/>enabled?"}
    Check4 -->|no| Log["Log Only"]
    Check4 -->|yes| Send
    
    Send["Send Discord Notification"]
    Queue -->|after delay| Check3
    
    Send --> Update["Update Last Alert Time"]
    Update --> Store["Store in History"]
    Log --> Store
    Store --> [*]
```

### Discord Webhook Integration

```mermaid
graph LR
    Manager["HGENotifierManager"]
    
    NotifMgr["NotificationManager"]
    
    Discord["DiscordNotifier"]
    
    Webhook["Discord Webhook<br/>HTTP POST"]
    
    Channel["Discord Channel"]
    
    Manager -->|trigger alert| NotifMgr
    NotifMgr -->|check conditions| NotifMgr
    NotifMgr -->|create payload| Discord
    Discord -->|HTTP POST| Webhook
    Webhook -->|deliver| Channel
    Channel -->|display| Message["🎯 HGE Alert<br/>Signal Details"]
```

---

## Deployment Model

### Single-User Desktop Deployment

```mermaid
graph TB
    subgraph "User's Windows Machine"
        EDS["Elite Dangerous<br/>Game"]
        Journal["Journal Files<br/>auto-generated"]
        
        App["HGE Notifier<br/>Python App"]
        
        CLI["CLI Terminal<br/>Window"]
        Web["Web Browser<br/>localhost:5000"]
    end
    
    subgraph "External Services"
        EDDN["EDDN Network"]
        EDSM["EDSM API"]
        Discord["Discord Server"]
    end
    
    EDS -->|writes| Journal
    Journal -->|read| App
    
    EDDN -->|stream| App
    EDSM -->|query| App
    
    App -->|display| CLI
    App -->|serve| Web
    
    App -->|notify| Discord
```

### Execution Flow

```mermaid
sequenceDiagram
    actor User
    participant App as HGE Notifier
    participant Terminal as CLI/Web
    participant Sources as External Sources
    
    User->>App: Start (--web or --cli)
    activate App
    
    App->>Sources: Connect EDDN
    App->>Sources: Connect Journal Watcher
    Note over App: Initialization complete
    
    loop Continuous Monitoring
        Sources->>App: New HGE Signal / Location Update
        App->>App: Process & Calculate
        App->>Terminal: Emit update
        Terminal->>User: Display
    end
    
    User->>App: Close Application
    deactivate App
    Note over App: Cleanup & exit
```

---

## Configuration

### Settings Hierarchy

```mermaid
graph TB
    Default["Default Settings<br/>settings.py"]
    
    Env["Environment Variables<br/>.env file"]
    
    CLI["CLI Arguments<br/>Command Line"]
    
    Active["Active Settings<br/>in Memory"]
    
    Default -->|override| Env
    Env -->|override| CLI
    
    Default -->|merged| Active
    Env -->|merged| Active
    CLI -->|merged| Active
    
    Active -->|used by| App["Application"]
```

### Key Configuration Areas

```mermaid
graph TB
    Settings["Settings"]
    
    subgraph "EDDN Configuration"
        EDDN_Mock["EDDN_MOCK_MODE"]
        EDDN_URL["EDDN_URL"]
    end
    
    subgraph "Journal Configuration"
        Journal_Path["JOURNAL_PATH"]
    end
    
    subgraph "Notification Configuration"
        Notif_Enabled["NOTIFICATIONS_ENABLED"]
        Discord_URL["DISCORD_WEBHOOK_URL"]
        Alert_Dist["ALERT_MAX_DISTANCE"]
        Alert_Age["ALERT_MAX_AGE"]
        Cooldown["NOTIFICATION_COOLDOWN_SECONDS"]
    end
    
    subgraph "Web Configuration"
        Web_Debug["WEB_DEBUG"]
        Web_Port["WEB_PORT"]
    end
    
    subgraph "Logging"
        Log_Level["LOG_LEVEL"]
        Log_File["LOG_FILE"]
    end
    
    Settings -->|contains| EDDN_Mock
    Settings -->|contains| Journal_Path
    Settings -->|contains| Notif_Enabled
    Settings -->|contains| Web_Debug
    Settings -->|contains| Log_Level
```

---

## Testing Architecture

### Test Organization

```mermaid
graph TB
    Tests["tests/"]
    
    subgraph "Unit Tests"
        ConfigTest["config/test_config.py"]
        EDDNTest["eddn/test_eddn.py"]
        JournalTest["journal/test_journal.py"]
        DistanceTest["distance/test_distance.py"]
        NotifTest["notifications/test_notifications_*.py"]
    end
    
    subgraph "Integration Tests"
        CoreTest["core/test_core.py"]
        CoreManager["core/test_core_manager.py"]
        WebTest["web/test_web*.py"]
        E2ETest["core/test_main.py"]
    end
    
    subgraph "Advanced Tests"
        EdgeCases["core/test_core_edge_cases.py"]
        Formatting["core/test_core_formatting.py"]
        Enrichment["core/test_core_enrichment.py"]
        Websocket["core/test_core_websocket.py"]
    end
    
    Tests --> Unit["Unit Tests<br/>100% coverage"]
    Tests --> Integration["Integration Tests<br/>~80% coverage"]
    Tests --> Advanced["Advanced Tests<br/>Edge cases"]
    
    Unit -->|verify| ConfigTest
    Unit -->|verify| EDDNTest
    Integration -->|verify| CoreTest
    Advanced -->|verify| EdgeCases
```

### Coverage Report

```mermaid
graph LR
    Modules["All Modules"]
    
    subgraph "100% Coverage"
        Perfect["core.py"]
        Models["notifications/models.py"]
        InApp["notifications/in_app.py"]
        Coords["distance/coordinates.py"]
    end
    
    subgraph "90%+ Coverage"
        HighCov["journal/__init__.py<br/>eddn/__init__.py<br/>config/settings.py"]
    end
    
    subgraph "80%+ Coverage"
        MidCov["cli.py<br/>web/__init__.py"]
    end
    
    subgraph "Below 80%"
        LowCov["notifications/discord.py<br/>(retry paths)"]
    end
    
    Modules -->|82%| Overall["Overall<br/>Coverage"]
    Overall -->|743 tests| Summary["743 Passing Tests"]
    
    Perfect -.->|best| Overall
    HighCov -.->|good| Overall
    MidCov -.->|solid| Overall
```

---

## Key Design Patterns

### Observer Pattern (Event-Driven)

```mermaid
graph LR
    Subject["HGENotifierManager"]
    
    Observer1["WebSocketManager"]
    Observer2["NotificationManager"]
    Observer3["Signal History"]
    
    Subject -->|notify| Observer1
    Subject -->|notify| Observer2
    Subject -->|notify| Observer3
    
    Observer1 -->|broadcast| Users["Web Users"]
    Observer2 -->|send| Discord["Discord Channel"]
    Observer3 -->|store| Store["In-Memory Deque"]
```

### Factory Pattern (Configuration)

```mermaid
graph TB
    Factory["ConfigFactory"]
    
    Env["Env File"]
    Default["Defaults"]
    CLI["CLI Args"]
    
    Factory -->|reads| Env
    Factory -->|reads| Default
    Factory -->|reads| CLI
    
    Factory -->|creates| Settings["Settings Object"]
    Settings -->|used by| App["Application"]
```

### Strategy Pattern (Notifications)

```mermaid
graph TB
    Manager["NotificationManager"]
    
    Strategy["Notification Strategy"]
    
    Discord["DiscordNotifier"]
    InApp["InAppNotifier"]
    
    Manager -->|uses| Strategy
    Strategy -->|implements| Discord
    Strategy -->|implements| InApp
```

---

## Performance Considerations

### Memory Management

```mermaid
graph TB
    App["Application"]
    
    subgraph "In-Memory Storage"
        History["Signal History<br/>maxlen=100"]
        SystemCache["System Info Cache<br/>TTL: 24 hours"]
        CoordCache["Coordinate Cache<br/>Persistent File"]
    end
    
    subgraph "Optimizations"
        Deque["Use deque for<br/>bounded history"]
        LRU["LRU caching for<br/>system info"]
        File["File-based caching<br/>for coordinates"]
    end
    
    App -->|stores| History
    App -->|stores| SystemCache
    App -->|stores| CoordCache
    
    History -->|implements| Deque
    SystemCache -->|implements| LRU
    CoordCache -->|implements| File
```

### Network Optimization

```mermaid
graph TB
    App["Application"]
    
    EDDN["EDDN Stream"]
    EDSM["EDSM API"]
    
    App -->|persistent connection| EDDN
    App -->|caches coordinates| CoordDB["Coordinate Database"]
    CoordDB -->|reduces API calls| EDSM
    
    Note["Caching reduces EDSM<br/>API calls by ~95%"]
```

---

## Error Handling & Recovery

### Error Handling Flow

```mermaid
graph TB
    Operation["Operation"]
    
    Try["Try Operation"]
    
    Success["Success"]
    
    Catch["Catch Exception"]
    
    Retry{"Should Retry?"}
    
    Log["Log Error"]
    
    Notify["Notify User"]
    
    Recover["Recover State"]
    
    Try -->|success| Success
    Try -->|exception| Catch
    
    Catch -->|evaluate| Retry
    Retry -->|yes| Try
    Retry -->|no| Log
    
    Log --> Notify
    Notify --> Recover
    Recover --> Continue["Continue Operation"]
```

### Connection Resilience

```mermaid
graph TB
    Connection["Connection to EDDN"]
    
    Connected["Connected"]
    Disconnected["Disconnected"]
    
    Connected -->|error| Disconnected
    Disconnected -->|retry| Try["Attempt Reconnect"]
    Try -->|success| Connected
    Try -->|failure| Backoff["Exponential Backoff"]
    Backoff -->|ready| Try
    
    Note1["Graceful degradation<br/>Works offline with mock data"]
```

---

## Security Considerations

### Security Architecture

```mermaid
graph TB
    subgraph "Data Protection"
        LocalOnly["Journal files<br/>stay local"]
        NoAuth["No authentication<br/>required"]
        NoPrivate["No personal data<br/>transmitted"]
    end
    
    subgraph "Network Safety"
        Discord["Discord webhook<br/>secure endpoint"]
        EDSM["EDSM API<br/>public read-only"]
        EDDN["EDDN stream<br/>anonymous data"]
    end
    
    subgraph "Code Quality"
        TypeHints["Type hints<br/>for safety"]
        Validation["Input validation"]
        ErrorHandle["Error handling"]
    end
    
    LocalOnly -->|ensures| Privacy["User Privacy"]
    Discord -->|ensures| Security["Network Security"]
    TypeHints -->|ensures| Quality["Code Quality"]
```

---

## Future Architecture Enhancements

### Proposed Phase 5 Features

```mermaid
graph TB
    Current["Current v0.1.0"]
    
    Phase5A["Phase 5A: Database"]
    Phase5B["Phase 5B: Advanced UI"]
    Phase5C["Phase 5C: Fleet Tracking"]
    
    subgraph "Database Features"
        SQLite["SQLite Backend"]
        Analytics["Historical Analytics"]
        Trending["Trend Analysis"]
    end
    
    subgraph "UI Features"
        Mapping["3D System Mapping"]
        Filtering["Advanced Filtering"]
        Export["Data Export"]
    end
    
    subgraph "Multiplayer Features"
        FleetTracking["Fleet Member Tracking"]
        MultiNotif["Multi-User Notifications"]
        SharedData["Shared Signal Data"]
    end
    
    Current -->|evolve to| Phase5A
    Current -->|evolve to| Phase5B
    Current -->|evolve to| Phase5C
    
    Phase5A -->|enables| SQLite
    Phase5A -->|enables| Analytics
    
    Phase5B -->|enables| Mapping
    Phase5B -->|enables| Filtering
    
    Phase5C -->|enables| FleetTracking
    Phase5C -->|enables| MultiNotif
```

---

## Glossary

| Term | Definition |
|------|-----------|
| **EDDN** | Elite Dangerous Data Network - crowdsourced real-time game data |
| **HGE** | High Grade Emission - specific type of USS signal in Elite Dangerous |
| **USS** | Unidentified Signal Source - points of interest in space |
| **EDSM** | Elite Dangerous Star Map API - provides system coordinates |
| **WebSocket** | Bidirectional real-time communication protocol |
| **Webhook** | HTTP callback mechanism for sending notifications |
| **ZMQ** | Zero Message Queue - efficient messaging framework |
| **Deque** | Double-ended queue data structure (used for history) |
| **LRU Cache** | Least Recently Used cache for memory optimization |

---

## Related Documentation

- [README.md](README.md) - Quick start and usage
- [DEVELOPMENT_NOTES.md](DEVELOPMENT_NOTES.md) - Development history and progress
- [ROADMAP.md](ROADMAP.md) - Future development plans
- [REAL_EDDN_USAGE.md](REAL_EDDN_USAGE.md) - Advanced usage with real EDDN

---

**Last Updated:** October 26, 2025  
**Status:** Production Ready v0.1.0  
**Coverage:** 82% | Tests: 743/743 passing ✅
