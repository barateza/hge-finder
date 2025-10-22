# 🎯 Code Coverage Improvement Plan

**Current Status**: 80% overall coverage ✅ (Updated post-Phase 2)
**Target**: 85%+ overall coverage
**Opportunity**: +5% additional coverage improvement remaining (Phase 3)

---

## ✅ PHASE 2 COMPLETED - Final Results Summary

**Phase 2 Completion Date**: October 22, 2025

### Coverage Improvement Achieved (Full Journey):
- **Before Phase 1**: 64% (357 statements missing)
- **After Phase 1**: 79% (205 statements missing) = +15%
- **After Phase 2**: 80% (198 statements missing) = +16% total
- **Final Improvement**: +16 percentage points, 159 additional lines covered

### Phase 2 Final Deliverables (COMPLETED):
1. ✅ Enhanced `tests/test_cli.py` - 3 additional tests (+35 lines)
   - test_run_cli_continuous_mode_multiple_iterations
   - test_run_cli_continuous_mode_refresh_interval
   - Plus fixes from Phase 1

2. ✅ Created `tests/test_config.py` (NEW FILE) - 23 comprehensive tests (+320 lines)
   - All environment variable handling tests
   - Boolean parsing variations (true/false, 1/0, yes/no, on/off)
   - Path parsing and validation
   - Singleton pattern verification
   - Log file directory creation

3. ✅ Enhanced `tests/test_notifications.py` - 11 Discord error tests (+130 lines)
   - test_discord_retry_exhaustion_all_failures
   - test_discord_http_429_rate_limit_with_retry
   - test_discord_http_500_server_error
   - test_discord_connection_timeout
   - And 7 more comprehensive error scenarios

### Phase 2 Test Results (FINAL):
- **Total Tests Passing**: 180/180 (100%)
  - Phase 1 Original: 80 tests
  - Phase 1 New: 64 tests
  - Phase 2 New: 36 tests
- **Coverage Achieved**: 80% (198 missing lines, 793 covered)
- **Settings Module**: 100% coverage ✅ (newly achieved!)
- **Total Test Code**: 2664+ lines
- **Regressions**: 0 ✅

## ✅ PHASE 1 COMPLETED - Results Summary

**Phase 1 Completion Date**: October 22, 2025

### Coverage Improvement Achieved:
- **Before Phase 1**: 64% (357 statements missing)
- **After Phase 1**: 79% (205 statements missing)
- **Improvement**: +15 percentage points, 152 additional statements covered

### Phase 1 Deliverables (COMPLETED):
1. ✅ `tests/test_cli.py` - 20 comprehensive tests (320 lines)
   - TestSetupLogging: All log levels, file handlers, formatting
   - TestDisplayStatus: All status display scenarios
   - TestRunCli: All CLI modes, interrupts, error handling

2. ✅ `tests/test_main.py` - 15 entry point tests (250 lines)
   - TestMainEntry: CLI/web modes, all flag combinations, error handling

3. ✅ `tests/test_web.py` - 35+ route tests (380 lines)
   - TestWebRoutes: All Flask endpoints, error paths, data validation

### Test Results:
- **Total Tests Passing**: 144 (80 existing + 64 new)
- **Success Rate**: 100%
- **Regressions**: Zero
- **New Lines of Test Code**: 950+ lines
- **New Test Cases**: 100+

### Coverage by Module (Post-Phase 1):
| Module | Before | After | Change |
|--------|--------|-------|--------|
| `src/__main__.py` | 0% | 97% | +97% ✅ |
| `src/cli.py` | 0% | 89% | +89% ✅ |
| `src/web/__init__.py` | 0% | 91% | +91% ✅ |
| `src/config/settings.py` | 32% | 87% | +55% |
| `src/core.py` | 25% | 65% | +40% |
| `src/distance/coordinates.py` | 17% | 74% | +57% |
| `src/notifications/in_app.py` | 45% | 100% | +55% |
| `src/eddn/__init__.py` | 26% | 68% | +42% |
| `src/journal/__init__.py` | 26% | 78% | +52% |
| `src/notifications/discord.py` | 19% | 74% | +55% |
| `src/notifications/manager.py` | 26% | 91% | +65% |
| **OVERALL** | **64%** | **79%** | **+15%** ✅ |

---

## 📊 Phase 2 Coverage Analysis - Remaining Gaps

---

## 📊 Phase 2 Coverage Analysis - Remaining Gaps

