"""Flask web interface for HGE Notifier."""

import logging
from flask import Flask, jsonify, render_template_string, request, Response
from socketio import AsyncServer
from typing import Union, Tuple

from src.core import HGENotifierManager
from src.web.websocket import WebSocketManager


def create_app(manager: HGENotifierManager, ws_manager: WebSocketManager | None = None) -> Flask:
    """Create and configure the Flask application.

    Args:
        manager: HGENotifierManager instance.
        ws_manager: Optional WebSocketManager for real-time updates.

    Returns:
        Configured Flask application.
    """
    app = Flask(__name__)
    app.config["JSON_SORT_KEYS"] = False
    
    logger = logging.getLogger(__name__)

    # Initialize WebSocket if manager provided
    if ws_manager:
        sio = ws_manager.initialize()
        
        @sio.event
        async def connect(sid, environ):
            """Handle WebSocket client connection."""
            logger.info(f"WebSocket client connected: {sid}")
        
        @sio.event
        async def disconnect(sid):
            """Handle WebSocket client disconnection."""
            logger.info(f"WebSocket client disconnected: {sid}")
        
        @sio.event
        async def subscribe(sid, data):
            """Handle channel subscription."""
            channels = data.get("channels", [])
            logger.debug(f"Client {sid} subscribing to channels: {channels}")
            await ws_manager._on_subscribe(sid, data)
        
        @sio.event
        async def unsubscribe(sid, data):
            """Handle channel unsubscription."""
            channels = data.get("channels", [])
            logger.debug(f"Client {sid} unsubscribing from channels: {channels}")
            await ws_manager._on_unsubscribe(sid, data)

    @app.route("/")
    def index() -> str:
        """Render the main dashboard."""
        return render_template_string(HTML_TEMPLATE)

    @app.route("/api/status")
    def api_status() -> Response:
        """Get current status as JSON."""
        return jsonify(manager.get_status())

    @app.route("/api/refresh", methods=["POST"])
    def api_refresh() -> Union[Response, Tuple[Response, int]]:
        """Trigger a manual refresh."""
        try:
            manager.refresh()
            return jsonify({"status": "success", "data": manager.get_status()})
        except Exception as e:
            logger.error(f"Error during refresh: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route("/api/notifications")
    def api_notifications() -> Union[Response, Tuple[Response, int]]:
        """Get notification history."""
        try:
            count = request.args.get("count", 10, type=int)
            history = manager.notification_manager.get_notification_history(count=count)
            return jsonify({
                "status": "success",
                "data": [
                    {
                        "system_name": notification.signal_system,
                        "distance_ly": notification.distance_ly,
                        "timestamp": notification.timestamp.isoformat(),
                        "channel": notification.channel,
                        "success": notification.success,
                        "error": notification.error,
                    }
                    for notification in history
                ],
            })
        except Exception as e:
            logger.error(f"Error getting notifications: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route("/api/notifications/stats")
    def api_notifications_stats() -> Union[Response, Tuple[Response, int]]:
        """Get notification statistics."""
        try:
            stats = manager.notification_manager.get_stats()
            return jsonify({
                "status": "success",
                "data": {
                    "total": stats.get("total", 0),
                    "successful": stats.get("successful", 0),
                    "failed": stats.get("failed", 0),
                },
            })
        except Exception as e:
            logger.error(f"Error getting notification stats: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route("/api/notifications/clear", methods=["POST"])
    def api_notifications_clear() -> Union[Response, Tuple[Response, int]]:
        """Clear notification history."""
        try:
            manager.notification_manager.in_app.clear_history()
            return jsonify({"status": "success", "message": "Notification history cleared"})
        except Exception as e:
            logger.error(f"Error clearing notifications: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route("/notifications")
    def notifications_page() -> str:
        """Render the notifications page."""
        return render_template_string(NOTIFICATIONS_TEMPLATE)

    return app


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HGE Notifier - Elite Dangerous</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Courier New', monospace;
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
            color: #00ff00;
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1000px;
            margin: 0 auto;
        }
        
        h1 {
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 0 0 10px #00ff00;
        }
        
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: rgba(0, 50, 0, 0.3);
            border: 2px solid #00ff00;
            border-radius: 5px;
            padding: 20px;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.2);
        }
        
        .card h2 {
            margin-bottom: 15px;
            font-size: 1.3em;
            border-bottom: 1px solid #00ff00;
            padding-bottom: 10px;
        }
        
        .card p {
            margin: 8px 0;
            font-size: 0.95em;
        }
        
        .label {
            color: #00cc00;
            font-weight: bold;
        }
        
        .value {
            color: #00ff00;
        }
        
        .distance-large {
            font-size: 2em;
            color: #ffff00;
            font-weight: bold;
            text-align: center;
            margin: 20px 0;
        }
        
        .unknown {
            color: #ff6600;
        }
        
        button {
            background: #001a00;
            border: 2px solid #00ff00;
            color: #00ff00;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-family: 'Courier New', monospace;
            font-size: 1em;
            margin-top: 20px;
            width: 100%;
            transition: all 0.3s;
        }
        
        button:hover {
            background: #003300;
            box-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
        }
        
        button:active {
            transform: scale(0.98);
        }
        
        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #00ff00;
            margin-right: 5px;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .error {
            color: #ff0000;
        }
        
        .coordinates {
            font-size: 0.9em;
            color: #00cc00;
            word-break: break-all;
        }
        
        .timestamp {
            font-size: 0.85em;
            color: #008800;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎮 HGE NOTIFIER</h1>
        
        <div class="status-grid" id="statusGrid">
            <div class="card">
                <h2>⏳ Loading...</h2>
                <p>Initializing data...</p>
            </div>
        </div>
        
        <div style="text-align: center;">
            <button onclick="refreshStatus()">🔄 REFRESH NOW</button>
        </div>
    </div>

    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <script>
        // =====================================================
        // WEBSOCKET CLIENT CONFIGURATION
        // =====================================================
        const socket = io();
        const statusEndpoint = "/api/status";
        const refreshEndpoint = "/api/refresh";
        
        // Track connection status
        let isConnected = false;
        let pollingTimer = null;
        const POLLING_INTERVAL_MS = 30000; // 30 seconds fallback polling
        
        // =====================================================
        // WEBSOCKET CONNECTION HANDLERS
        // =====================================================
        socket.on('connect', () => {
            console.log('✅ Connected to WebSocket server:', socket.id);
            isConnected = true;
            updateConnectionStatus(true);
            
            // Stop polling when connected (WebSocket will handle updates)
            if (pollingTimer !== null) {
                clearInterval(pollingTimer);
                pollingTimer = null;
                console.log('🔌 Polling stopped - using real-time updates');
            }
            
            // Subscribe to real-time updates
            socket.emit('subscribe', {
                channels: ['hge_signal', 'location_update', 'distance_update', 'status']
            });
        });
        
        socket.on('disconnect', () => {
            console.log('❌ Disconnected from WebSocket server');
            isConnected = false;
            updateConnectionStatus(false);
            
            // Start polling as fallback when disconnected
            if (pollingTimer === null) {
                console.log('⏱️ Starting fallback polling...');
                pollingTimer = setInterval(updateStatusViaREST, POLLING_INTERVAL_MS);
                // Immediate refresh to avoid waiting for first interval
                updateStatusViaREST();
            }
        });
        
        socket.on('connect_error', (error) => {
            console.error('Connection error:', error);
            updateConnectionStatus(false);
        });
        
        // =====================================================
        // WEBSOCKET EVENT LISTENERS
        // =====================================================
        socket.on('hge_signal_update', (data) => {
            console.log('📡 HGE Signal Update:', data);
            if (data) {
                renderHGESignal(data);
            }
        });
        
        socket.on('location_update', (data) => {
            console.log('📍 Location Update:', data);
            if (data) {
                renderLocation(data);
            }
        });
        
        socket.on('distance_update', (data) => {
            console.log('📏 Distance Update:', data);
            if (data) {
                renderDistance(data);
            }
        });
        
        socket.on('status_update', (data) => {
            console.log('📊 Status Update:', data);
            if (data) {
                renderStatus(data);
            }
        });
        
        // =====================================================
        // UI UPDATE FUNCTIONS
        // =====================================================
        function updateConnectionStatus(connected) {
            const indicator = document.querySelector('.status-indicator');
            if (indicator) {
                if (connected) {
                    indicator.style.background = '#00ff00';
                    indicator.title = 'Connected to server';
                } else {
                    indicator.style.background = '#ff6600';
                    indicator.title = 'Disconnected from server';
                }
            }
        }
        
        function renderHGESignal(signal) {
            const grid = document.getElementById("statusGrid");
            if (!grid) return;
            
            let signalCard = grid.querySelector('[data-card="hge-signal"]');
            if (!signalCard) {
                signalCard = document.createElement('div');
                signalCard.className = 'card';
                signalCard.setAttribute('data-card', 'hge-signal');
                grid.insertBefore(signalCard, grid.firstChild);
            }
            
            signalCard.innerHTML = `
                <h2>🔴 HGE Signal</h2>
                <p><span class="label">System:</span> <span class="value">${signal.system_name}</span></p>
                <p><span class="label">Age:</span> <span class="value">${signal.age}</span></p>
                <p><span class="label">Coordinates:</span></p>
                <div class="coordinates">
                    X: ${signal.coordinates.x?.toFixed(2) ?? 'N/A'}<br>
                    Y: ${signal.coordinates.y?.toFixed(2) ?? 'N/A'}<br>
                    Z: ${signal.coordinates.z?.toFixed(2) ?? 'N/A'}
                </div>
            `;
        }
        
        function renderLocation(location) {
            const grid = document.getElementById("statusGrid");
            if (!grid) return;
            
            let locationCard = grid.querySelector('[data-card="location"]');
            if (!locationCard) {
                locationCard = document.createElement('div');
                locationCard.className = 'card';
                locationCard.setAttribute('data-card', 'location');
                grid.appendChild(locationCard);
            }
            
            locationCard.innerHTML = `
                <h2>📍 Your Location</h2>
                <p><span class="label">System:</span> <span class="value">${location.system_name}</span></p>
                <p><span class="label">Coordinates:</span></p>
                <div class="coordinates">
                    X: ${location.coordinates.x?.toFixed(2) ?? 'N/A'}<br>
                    Y: ${location.coordinates.y?.toFixed(2) ?? 'N/A'}<br>
                    Z: ${location.coordinates.z?.toFixed(2) ?? 'N/A'}
                </div>
            `;
        }
        
        function renderDistance(distance) {
            const grid = document.getElementById("statusGrid");
            if (!grid) return;
            
            let distanceCard = grid.querySelector('[data-card="distance"]');
            if (!distanceCard) {
                distanceCard = document.createElement('div');
                distanceCard.className = 'card';
                distanceCard.setAttribute('data-card', 'distance');
                distanceCard.style.gridColumn = '1 / -1';
                grid.appendChild(distanceCard);
            }
            
            distanceCard.innerHTML = `
                <h2>📏 Distance to HGE</h2>
                <div class="distance-large">${distance.formatted}</div>
                <p style="text-align: center; color: #008800;">
                    <span class="status-indicator"></span>Last updated: ${new Date().toLocaleTimeString()}
                </p>
            `;
            updateConnectionStatus(isConnected);
        }
        
        // REST API fallback (only called when WebSocket disconnected)
        async function updateStatusViaREST() {
            try {
                const response = await fetch(statusEndpoint);
                if (!response.ok) {
                    console.error(`HTTP error! status: ${response.status}`);
                    return;
                }
                const data = await response.json();
                renderStatus(data);
            } catch (error) {
                console.error("Error fetching status via REST:", error);
            }
        }
        
        function renderStatus(status) {
            const grid = document.getElementById("statusGrid");
            let html = "";
            
            // HGE Signal Card
            if (status.hge_signal) {
                const signal = status.hge_signal;
                html += `
                    <div class="card">
                        <h2>🔴 HGE Signal</h2>
                        <p><span class="label">System:</span> <span class="value">${signal.system_name}</span></p>
                        <p><span class="label">Age:</span> <span class="value">${signal.age}</span></p>
                        <p><span class="label">Coordinates:</span></p>
                        <div class="coordinates">
                            X: ${signal.coordinates.x?.toFixed(2) ?? 'N/A'}<br>
                            Y: ${signal.coordinates.y?.toFixed(2) ?? 'N/A'}<br>
                            Z: ${signal.coordinates.z?.toFixed(2) ?? 'N/A'}
                        </div>
                    </div>
                `;
            } else {
                html += `
                    <div class="card">
                        <h2>🔴 HGE Signal</h2>
                        <p><span class="unknown">No signal detected yet</span></p>
                    </div>
                `;
            }
            
            // Commander Location Card
            if (status.commander_location) {
                const location = status.commander_location;
                html += `
                    <div class="card">
                        <h2>📍 Your Location</h2>
                        <p><span class="label">System:</span> <span class="value">${location.system_name}</span></p>
                        <p><span class="label">Coordinates:</span></p>
                        <div class="coordinates">
                            X: ${location.coordinates.x?.toFixed(2) ?? 'N/A'}<br>
                            Y: ${location.coordinates.y?.toFixed(2) ?? 'N/A'}<br>
                            Z: ${location.coordinates.z?.toFixed(2) ?? 'N/A'}
                        </div>
                    </div>
                `;
            } else {
                html += `
                    <div class="card">
                        <h2>📍 Your Location</h2>
                        <p><span class="unknown">Location unknown</span></p>
                    </div>
                `;
            }
            
            grid.innerHTML = html;
            
            // Distance Card
            if (status.distance) {
                const distance = status.distance;
                grid.innerHTML += `
                    <div class="card" style="grid-column: 1 / -1;">
                        <h2>📏 Distance to HGE</h2>
                        <div class="distance-large">${distance.formatted}</div>
                        <p style="text-align: center; color: #008800;">
                            <span class="status-indicator"></span>Last updated: ${new Date().toLocaleTimeString()}
                        </p>
                    </div>
                `;
            } else {
                grid.innerHTML += `
                    <div class="card" style="grid-column: 1 / -1;">
                        <h2>📏 Distance to HGE</h2>
                        <p><span class="unknown">Cannot calculate distance (missing data)</span></p>
                    </div>
                `;
            }
            updateConnectionStatus(isConnected);
        }
        
        function renderError(error) {
            const grid = document.getElementById("statusGrid");
            grid.innerHTML = `
                <div class="card">
                    <h2 class="error">⚠️ Error</h2>
                    <p><span class="error">${error.message}</span></p>
                </div>
            `;
        }
        
        function refreshStatus() {
            const btn = event.target;
            btn.disabled = true;
            btn.textContent = "⏳ Refreshing...";
            
            try {
                fetch(refreshEndpoint, { method: "POST" })
                    .then(response => response.json())
                    .then(data => renderStatus(data.data))
                    .catch(error => {
                        console.error("Error refreshing status:", error);
                        renderError(error);
                    })
                    .finally(() => {
                        btn.disabled = false;
                        btn.textContent = "🔄 REFRESH NOW";
                    });
            } catch (error) {
                console.error("Unexpected error during refresh:", error);
                btn.disabled = false;
                btn.textContent = "🔄 REFRESH NOW";
            }
        }
        
        // Initial load via REST API
        updateStatusViaREST();
        
        // Note: Real-time updates are driven by WebSocket events when connected
        // Fallback polling (every 30 seconds) is automatically enabled on disconnect
    </script>
</body>
</html>
"""


NOTIFICATIONS_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Notifications - HGE Notifier</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Courier New', monospace;
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
            color: #00ff00;
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        h1 {
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 0 0 10px #00ff00;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: rgba(0, 50, 0, 0.3);
            border: 2px solid #00ff00;
            border-radius: 5px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.2);
        }
        
        .stat-card h3 {
            font-size: 0.9em;
            margin-bottom: 10px;
            border-bottom: 1px solid #00ff00;
            padding-bottom: 10px;
        }
        
        .stat-value {
            font-size: 2.5em;
            color: #ffff00;
            font-weight: bold;
        }
        
        .history-section {
            background: rgba(0, 50, 0, 0.3);
            border: 2px solid #00ff00;
            border-radius: 5px;
            padding: 20px;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.2);
            margin-bottom: 20px;
        }
        
        .history-section h2 {
            margin-bottom: 20px;
            border-bottom: 2px solid #00ff00;
            padding-bottom: 10px;
        }
        
        .notification-item {
            border-left: 4px solid #00ff00;
            padding: 15px;
            margin-bottom: 15px;
            background: rgba(0, 100, 0, 0.2);
            border-radius: 3px;
        }
        
        .notification-item p {
            margin: 5px 0;
            font-size: 0.95em;
        }
        
        .notification-system {
            font-size: 1.2em;
            font-weight: bold;
            color: #ffff00;
            margin-bottom: 8px;
        }
        
        .notification-distance {
            color: #00ff00;
        }
        
        .notification-timestamp {
            color: #008800;
            font-size: 0.85em;
        }
        
        .notification-channel {
            display: inline-block;
            background: #001a00;
            border: 1px solid #00ff00;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 0.8em;
            margin-top: 8px;
        }
        
        .success {
            border-left-color: #00ff00;
            color: #00ff00;
        }
        
        .failed {
            border-left-color: #ff0000;
            color: #ff6666;
        }
        
        button {
            background: #001a00;
            border: 2px solid #00ff00;
            color: #00ff00;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-family: 'Courier New', monospace;
            font-size: 1em;
            margin-top: 20px;
            margin-right: 10px;
            transition: all 0.3s;
        }
        
        button:hover {
            background: #003300;
            box-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
        }
        
        button:active {
            transform: scale(0.98);
        }
        
        .button-group {
            text-align: center;
        }
        
        .empty-message {
            text-align: center;
            color: #008800;
            padding: 30px;
            font-size: 1.1em;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📬 NOTIFICATIONS</h1>
        
        <div class="stats-grid" id="statsGrid">
            <div class="stat-card">
                <h3>Total</h3>
                <div class="stat-value" id="statTotal">0</div>
            </div>
            <div class="stat-card">
                <h3>Successful</h3>
                <div class="stat-value" id="statSuccessful">0</div>
            </div>
            <div class="stat-card">
                <h3>Failed</h3>
                <div class="stat-value" id="statFailed">0</div>
            </div>
        </div>
        
        <div class="history-section">
            <h2>📋 Notification History</h2>
            <div id="historyContainer" class="empty-message">
                Loading notifications...
            </div>
        </div>
        
        <div class="button-group">
            <button onclick="refreshNotifications()">🔄 Refresh</button>
            <button onclick="clearNotifications()" style="background: #330000; border-color: #ff0000; color: #ff0000;">🗑️ Clear History</button>
        </div>
    </div>

    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <script>
        // =====================================================
        // WEBSOCKET CLIENT CONFIGURATION
        // =====================================================
        const socket = io();
        const statsEndpoint = "/api/notifications/stats";
        const historyEndpoint = "/api/notifications";
        
        // Track connection status
        let isConnected = false;
        let notificationsPollingTimer = null;
        const NOTIFICATIONS_POLLING_INTERVAL_MS = 10000; // 10 seconds fallback polling
        
        // =====================================================
        // WEBSOCKET CONNECTION HANDLERS
        // =====================================================
        socket.on('connect', () => {
            console.log('✅ Connected to WebSocket server:', socket.id);
            isConnected = true;
            updateConnectionStatus(true);
            
            // Stop polling when connected (WebSocket will handle updates)
            if (notificationsPollingTimer !== null) {
                clearInterval(notificationsPollingTimer);
                notificationsPollingTimer = null;
                console.log('🔌 Notifications polling stopped - using real-time updates');
            }
            
            // Subscribe to real-time updates
            socket.emit('subscribe', {
                channels: ['status']  // Notifications page watches status channel
            });
            
            // Load initial data
            loadNotifications();
        });
        
        socket.on('disconnect', () => {
            console.log('❌ Disconnected from WebSocket server');
            isConnected = false;
            updateConnectionStatus(false);
            
            // Start polling as fallback when disconnected
            if (notificationsPollingTimer === null) {
                console.log('⏱️ Starting fallback notifications polling...');
                notificationsPollingTimer = setInterval(loadNotifications, NOTIFICATIONS_POLLING_INTERVAL_MS);
                // Immediate refresh to avoid waiting for first interval
                loadNotifications();
            }
        });
        
        socket.on('connect_error', (error) => {
            console.error('Connection error:', error);
            updateConnectionStatus(false);
        });
        
        // =====================================================
        // WEBSOCKET EVENT LISTENERS
        // =====================================================
        // Listen for status updates which trigger notification refresh
        socket.on('status_update', (data) => {
            console.log('📊 Status Update (auto-refreshing notifications):', data);
            loadNotifications();
        });
        
        // =====================================================
        // UI UPDATE FUNCTIONS
        // =====================================================
        function updateConnectionStatus(connected) {
            let indicator = document.getElementById('connectionIndicator');
            if (!indicator) {
                // Create indicator if it doesn't exist
                const btn = document.querySelector('.button-group');
                if (btn) {
                    indicator = document.createElement('div');
                    indicator.id = 'connectionIndicator';
                    indicator.style.cssText = 'text-align: center; margin-top: 20px; padding: 10px; border-top: 1px solid #00ff00;';
                    btn.parentNode.insertBefore(indicator, btn.nextSibling);
                }
            }
            
            if (indicator) {
                if (connected) {
                    indicator.innerHTML = '<span style="color: #00ff00;">● Connected (Real-time)</span>';
                } else {
                    indicator.innerHTML = '<span style="color: #ff6600;">● Disconnected (Polling)</span>';
                }
            }
        }
        
        async function loadNotifications() {
            try {
                // Load stats
                const statsResponse = await fetch(statsEndpoint);
                const statsData = await statsResponse.json();
                if (statsData.status === "success") {
                    document.getElementById("statTotal").textContent = statsData.data.total;
                    document.getElementById("statSuccessful").textContent = statsData.data.successful;
                    document.getElementById("statFailed").textContent = statsData.data.failed;
                }
                
                // Load history
                const historyResponse = await fetch(historyEndpoint + "?count=20");
                const historyData = await historyResponse.json();
                if (historyData.status === "success") {
                    renderHistory(historyData.data);
                }
            } catch (error) {
                console.error("Error loading notifications:", error);
                document.getElementById("historyContainer").innerHTML = `
                    <div style="color: #ff0000; text-align: center;">Error loading notifications: ${error.message}</div>
                `;
            }
        }
        
        function renderHistory(notifications) {
            const container = document.getElementById("historyContainer");
            
            if (notifications.length === 0) {
                container.innerHTML = `<div class="empty-message">No notifications yet</div>`;
                return;
            }
            
            let html = "";
            for (const notif of notifications) {
                const timestamp = new Date(notif.timestamp).toLocaleString();
                const statusClass = notif.success ? "success" : "failed";
                const statusText = notif.success ? "✓ Success" : "✗ Failed";
                
                html += `
                    <div class="notification-item ${statusClass}">
                        <div class="notification-system">${notif.system_name}</div>
                        <p class="notification-distance">
                            <span style="color: #00ff00;">Distance:</span> ${notif.distance_ly.toFixed(2)} ly
                        </p>
                        <p class="notification-timestamp">${timestamp}</p>
                        <span class="notification-channel">${notif.channel} - ${statusText}</span>
                        ${notif.error ? `<p style="color: #ff0000; font-size: 0.85em;">Error: ${notif.error}</p>` : ""}
                    </div>
                `;
            }
            
            container.innerHTML = html;
        }
        
        async function refreshNotifications() {
            const btn = event.target;
            btn.disabled = true;
            btn.textContent = "⏳ Refreshing...";
            
            try {
                await loadNotifications();
            } finally {
                btn.disabled = false;
                btn.textContent = "🔄 Refresh";
            }
        }
        
        async function clearNotifications() {
            if (!confirm("Are you sure you want to clear all notifications?")) {
                return;
            }
            
            try {
                const response = await fetch("/api/notifications/clear", { method: "POST" });
                const data = await response.json();
                if (data.status === "success") {
                    document.getElementById("statTotal").textContent = "0";
                    document.getElementById("statSuccessful").textContent = "0";
                    document.getElementById("statFailed").textContent = "0";
                    document.getElementById("historyContainer").innerHTML = `<div class="empty-message">No notifications yet</div>`;
                } else {
                    alert("Error clearing notifications: " + data.message);
                }
            } catch (error) {
                console.error("Error clearing notifications:", error);
                alert("Error clearing notifications: " + error.message);
            }
        }
        
        // Initial load and connection status
        updateConnectionStatus(isConnected);
        loadNotifications();
        
        // Note: Real-time updates are driven by WebSocket events when connected
        // Fallback polling (every 10 seconds) is automatically enabled on disconnect
    </script>
</body>
</html>
"""


def run_server(
    manager: HGENotifierManager,
    host: str = "127.0.0.1",
    port: int = 5000,
    debug: bool = False,
    enable_websocket: bool = True,
) -> None:
    """Run the Flask web server with optional WebSocket support.

    Args:
        manager: HGENotifierManager instance.
        host: Host to bind to.
        port: Port to bind to.
        debug: Enable debug mode.
        enable_websocket: Enable WebSocket real-time updates.
    """
    # Create WebSocket manager if enabled
    ws_manager = None
    if enable_websocket:
        ws_manager = WebSocketManager(async_mode="threading")
        manager.websocket_manager = ws_manager
    
    app = create_app(manager, ws_manager)
    manager.start()
    
    try:
        if ws_manager:
            # Use python-socketio with Flask
            from socketio import WSGIApp
            app_with_socketio = WSGIApp(ws_manager.sio, app)
            from werkzeug.serving import run_simple
            run_simple(host, port, app_with_socketio, use_reloader=debug, use_debugger=debug)
        else:
            app.run(host=host, port=port, debug=debug)
    finally:
        manager.stop()
        if ws_manager:
            ws_manager.close()
