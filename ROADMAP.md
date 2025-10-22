# Development Roadmap - HGE Notifier

## MVP Status ✅ COMPLETE

### Core Features Implemented
- [x] Modular architecture (EDDN, Journal, Distance modules)
- [x] CLI interface with real-time status
- [x] Web interface with Flask
- [x] Configuration management
- [x] Mock data for testing
- [x] 17 unit tests (all passing)
- [x] Distance calculation engine
- [x] Status reporting and formatting
- [x] Error handling with graceful fallbacks
- [x] Comprehensive documentation

---

## Phase 1: Real Data Integration (Next Priority)

### 1.1 EDDN Real Connection
**Status**: Not Started  
**Effort**: Medium  
**Dependencies**: PyZMQ installation

```python
# TODO: Implement in src/eddn/__init__.py
# Connect to EDDN ZMQ endpoint: tcp://eddn.edcd.io:9500
# Subscribe to HighGradeEmission message type
# Parse incoming JSON messages
# Extract: timestamp, star_system, star_pos (x, y, z)
```

**Tasks**:
- [ ] Add ZMQ connection logic
- [ ] Implement message filtering
- [ ] Add reconnection/error handling
- [ ] Test with real EDDN stream
- [ ] Add configuration for EDDN endpoints

### 1.2 Real Journal Parsing
**Status**: Not Started  
**Effort**: Medium  
**Dependencies**: Python file watching

```python
# TODO: Implement in src/journal/__init__.py
# Use pathlib to find latest journal file
# Implement file tail watching
# Parse JSON log entries
# Track Location and FSDJump events
```

**Tasks**:
- [ ] Implement journal file discovery
- [ ] Add file watching with watchdog
- [ ] Extract coordinate data from events
- [ ] Handle journal file rotation
- [ ] Cache last known location

### 1.3 System Coordinate Database
**Status**: Not Started  
**Effort**: High  
**Dependencies**: Requests, EDSM API

```python
# TODO: Create src/coordinates/ module
# Integrate EDSM API for system coordinates
# Cache results locally
# Handle API rate limiting
```

**Tasks**:
- [ ] Design coordinate cache schema
- [ ] Implement EDSM API client
- [ ] Add local SQLite cache
- [ ] Handle missing coordinates gracefully
- [ ] Add coordinate update scheduling

---

## Phase 2: Notifications & Alerts

### 2.1 Discord Integration
**Status**: Not Started  
**Effort**: Low

```python
# TODO: Create src/notifications/discord.py
# Send HGE alerts to Discord webhook
# Format messages with embeds
# Add filtering options
```

**Tasks**:
- [ ] Design notification message format
- [ ] Implement Discord webhook client
- [ ] Add configuration for webhook URLs
- [ ] Test notification delivery
- [ ] Add notification throttling

### 2.2 Email Notifications
**Status**: Not Started  
**Effort**: Low

**Tasks**:
- [ ] Implement SMTP client
- [ ] Design email template
- [ ] Add email configuration
- [ ] Test email delivery

### 2.3 In-App Alerts
**Status**: Not Started  
**Effort**: Low

**Tasks**:
- [ ] Add sound alerts to CLI
- [ ] Add visual indicators to web UI
- [ ] Implement alert debouncing
- [ ] Add severity levels

---

## Phase 3: Enhanced Web UI

### 3.1 Advanced Dashboard
**Status**: Not Started  
**Effort**: Medium

**Tasks**:
- [ ] Add system detail view
- [ ] Implement search/filter
- [ ] Add signal history timeline
- [ ] Display HGE frequency stats
- [ ] Add route planning visualization

### 3.2 WebSocket Real-Time Updates
**Status**: Not Started  
**Effort**: Medium

**Tasks**:
- [ ] Implement WebSocket server
- [ ] Push updates to clients in real-time
- [ ] Add server-sent events fallback
- [ ] Implement client reconnection

### 3.3 Mobile Responsive Design
**Status**: Not Started  
**Effort**: Low

**Tasks**:
- [ ] Test current UI on mobile
- [ ] Implement responsive layout
- [ ] Add mobile-optimized controls

---

## Phase 4: Advanced Features

### 4.1 Route Planning
**Status**: Not Started  
**Effort**: High

**Tasks**:
- [ ] Integrate with EDSM for route calculation
- [ ] Display optimal routes to HGE
- [ ] Add waypoint support
- [ ] Estimate jump count/time

### 4.2 Material Filtering
**Status**: Not Started  
**Effort**: Medium

**Tasks**:
- [ ] Add material requirement database
- [ ] Filter HGE by materials
- [ ] Create watchlist for specific materials
- [ ] Notify on matching materials

### 4.3 Multi-User Support
**Status**: Not Started  
**Effort**: High

**Tasks**:
- [ ] Design fleet tracking system
- [ ] Add user authentication
- [ ] Implement shared HGE database
- [ ] Add team coordination features