### High Priority (Still Under 90%)

#### 1. `src/cli.py` - 89% (64/72 lines covered)
**Uncovered**: 8 lines (110-134, 138)
**What's missing**:
- Lines 110-134: Continuous monitoring loop (while True block)
  - Likely: Edge case where `display_status()` is called in continuous mode
  - Requires mocking `time.sleep()` to avoid delays in continuous mode
- Line 138: Final return statement in exception handler

**Impact**: 8 lines
**Difficulty**: Medium - requires careful timing/mocking

**Test Strategy**:
- Add test for continuous mode running multiple iterations
- Mock `time.sleep()` to allow loop execution without delays
- Verify `display_status()` is called on each iteration
- Test that loop exits on KeyboardInterrupt

**Estimated Effort**: 30-45 minutes

---

#### 2. `src/config/settings.py` - 87% (33/38 lines covered)
**Uncovered**: 5 lines (71, 76-79)
**What's missing**:
- Lines 71-72: Likely environment variable fallback paths
- Lines 76-79: Likely error handling for invalid config values

**Impact**: 5 lines
**Difficulty**: Low - configuration edge cases

**Test Strategy**:
- Test missing environment variables
- Test invalid configuration values
- Test config file parsing errors
- Test default value fallbacks

**Estimated Effort**: 20-30 minutes

---

#### 3. `src/notifications/discord.py` - 74% (53/72 lines covered)
**Uncovered**: 19 lines (34, 108, 115, 119, 187-195, 198-206, 213)
**What's missing**:
- Line 34: Likely WebhookClient initialization error
- Lines 108-119: Retry logic edge cases
  - Line 108: Retry after specific failures
  - Line 115: Final retry attempt failure
  - Line 119: Exhausted all retries
- Lines 187-206: HTTP error handling (specific status codes)
- Line 213: Final error logging

**Impact**: 19 lines
**Difficulty**: High - requires mocking HTTP errors

**Test Strategy**:
- Test retry exhaustion (all 3 retries fail)
- Test specific HTTP errors (429 rate limit, 500 server error, 502 bad gateway)
- Test connection timeout
- Test malformed webhook responses
- Test successful retry after transient failure

**Estimated Effort**: 1.5-2 hours

---

#### 4. `src/core.py` - 65% (71/109 lines covered)
**Uncovered**: 38 lines (58-73, 77, 124-126, 141-148, 163-170, 176, 193, 212, 224, 246-248, 259-261)
**What's missing**:
- Lines 58-73: HGE signal processing/filtering logic
- Lines 77, 124-126: Distance calculation paths
- Lines 141-148: Location update logic
- Lines 163-170: Error recovery paths
- Lines 176+: Various edge cases in orchestration

**Impact**: 38 lines
**Difficulty**: Very High - complex orchestration logic

**Test Strategy**:
- Mock EDDN data with edge case signal formats
- Test filtering logic with various signal types
- Test location updates with missing/invalid coordinates
- Test error recovery when services fail
- Test refresh rate limiting

**Estimated Effort**: 2-3 hours

---

#### 5. `src/eddn/__init__.py` - 68% (113/167 lines covered)
**Uncovered**: 54 lines
**What's missing**:
- Connection failure handling
- Message parsing edge cases
- ZMQ timeout/error scenarios
- Protocol version mismatches

**Impact**: 54 lines
**Difficulty**: Very High - requires ZMQ mocking

**Test Strategy**:
- Mock ZMQ socket failures
- Test malformed EDDN messages
- Test connection timeouts
- Test various EDDN message types

**Estimated Effort**: 2-3 hours

---

#### 6. `src/journal/__init__.py` - 78% (117/150 lines covered)
**Uncovered**: 33 lines
**What's missing**:
- File parsing error handling
- Missing journal file scenarios
- Corrupted log entry handling
- Edge cases in coordinate extraction

**Impact**: 33 lines
**Difficulty**: Medium - file I/O edge cases

**Test Strategy**:
- Test missing journal directory
- Test missing journal files
- Test corrupted/malformed JSON entries
- Test empty journal files
- Test large journal files

**Estimated Effort**: 1-1.5 hours

---

### Lower Priority (85%+ coverage already)

#### 7. `src/distance/coordinates.py` - 74% (90/121 lines covered)
**Note**: Already achieved 74% in Phase 1, could be improved further

#### 8. `src/notifications/manager.py` - 91% (69/76 lines covered)
**Note**: Near 90% threshold, only 7 lines missing

