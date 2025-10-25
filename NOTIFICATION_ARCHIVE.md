# Notification Feature Archive

## Summary
The notification feature has been archived (disabled) as of October 25, 2025 due to reliability issues.

## What Was Changed

### In `src/core.py`:

1. **Notification Manager Initialization** (lines 55-67)
   - The `NotificationManager` is no longer initialized
   - Set to `self.notification_manager = None`
   - Original initialization code is preserved in comments for future re-enabling

2. **Signal Callback** (lines 121-128)
   - Removed the `check_and_notify()` call
   - Code that triggered notifications on new signals is now commented out
   - The signal enrichment and storage still works normally

3. **Notification History Getter** (lines 345-365)
   - Added check for `self.notification_manager is None`
   - Returns empty list `[]` instead of trying to access notification history
   - Prevents crashes when endpoints are called

4. **Notification Stats Getter** (lines 367-381)
   - Added check for `self.notification_manager is None`
   - Returns empty stats `{"total": 0, "successful": 0, "failed": 0}`
   - Prevents crashes when stats are requested

## Web Interface Impact

The following endpoints are still active but return empty data:
- `GET /api/notifications` - Returns empty notification history
- `GET /api/notifications/stats` - Returns zero stats
- `POST /api/notifications/clear` - Does nothing

The notification UI sections on the web interface will display empty (0 notifications, no history).

## How to Re-enable

When the notification feature is ready to be re-enabled:

1. Uncomment the `NotificationManager` initialization in `src/core.py` lines 55-67
2. Change `self.notification_manager = None` to actual initialization
3. Uncomment the `check_and_notify()` call in the signal callback
4. Remove the None checks in `_format_notification_history()` and `_get_notification_stats()`

## What Still Works

✅ EDDN monitoring
✅ Journal tracking  
✅ Distance calculations
✅ Material inference
✅ Signal history
✅ Timeline view
✅ Dashboard display
✅ System info lookup

## What's Archived

🔴 Discord webhook notifications
🔴 In-app notification system
🔴 Notification cooldown logic
🔴 Notification history tracking
🔴 Alert configuration

The notification modules still exist in the codebase and can be reactivated later.
