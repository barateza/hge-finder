"""Flask web interface for HGE Notifier."""

import logging
from flask import Flask, jsonify, render_template_string

from src.core import HGENotifierManager


def create_app(manager: HGENotifierManager) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config["JSON_SORT_KEYS"] = False
    
    logger = logging.getLogger(__name__)

    @app.route("/")
    def index() -> str:
        """Render the main dashboard."""
        return render_template_string(HTML_TEMPLATE)

    @app.route("/api/status")
    def api_status() -> dict:
        """Get current status as JSON."""
        return jsonify(manager.get_status())

    @app.route("/api/refresh", methods=["POST"])
    def api_refresh() -> dict:
        """Trigger a manual refresh."""
        try:
            manager.refresh()
            return jsonify({"status": "success", "data": manager.get_status()})
        except Exception as e:
            logger.error(f"Error during refresh: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

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

    <script>
        const statusEndpoint = "/api/status";
        const refreshEndpoint = "/api/refresh";
        const autoRefreshInterval = 10000; // 10 seconds
        
        async function updateStatus() {
            try {
                const response = await fetch(statusEndpoint);
                const data = await response.json();
                renderStatus(data);
            } catch (error) {
                console.error("Error fetching status:", error);
                renderError(error);
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
        
        async function refreshStatus() {
            const btn = event.target;
            btn.disabled = true;
            btn.textContent = "⏳ Refreshing...";
            
            try {
                const response = await fetch(refreshEndpoint, { method: "POST" });
                const data = await response.json();
                renderStatus(data.data);
            } catch (error) {
                console.error("Error refreshing status:", error);
                renderError(error);
            } finally {
                btn.disabled = false;
                btn.textContent = "🔄 REFRESH NOW";
            }
        }
        
        // Initial load
        updateStatus();
        
        // Auto-refresh every 10 seconds
        setInterval(updateStatus, autoRefreshInterval);
    </script>
</body>
</html>
"""


def run_server(
    manager: HGENotifierManager,
    host: str = "127.0.0.1",
    port: int = 5000,
    debug: bool = False,
) -> None:
    """Run the Flask web server."""
    app = create_app(manager)
    manager.start()
    
    try:
        app.run(host=host, port=port, debug=debug)
    finally:
        manager.stop()