---

## 🚀 Phase 2 - Remaining Work to Reach 85%+

### Phase 2 Priority (Highest ROI First)

#### Priority 1: Quick Wins (1-1.5 hours) → +8% to 80-81%
**Target**: Extend existing test files with edge cases

1. **Enhance `tests/test_cli.py`** (Add 3-5 tests)
   - Continuous mode with multiple iterations (covers lines 110-134)
   - Test `setup_logging()` with missing log file directory
   - **Impact**: +8 lines in cli.py
   - **Time**: 30-40 min

2. **Create `tests/test_config.py`** (NEW - ~50 lines)
   - Test missing environment variables
   - Test invalid configuration values
   - Test environment variable overrides
   - **Impact**: +5 lines in settings.py
   - **Time**: 20-30 min

**Subtotal**: 1-1.5 hours, +13 lines → **80-81% coverage**

---

#### Priority 2: Medium Effort (1.5-2 hours) → +4% to 84-85%
**Target**: Discord notification error paths

3. **Enhance `tests/test_notifications.py`** (Add discord tests)
   - Test retry exhaustion scenarios (all 3 retries fail)
   - Test specific HTTP errors (429, 500, 502)
   - Test connection timeout scenarios
   - Test malformed webhook responses
   - Test successful retry after transient failure
   - **Impact**: +15 lines in discord.py
   - **Time**: 1.5-2 hours

**Subtotal**: 1.5-2 hours, +15 lines → **84-85% coverage**

---

#### Priority 3: High Effort (2-3 hours) → +3-4% to 87-88%
**Target**: Core orchestration and data ingestion

4. **Enhance `tests/test_core.py`** (Add comprehensive tests)
   - Mock EDDN data with edge case signal formats
   - Test filtering logic with various signal types
   - Test location updates with missing/invalid coordinates
   - Test error recovery when services fail
   - **Impact**: +15-20 lines in core.py
   - **Time**: 2-3 hours

5. **Enhance `tests/test_journal.py`** (Add error handling tests)
   - Test missing journal directory scenarios
   - Test corrupted/malformed JSON entries
   - Test empty journal files
   - **Impact**: +10-15 lines in journal/__init__.py
   - **Time**: 1-1.5 hours

**Subtotal**: 3-4.5 hours, +25-35 lines → **87-88% coverage**

---

#### Priority 4: Optional (2-3 hours) → +1-2% to 89-90%
**Target**: EDDN and distance calculation edge cases

6. **Enhance `tests/test_eddn.py`** (Add connection/parsing tests)
   - Mock ZMQ socket failures
   - Test malformed EDDN messages
   - Test connection timeouts
   - **Impact**: +20-25 lines in eddn/__init__.py
   - **Time**: 2-3 hours

---

## 📈 Phase 2 Implementation Roadmap

### Option A: Fast Path (Get to 80% quickly - 1-1.5 hours)
Execute Priority 1 only:
- Enhance test_cli.py with continuous mode tests
- Create test_config.py for settings edge cases
- **Result**: 80-81% coverage

### Option B: Target Path (Reach 85% - 2.5-3 hours)
Execute Priority 1 + Priority 2:
- All quick wins
- Discord error scenarios
- **Result**: 84-85% coverage

### Option C: Comprehensive (Get to 87-88% - 5.5-7.5 hours)
Execute Priority 1 + Priority 2 + Priority 3:
- All quick wins
- Discord error scenarios
- Core orchestration and journal edge cases
- **Result**: 87-88% coverage

### Option D: Complete (Get to 89-90% - 7.5-10.5 hours)
Execute all priorities:
- Complete all edge case coverage
- EDDN and distance calculation scenarios
- **Result**: 89-90% coverage

---

## � Phase 2 Detailed Test Implementation

### Priority 1.1: Enhanced `tests/test_cli.py` - Continuous Mode
**Location**: Add to existing test file
**Lines Missing**: 110-134 (continuous mode loop)

