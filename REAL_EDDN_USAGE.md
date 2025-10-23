# Using Real EDDN Data

By default, HGE Notifier uses **mock data** for testing. To connect to real Elite Dangerous EDDN for live HGE signals, use the `--real-eddn` flag.

## Command Line Usage

### Web Server with Mock Data (Default)
```powershell
python -m src --web
```

### Web Server with Real EDDN Data
```powershell
python -m src --web --real-eddn
```

### CLI with Mock Data (Default)
```powershell
python -m src
```

### CLI with Real EDDN Data
```powershell
python -m src --real-eddn
```

### CLI (Once) with Real EDDN Data
```powershell
python -m src --once --real-eddn
```

## VS Code Debug Configurations

Open the **Run and Debug** view (Ctrl+Shift+D) and select one of these configurations:

### Mock Mode (Default - Great for Testing)
- `HGE Notifier - Web Server` → Uses mock HGE signals
- `HGE Notifier - CLI` → Uses mock HGE signals
- `HGE Notifier - CLI (Once)` → One-shot with mock data

### Real EDDN Mode (Live Data)
- `HGE Notifier - Web Server (Real EDDN)` → Live EDDN monitoring
- `HGE Notifier - CLI (Real EDDN)` → CLI with real signals
- `HGE Notifier - CLI (Once, Real EDDN)` → One-shot with real data

## Environment Variable

You can also set this via environment variable (in PowerShell):

### With Real EDDN
```powershell
$env:EDDN_MOCK_MODE = "false"
python -m src --web
```

### Back to Mock Mode
```powershell
$env:EDDN_MOCK_MODE = "true"
python -m src --web
```

Or create a `.env` file in the project root:
```
EDDN_MOCK_MODE=false
```

## What's Different?

| Aspect | Mock Mode | Real EDDN Mode |
|--------|-----------|----------------|
| **HGE Signals** | Predefined test signals from Shinrarta Dezhra | Real signals from Elite Dangerous players worldwide |
| **Signal Updates** | Static (doesn't change) | Dynamic (updates every few seconds) |
| **Testing** | ✅ Safe for development | ⚠️ Uses live network resources |
| **Default** | ✅ Yes | ❌ No |

## Notes

- Real EDDN mode requires an active internet connection to ZMQ EDDN broker
- If EDDN connection fails, the app will automatically fall back to mock mode
- Your journal location is independent of mock/real mode (always reads your actual Elite Dangerous location)
- Coordinates for systems are cached locally after first EDSM lookup
