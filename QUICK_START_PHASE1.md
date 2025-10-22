# Quick Start: Phase 1 Real Data

> **TL;DR**: 5-minute setup for real HGE monitoring

## ⚡ Quick Setup

### 1. Configure (30 seconds)

Edit `.env`:
```env
EDDN_MOCK_MODE=false
JOURNAL_PATH=C:\Users\YourUsername\Saved Games\Frontier Developments\Elite Dangerous
```

Replace `YourUsername` with your Windows username.

### 2. Run (10 seconds)

```bash
python -m src --once
```

### 3. Check Output

You should see:
- ✅ Latest HGE system
- ✅ Your current location  
- ✅ Distance in light years
- ✅ Coordinates for both

**That's it!** Phase 1 is working.

---

## 🎮 While Playing

### Continuous Monitoring (CLI)
```bash
python -m src
```
Auto-updates every 10 seconds as you play.

### Web Dashboard
```bash
python -m src --web
# Open http://127.0.0.1:5000
```
Real-time updates in browser.

---

## 🔧 Configuration Details

| Setting | Value | Notes |
|---------|-------|-------|
| `EDDN_MOCK_MODE` | `false` | Enable real data |
| `JOURNAL_PATH` | Your ED directory | Required for location |
| `REFRESH_INTERVAL` | `10` | Update frequency (seconds) |
| `LOG_LEVEL` | `INFO` | Change to `DEBUG` for details |

---

## ✅ Verification

After first run, check for:
- [ ] `.env` file configured
- [ ] `data/coordinates.db` created
- [ ] CLI shows real HGE system
- [ ] Distance calculation working
- [ ] Web dashboard accessible

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Journal path not found" | Check `.env` path exists and is correct |
| No HGE data showing | HGE signals are rare (1-5 per day) |
| Connection errors | Check internet, firewall port 9500 |
| Coordinates missing | First lookups take 1-2s, then cached |

---

## 📊 What's Running

- **EDDN Monitor**: Real-time HGE signal stream (background thread)
- **Journal Watcher**: Monitors your Elite Dangerous location (background thread)
- **Coordinate Cache**: Queries EDSM API, caches locally (SQLite)

All three work together to show you the nearest HGE.

---

## 📚 Need More Details?

- **Setup Guide**: See `PHASE1_GUIDE.md`
- **Full Architecture**: See `README.md`
- **Project Status**: See `PHASE1_COMPLETE.md`
- **Getting Started**: See `GETTING_STARTED.md`

---

## 🎯 Next: Phase 2

After you're comfortable with Phase 1 real data, Phase 2 will add:
- Discord notifications
- Email alerts
- Custom filters
- Advanced routing

---

**Ready?** → `python -m src --web`