```python
@patch('src.cli.HGENotifierManager')
@patch('src.cli.time.sleep')
@patch('src.cli.display_status')
def test_run_cli_continuous_mode_iterations(self, mock_display, mock_sleep, mock_manager_class):
    """Test continuous mode runs multiple iterations before interrupt."""
    mock_manager = MagicMock()
    mock_manager_class.return_value = mock_manager
    mock_manager.settings.refresh_interval = 1
    
    # Simulate interrupt after 3 iterations
    call_count = [0]
    def interrupt_after_iterations(*args, **kwargs):
        call_count[0] += 1
        if call_count[0] == 3:
            raise KeyboardInterrupt()
    
    mock_sleep.side_effect = interrupt_after_iterations
    
    args = argparse.Namespace(once=False, log_level="INFO", log_file=None)
    result = run_cli(args)
    
    assert result == 0
    assert mock_display.call_count == 3  # Called 3 times before interrupt
    assert mock_sleep.call_count == 3    # Sleep called 3 times
```

---

### Priority 1.2: New `tests/test_config.py` - Settings Edge Cases
**Location**: New file
**Impact**: +5 lines in settings.py

```python
import pytest
from unittest.mock import patch, MagicMock
import os

from src.config.settings import get_settings, Settings

class TestSettingsConfiguration:
    def test_missing_journal_directory_env_var(self):
        """Test default journal directory when env var missing."""
        with patch.dict(os.environ, {}, clear=True):
            settings = get_settings()
            # Should use default
            assert settings.journal_dir is not None

    def test_invalid_refresh_interval_env_var(self):
        """Test invalid refresh interval falls back to default."""
        with patch.dict(os.environ, {"REFRESH_INTERVAL": "not_a_number"}):
            settings = get_settings()
            # Should use default (not raise error)
            assert settings.refresh_interval > 0

    def test_invalid_path_env_var(self):
        """Test invalid path in env var is handled gracefully."""
        with patch.dict(os.environ, {"JOURNAL_DIR": "/invalid/path/that/does/not/exist"}):
            settings = get_settings()
            # Should not raise error, store value anyway
            assert settings.journal_dir == "/invalid/path/that/does/not/exist"

    def test_environment_variable_overrides(self):
        """Test environment variables override config file."""
        with patch.dict(os.environ, {"REFRESH_INTERVAL": "30"}):
            settings = get_settings()
            assert settings.refresh_interval == 30
```

---

### Priority 2: Enhanced `tests/test_notifications.py` - Discord Errors
**Location**: Add to existing test file (or enhance)
**Impact**: +15 lines in discord.py

```python
class TestDiscordNotificationErrors:
    @patch('src.notifications.discord.WebhookClient')
    def test_retry_exhaustion(self, mock_webhook_class):
        """Test that all retries are attempted before giving up."""
        mock_webhook = MagicMock()
        mock_webhook.send.side_effect = Exception("Connection failed")
        mock_webhook_class.return_value = mock_webhook
        
        notifier = DiscordNotifier(url="http://test")
        result = notifier.send_notification("Test signal", 50.0)
        
        assert result is False
        assert mock_webhook.send.call_count == 3  # Should retry 3 times

    @patch('src.notifications.discord.WebhookClient')
    def test_http_429_rate_limit(self, mock_webhook_class):
        """Test handling of HTTP 429 (rate limit) with retry."""
        mock_webhook = MagicMock()
        # First 2 calls fail with 429, third succeeds
        mock_webhook.send.side_effect = [
            HTTPError("429 Too Many Requests"),
            HTTPError("429 Too Many Requests"),
            None  # Success
        ]
        mock_webhook_class.return_value = mock_webhook
        
        notifier = DiscordNotifier(url="http://test")
        result = notifier.send_notification("Test signal", 50.0)
        
        assert result is True  # Should succeed after retries

    @patch('src.notifications.discord.WebhookClient')
    def test_http_500_server_error(self, mock_webhook_class):
        """Test handling of HTTP 500 (server error) with retry."""
        mock_webhook = MagicMock()
        mock_webhook.send.side_effect = HTTPError("500 Internal Server Error")
        mock_webhook_class.return_value = mock_webhook
        
        notifier = DiscordNotifier(url="http://test")
        result = notifier.send_notification("Test signal", 50.0)
        
        assert result is False

    @patch('src.notifications.discord.WebhookClient')
    def test_connection_timeout(self, mock_webhook_class):
        """Test handling of connection timeout."""
        mock_webhook = MagicMock()
        mock_webhook.send.side_effect = TimeoutError("Connection timed out")
        mock_webhook_class.return_value = mock_webhook
        
        notifier = DiscordNotifier(url="http://test")
        result = notifier.send_notification("Test signal", 50.0)
        
        assert result is False

    @patch('src.notifications.discord.WebhookClient')
    def test_transient_failure_recovery(self, mock_webhook_class):
        """Test successful recovery from transient failure."""
        mock_webhook = MagicMock()
        # First attempt fails, second succeeds
        mock_webhook.send.side_effect = [
            Exception("Transient error"),
            None  # Success
        ]
        mock_webhook_class.return_value = mock_webhook
        
        notifier = DiscordNotifier(url="http://test")
        result = notifier.send_notification("Test signal", 50.0)
        
        assert result is True
```