### 4.4 Historical Analytics
**Status**: Not Started  
**Effort**: Medium

**Tasks**:
- [ ] Store signal history
- [ ] Implement data analysis
- [ ] Create statistical reports
- [ ] Add visualization charts

---

## Phase 5: Deployment & Distribution

### 5.1 PyInstaller Packaging
**Status**: Not Started  
**Effort**: Low

**Tasks**:
- [ ] Configure PyInstaller
- [ ] Create standalone executable
- [ ] Test on clean Windows system
- [ ] Add Windows shortcut

### 5.2 Windows Installer
**Status**: Not Started  
**Effort**: Medium

**Tasks**:
- [ ] Create NSIS installer
- [ ] Add start menu shortcuts
- [ ] Implement auto-updater
- [ ] Create uninstaller

### 5.3 Auto-Update System
**Status**: Not Started  
**Effort**: Medium

**Tasks**:
- [ ] Implement version checking
- [ ] Create auto-update mechanism
- [ ] Add rollback capability
- [ ] Test update process

---

## Technical Debt & Improvements

### Code Quality
- [ ] Increase test coverage to 80%+
- [ ] Add integration tests
- [ ] Implement end-to-end tests
- [ ] Add performance benchmarks
- [ ] Refactor large functions

### Documentation
- [ ] Add API documentation
- [ ] Create architecture diagrams
- [ ] Add developer guide
- [ ] Create troubleshooting guide
- [ ] Add video tutorials

### Performance
- [ ] Optimize distance calculations
- [ ] Implement caching strategies
- [ ] Profile memory usage
- [ ] Optimize database queries
- [ ] Add performance monitoring

### Security
- [ ] Add input validation
- [ ] Implement rate limiting
- [ ] Add request signing
- [ ] Secure sensitive data
- [ ] Regular dependency updates

---

## Dependencies to Add (By Phase)

### Phase 1
- `pyzmq>=25.0.0` - EDDN ZMQ connection
- `watchdog>=3.0.0` - Journal file monitoring

### Phase 2
- `discord.py>=2.0.0` - Discord integration
- `discord-webhook>=1.3.0` - Discord webhooks

### Phase 3
- `websocket-client>=1.6.0` - WebSocket support

### Phase 4
- `numpy>=1.24.0` - Advanced calculations
- `pandas>=2.0.0` - Data analysis

### Phase 5
- `auto-py-to-exe>=2.4.0` - PyInstaller GUI

---

## Success Metrics

### MVP Success Criteria ✅
- [x] CLI interface displays correct information
- [x] Web interface is functional
- [x] All unit tests pass
- [x] No critical bugs
- [x] Documentation is complete
- [x] Project is deployable

### Phase 1 Success Criteria
- [ ] Real EDDN data is being received
- [ ] Commander location updates in real-time
- [ ] Distance calculations are accurate
- [ ] No data loss on reconnection
- [ ] 80%+ test coverage

### Phase 2 Success Criteria
- [ ] Notifications are delivered reliably
- [ ] Users can customize alert settings
- [ ] No notification spam
- [ ] Multiple notification channels work

---

## Known Limitations & Notes

### Current MVP Limitations
1. **Mock Data**: Uses hardcoded test data
2. **No Real Integration**: EDDN and Journal connections not implemented
3. **Limited UI**: Basic dashboard without advanced features
4. **No Persistence**: Data not stored between sessions
5. **Single User**: No multi-user support

### Design Decisions
1. **Mock-First Approach**: Easier testing and development
2. **Modular Architecture**: Enables incremental feature addition
3. **Flask/HTML UI**: Lightweight, no complex dependencies
4. **Type Hints**: Improves code maintainability
5. **Pytest**: Industry standard testing framework

---

## Timeline Estimates

| Phase | Status | Estimated Duration |
|-------|--------|-------------------|
| MVP | ✅ Complete | 1 day |
| Phase 1 (Real Data) | 📋 Ready | 3-5 days |
| Phase 2 (Notifications) | 📋 Ready | 2-3 days |
| Phase 3 (Web UI) | 📋 Ready | 3-5 days |
| Phase 4 (Advanced) | 📋 Ready | 5-10 days |
| Phase 5 (Distribution) | 📋 Ready | 2-3 days |
| **Total** | | **~20-30 days** |

---

## Resources & References

- [Elite Dangerous Data Network](https://eddn.edcd.io/)
- [Elite Dangerous Star Map API](https://www.edsm.net/api-v1)
- [PyZMQ Documentation](http://pyzmq.readthedocs.io/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Python Packaging Guide](https://packaging.python.org/)

---

## Contact & Support

For questions or suggestions about the roadmap:
- Create an issue in the repository
- Discuss in Elite Dangerous community channels
- Refer to SRS document in `.github/copilot-instructions.md`