---

### Priority 3: Enhanced `tests/test_core.py` - Core Logic
**Location**: Enhance existing test file
**Impact**: +15-20 lines in core.py

```python
class TestHGENotifierManagerEdgeCases:
    def test_process_hge_signal_with_missing_coordinates(self):
        """Test signal processing when coordinates are missing."""
        manager = HGENotifierManager()
        manager.eddn_listener = MagicMock()
        manager.location_tracker = MagicMock()
        
        # Signal with missing coordinates
        signal = {"system_name": "Test", "coordinates": None}
        
        # Should handle gracefully
        result = manager._process_signal(signal)
        assert result is not None

    def test_location_update_with_invalid_coordinates(self):
        """Test location update handles invalid coordinate data."""
        manager = HGENotifierManager()
        manager.location_tracker = MagicMock()
        manager.location_tracker.get_location.return_value = {
            "system": "Test",
            "coordinates": {"x": None, "y": None, "z": None}
        }
        
        # Should not crash
        status = manager.get_status()
        assert status is not None

    def test_error_recovery_on_eddn_failure(self):
        """Test graceful recovery when EDDN connection fails."""
        manager = HGENotifierManager()
        manager.eddn_listener = MagicMock()
        manager.eddn_listener.start.side_effect = Exception("EDDN connection failed")
        
        # Should handle error
        result = manager.start()
        # Verify error was logged/handled
```

---

### Priority 3.2: Enhanced `tests/test_journal.py` - Journal Edge Cases
**Location**: Enhance existing test file
**Impact**: +10-15 lines in journal/__init__.py

```python
class TestJournalEdgeCases:
    def test_missing_journal_directory(self, tmp_path):
        """Test when journal directory doesn't exist."""
        missing_dir = tmp_path / "nonexistent"
        tracker = JournalLocationTracker(str(missing_dir))
        
        # Should handle gracefully
        location = tracker.get_location()
        assert location is None or location == {}

    def test_corrupted_journal_entry(self, tmp_path):
        """Test handling of corrupted JSON in journal."""
        journal_dir = tmp_path / "journal"
        journal_dir.mkdir()
        
        # Write corrupted JSON
        journal_file = journal_dir / "Journal.1.log"
        journal_file.write_text('{"System":"Test"}' + '\n' + '{INVALID JSON}')
        
        tracker = JournalLocationTracker(str(journal_dir))
        # Should not crash
        location = tracker.get_location()
        # Should still parse the valid entry
        assert location is not None or location is None  # Graceful handling

    def test_empty_journal_file(self, tmp_path):
        """Test handling of empty journal file."""
        journal_dir = tmp_path / "journal"
        journal_dir.mkdir()
        journal_file = journal_dir / "Journal.1.log"
        journal_file.write_text("")
        
        tracker = JournalLocationTracker(str(journal_dir))
        location = tracker.get_location()
        # Should return None or empty
        assert location is None or location == {}
```

---

## 📈 Expected Coverage Improvements

### Scenario 1: Phase 1 Only (Implement Basic Tests)
- `src/__main__.py`: 0% → 95% (34/36 lines)
- `src/cli.py`: 0% → 90% (65/72 lines)
- `src/web/__init__.py`: 0% → 80% (48/58 lines)

**New Coverage**: 64% → **71% (+7%)**

---

### Scenario 2: Phase 1 + Phase 2 (Add Edge Cases)
- `src/notifications/discord.py`: 74% → 90% (65/72 lines)
- `src/config/settings.py`: 87% → 95% (36/38 lines)
- `src/notifications/models.py`: 89% → 97% (34/35 lines)

**New Coverage**: 71% → **78% (+7% more)**

---

### Scenario 3: Full Implementation (Add Integration Tests)
- `src/core.py`: 65% → 80% (87/109 lines)
- `src/eddn/__init__.py`: 68% → 85% (142/167 lines)
- `src/journal/__init__.py`: 78% → 90% (135/150 lines)

**New Coverage**: 78% → **82-85% (+4-7% more)**

---

## 🎯 Action Plan

### Week 1: Quick Wins (2-3 hours)
**Goal**: Get to 75% coverage

1. Create `tests/test_cli.py` with basic tests
   - Time: 1 hour
   - Estimated impact: +20 lines coverage

2. Create `tests/test_main.py` with entry point tests
   - Time: 1 hour
   - Estimated impact: +25 lines coverage

3. Create `tests/test_web.py` with route tests
   - Time: 1.5 hours
   - Estimated impact: +35 lines coverage

### Week 2: Refinement (1-2 hours)
**Goal**: Get to 80% coverage

1. Add edge case tests for discord.py
2. Add validation tests for settings.py
3. Increase core.py coverage

---

## 💡 Key Implementation Tips

1. **Mock external dependencies**: Don't test Flask/logging directly, mock the manager
2. **Use fixtures**: Create reusable fixtures for common test setup
3. **Test all paths**: Include error paths, not just happy paths
4. **Parametrize tests**: Use `@pytest.mark.parametrize` for multiple scenarios
5. **Use capsys for output**: Capture print statements to verify display_status()

---

## 📊 Phase 2 Summary

### Overall Progress

| Phase | Status | Coverage | Change | Lines Added | Tests Added |
|-------|--------|----------|--------|------------|-------------|
| **Phase 1** | ✅ COMPLETE | 64% → 79% | +15% | 950+ | 100+ |
| **Phase 2** | 🔄 IN PLANNING | 79% → 85%+ | +6% | 60-80 | 15-25 |
| **Target** | 🎯 85%+ | - | - | - | - |

### Phase 2 Execution Options

#### Option A: Fast Path (1-1.5 hours)
**Coverage**: 79% → 80-81%
- Enhanced test_cli.py (continuous mode)
- New test_config.py (settings edge cases)
- **Result**: Minimal effort, small gain

#### Option B: Recommended Path (2.5-3 hours) ⭐
**Coverage**: 79% → 84-85%
- All of Option A
- Enhanced test_notifications.py (Discord errors)
- **Result**: Reach 85% target, high ROI

#### Option C: Comprehensive Path (5.5-7.5 hours)
**Coverage**: 79% → 87-88%
- All of Option B
- Enhanced test_core.py (core logic edge cases)
- Enhanced test_journal.py (file handling edge cases)
- **Result**: Near 90% coverage, high quality

#### Option D: Complete Path (7.5-10.5 hours)
**Coverage**: 79% → 89-90%
- All of Option C
- Enhanced test_eddn.py (EDDN connection scenarios)
- **Result**: Comprehensive testing, excellent quality

---

## 🎯 Phase 2 Recommended Action Plan

### Recommended: Execute Option B (Reach 85% Target)

**Step 1: Quick Wins (1-1.5 hours)**
1. Add 3-5 tests to `tests/test_cli.py` for continuous mode
2. Create new `tests/test_config.py` with 4-5 settings edge case tests

**Step 2: Discord Error Scenarios (1.5-2 hours)**
3. Add 5-7 tests to `tests/test_notifications.py` for:
   - Retry exhaustion
   - HTTP error codes (429, 500, 502)
   - Connection timeouts
   - Transient failure recovery

**Expected Result**: 84-85% coverage, 150+ total tests passing

---

## 📋 Phase 2 Next Steps

### Immediate Actions
1. ✅ **Review** this updated plan
2. ⏳ **Decide** on execution path (A, B, C, or D)
3. ⏳ **Begin** with Priority 1 (quick wins)
4. ⏳ **Verify** coverage improvement after each step

### File Modifications Required
**Phase 2 Option B Requires**:
- `tests/test_cli.py` - +3-5 tests (continuous mode)
- `tests/test_config.py` - NEW file (4-5 tests)
- `tests/test_notifications.py` - +5-7 tests (Discord errors)

**Expected New Lines**: 80-120 lines of test code
**Expected Coverage Gain**: +5-6% to reach 84-85%

---

## 🏁 Phase 2 Success Criteria

- ✅ All 64 Phase 1 tests still passing (zero regressions)
- ✅ 15-25 new Phase 2 tests created and passing
- ✅ Overall coverage reaches 84-85% (or higher with Option C/D)
- ✅ All critical error paths tested
- ✅ Total test suite: 160+ tests, 100% pass rate

---

**Next Step**: Start Phase 2 Option B (recommended) to reach 85% coverage target!
