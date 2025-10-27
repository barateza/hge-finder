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

    @app.route("/api/hge/materials")
    def api_materials() -> Union[Response, Tuple[Response, int]]:
        """Get materials for the current HGE signal."""
        try:
            status = manager.get_status()
            signal_data = status.get("hge_signal")
            if not signal_data:
                return jsonify({"status": "success", "data": None})
            
            if isinstance(signal_data, dict):
                return jsonify({
                    "status": "success",
                    "data": {
                        "system_name": signal_data.get("system_name"),
                        "allegiance": signal_data.get("allegiance"),
                        "government": signal_data.get("government"),
                        "population": signal_data.get("population"),
                        "state": signal_data.get("state"),
                        "materials": signal_data.get("materials", {"count": 0, "materials": []}),
                    }
                })
            
            return jsonify({"status": "success", "data": None})
        except Exception as e:
            logger.error(f"Error getting materials: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

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
            # Notification system is archived
            if manager.notification_manager is None:
                return jsonify({
                    "status": "success",
                    "data": [],
                })
            
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
                    for notification in history  # type: ignore
                ],
            })
        except Exception as e:
            logger.error(f"Error getting notifications: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route("/api/notifications/stats")
    def api_notifications_stats() -> Union[Response, Tuple[Response, int]]:
        """Get notification statistics."""
        try:
            # Notification system is archived
            if manager.notification_manager is None:
                return jsonify({
                    "status": "success",
                    "data": {
                        "total": 0,
                        "successful": 0,
                        "failed": 0,
                    },
                })
            
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
            # Notification system is archived
            if manager.notification_manager is None:
                return jsonify({"status": "success", "message": "Notification system is archived"})
            
            manager.notification_manager.in_app.clear_history()
            return jsonify({"status": "success", "message": "Notification history cleared"})
        except Exception as e:
            logger.error(f"Error clearing notifications: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route("/api/timeline")
    def api_timeline() -> Union[Response, Tuple[Response, int]]:
        """Get HGE signal detection timeline data."""
        try:
            limit = request.args.get("limit", 50, type=int)
            signal_history = manager.get_signal_history(limit=limit)
            
            return jsonify({
                "status": "success",
                "data": signal_history,
            })
        except Exception as e:
            logger.error(f"Error getting timeline: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route("/api/timeline/summary")
    def api_timeline_summary() -> Union[Response, Tuple[Response, int]]:
        """Get timeline summary statistics."""
        try:
            signal_history = manager.get_signal_history(limit=100)
            
            if not signal_history:
                return jsonify({
                    "status": "success",
                    "data": {
                        "total_signals": 0,
                        "avg_distance": 0,
                        "min_distance": 0,
                        "max_distance": 0,
                        "hourly_distribution": {},
                    }
                })
            
            hourly = {}
            distances = []
            for signal in signal_history:
                try:
                    from datetime import datetime
                    ts = datetime.fromisoformat(signal["timestamp"])
                    hour = ts.strftime("%H:00")
                    hourly[hour] = hourly.get(hour, 0) + 1
                    
                    # Collect distances
                    if signal.get("distance_ly") and signal.get("distance_ly") > 0:
                        distances.append(signal.get("distance_ly"))
                except (KeyError, ValueError):
                    continue
            
            # Calculate distance statistics
            avg_distance = sum(distances) / len(distances) if distances else 0
            min_distance = min(distances) if distances else 0
            max_distance = max(distances) if distances else 0
            
            return jsonify({
                "status": "success",
                "data": {
                    "total_signals": len(signal_history),
                    "avg_distance": round(avg_distance, 2),
                    "min_distance": round(min_distance, 2),
                    "max_distance": round(max_distance, 2),
                    "hourly_distribution": hourly,
                }
            })
        except Exception as e:
            logger.error(f"Error getting timeline summary: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route("/api/timeline/trends")
    def api_timeline_trends() -> Union[Response, Tuple[Response, int]]:
        """Get distance trends data for charting."""
        try:
            signal_history = manager.get_signal_history(limit=100)
            
            trends = []
            for signal in signal_history:
                trends.append({
                    "timestamp": signal["timestamp"],
                    "system": signal["system_name"],
                })
            
            return jsonify({
                "status": "success",
                "data": trends,
            })
        except Exception as e:
            logger.error(f"Error getting trends: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route("/api/systems")
    def api_systems() -> Union[Response, Tuple[Response, int]]:
        """Get all active systems aggregated by system name and material.

        Query Parameters:
            sort_by: 'recent' (default), 'reports', or 'distance'
            material: Filter by material name (optional)
            limit: Maximum number of systems to return (default 50)

        Returns:
            JSON array of active SystemSignalGroup objects with formatting.
        """
        try:
            sort_by = request.args.get("sort_by", "recent", type=str)
            material_filter = request.args.get("material", None, type=str)
            limit = request.args.get("limit", 50, type=int)

            # Validate sort_by parameter (merger only supports 'recent', 'reports', 'name')
            valid_sorts = ['recent', 'reports', 'distance']
            if sort_by not in valid_sorts:
                sort_by = 'recent'

            # Get active systems (use 'recent' or 'reports' for merger, handle 'distance' in post-processing)
            merger_sort = 'recent' if sort_by == 'distance' else sort_by
            active_systems = manager.signal_merger.get_active_systems(sort_by=merger_sort)

            # Filter by material if specified
            if material_filter:
                active_systems = [
                    system for system in active_systems
                    if material_filter in system.materials
                ]

            # Format systems
            formatted_systems = []
            location = manager.journal_parser.get_latest_location()
            location = manager._enrich_location_coordinates(location)

            for system_group in active_systems[:limit]:
                system_data = manager._format_system_group(system_group)

                # Calculate distance if commander location available
                if location and location.x is not None and system_group.coordinates.get("x") is not None:
                    try:
                        distance = manager.distance_calculator.calculate_distance(
                            location.x, location.y, location.z,
                            system_group.coordinates["x"],
                            system_group.coordinates["y"],
                            system_group.coordinates["z"],
                        )
                        if distance is not None:
                            system_data["distance_ly"] = round(distance, 2)
                    except Exception as e:
                        logger.debug(f"Error calculating distance to {system_group.system_name}: {e}")

                formatted_systems.append(system_data)

            # Sort by distance if requested and distances are available
            if sort_by == 'distance':
                formatted_systems.sort(key=lambda s: s.get('distance_ly', float('inf')))

            return jsonify({
                "status": "success",
                "data": formatted_systems,
                "count": len(formatted_systems),
                "material_filter": material_filter,
                "sort_by": sort_by,
            })
        except Exception as e:
            logger.error(f"Error getting systems: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route("/api/systems/<system_name>")
    def api_system_detail(system_name: str) -> Union[Response, Tuple[Response, int]]:
        """Get detailed information about a specific system.

        Args:
            system_name: Name of the system to retrieve.

        Returns:
            JSON object with system details, material breakdown, and player reports.
        """
        try:
            system_group = manager.signal_merger.get_system_by_name(system_name)

            if system_group is None:
                return jsonify({
                    "status": "error",
                    "message": f"System '{system_name}' not found in active systems",
                }), 404

            system_data = manager._format_system_group(system_group)

            # Calculate distance
            location = manager.journal_parser.get_latest_location()
            location = manager._enrich_location_coordinates(location)

            if location and location.x is not None and system_group.coordinates.get("x") is not None:
                try:
                    distance = manager.distance_calculator.calculate_distance(
                        location.x, location.y, location.z,
                        system_group.coordinates["x"],
                        system_group.coordinates["y"],
                        system_group.coordinates["z"],
                    )
                    if distance is not None:
                        system_data["distance_ly"] = round(distance, 2)
                except Exception as e:
                    logger.debug(f"Error calculating distance: {e}")

            # Add material breakdown details (materials is Dict[str, MaterialReport])
            system_data["material_breakdown"] = [
                {
                    "name": material_name,
                    "count": material_report.player_reports,
                    "timestamp": material_report.timestamp.isoformat(),
                    "age": material_report.age_human_readable(),
                }
                for material_name, material_report in system_group.materials.items()
            ]

            return jsonify({
                "status": "success",
                "data": system_data,
            })
        except Exception as e:
            logger.error(f"Error getting system details: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route("/api/materials/<material_name>")
    def api_systems_by_material(material_name: str) -> Union[Response, Tuple[Response, int]]:
        """Get all active systems that have reported a specific material.

        Args:
            material_name: Name of the material to search for.

        Returns:
            JSON array of systems containing the specified material.
        """
        try:
            limit = request.args.get("limit", 50, type=int)

            # Get systems with this material
            systems_with_material = manager.signal_merger.get_systems_by_material(material_name)

            # Format systems
            formatted_systems = []
            location = manager.journal_parser.get_latest_location()
            location = manager._enrich_location_coordinates(location)

            for system_group in systems_with_material[:limit]:
                system_data = manager._format_system_group(system_group)

                # Calculate distance
                if location and location.x is not None and system_group.coordinates.get("x") is not None:
                    try:
                        distance = manager.distance_calculator.calculate_distance(
                            location.x, location.y, location.z,
                            system_group.coordinates["x"],
                            system_group.coordinates["y"],
                            system_group.coordinates["z"],
                        )
                        if distance is not None:
                            system_data["distance_ly"] = round(distance, 2)
                    except Exception as e:
                        logger.debug(f"Error calculating distance: {e}")

                formatted_systems.append(system_data)

            return jsonify({
                "status": "success",
                "data": formatted_systems,
                "material": material_name,
                "count": len(formatted_systems),
            })
        except Exception as e:
            logger.error(f"Error getting systems by material: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route("/api/materials")
    def api_all_materials() -> Union[Response, Tuple[Response, int]]:
        """Get all unique materials found across active systems with counts.

        Returns:
            JSON object with unique materials and their occurrence counts.
        """
        try:
            all_materials_list = manager.signal_merger.get_all_materials()
            active_systems = manager.signal_merger.get_active_systems()

            # Build material statistics
            materials_data = []
            for material_name in all_materials_list:
                # Count occurrences and total reports for this material
                occurrences = 0
                total_reports = 0
                for system in active_systems:
                    if material_name in system.materials:
                        occurrences += 1
                        total_reports += system.materials[material_name].player_reports

                materials_data.append({
                    "name": material_name,
                    "occurrences": occurrences,
                    "total_reports": total_reports,
                })

            # Sort by total reports descending
            materials_data.sort(key=lambda x: x["total_reports"], reverse=True)

            return jsonify({
                "status": "success",
                "data": materials_data,
                "count": len(materials_data),
            })
        except Exception as e:
            logger.error(f"Error getting materials: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route("/timeline")
    def timeline_page() -> str:
        """Render the timeline/charts page."""
        return render_template_string(TIMELINE_TEMPLATE)

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
        
        /* Materials styling */
        .materials-section {
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #00cc00;
        }
        
        .materials-list {
            list-style: none;
            padding-left: 0;
            margin: 10px 0;
        }
        
        .materials-list li {
            padding: 5px 0;
            color: #00ff00;
            font-size: 0.95em;
        }
        
        .materials-list .rarity {
            color: #ffff00;
            font-size: 0.85em;
            font-style: italic;
        }
        
        /* ===================================================
           SYSTEMS TABLE STYLING
           =================================================== */
        
        table {
            width: 100%;
            border-collapse: collapse;
        }
        
        table th {
            background: rgba(0, 100, 0, 0.2);
            padding: 12px;
            text-align: left;
            border-bottom: 2px solid #00ff00;
            color: #00ff00;
            font-weight: bold;
        }
        
        table td {
            padding: 12px;
            border-bottom: 1px solid rgba(0, 255, 0, 0.2);
            color: #00ff00;
        }
        
        table tbody tr:hover {
            background: rgba(0, 100, 0, 0.3);
        }
        
        table tbody tr:nth-child(even) {
            background: rgba(0, 50, 0, 0.2);
        }
        
        /* System name column */
        .system-name {
            font-weight: bold;
            color: #ffff00;
            font-size: 1.05em;
        }
        
        /* Materials column */
        .materials-list-inline {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        
        .materials-list-inline li {
            padding: 3px 0;
            margin: 0;
            font-size: 0.9em;
        }
        
        .material-count {
            color: #ffff00;
            font-weight: bold;
            margin-left: 5px;
        }
        
        /* Status indicators */
        .status-fresh {
            color: #00ff00;
        }
        
        .status-recent {
            color: #ffff00;
        }
        
        .status-old {
            color: #ff9900;
        }
        
        .status-stale {
            color: #ff0000;
        }
        
        /* Material filter tabs */
        .material-tab {
            background: #001a00;
            border: 2px solid #00ff00;
            color: #00ff00;
            padding: 8px 15px;
            border-radius: 5px;
            cursor: pointer;
            font-family: 'Courier New', monospace;
            font-size: 0.95em;
            transition: all 0.3s;
            white-space: nowrap;
        }
        
        .material-tab:hover {
            background: #003300;
            box-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
        }
        
        .material-tab.active {
            background: #003300;
            box-shadow: 0 0 15px rgba(0, 255, 0, 0.7);
        }
        
        /* ===================================================
           MOBILE RESPONSIVE ENHANCEMENTS
           =================================================== */
        
        /* Touch-friendly button sizing */
        @media (max-width: 768px) {
            button {
                padding: 15px 20px;
                font-size: 1.1em;
                min-height: 44px;  /* Touch target minimum */
            }
        }
        
        /* Small screens (portrait) */
        @media (max-width: 600px) {
            body {
                padding: 10px;
                font-size: 14px;
            }
            
            h1 {
                font-size: 1.8em;
                margin-bottom: 20px;
            }
            
            .container {
                max-width: 100%;
            }
            
            .status-grid {
                grid-template-columns: 1fr;
                gap: 15px;
                margin-bottom: 20px;
            }
            
            .card {
                padding: 15px;
                margin-bottom: 10px;
            }
            
            .card h2 {
                font-size: 1.1em;
                margin-bottom: 10px;
                padding-bottom: 8px;
            }
            
            .card p {
                font-size: 0.9em;
                margin: 6px 0;
            }
            
            .distance-large {
                font-size: 1.5em;
                margin: 15px 0;
            }
            
            .coordinates {
                font-size: 0.85em;
            }
            
            button {
                margin-top: 15px;
            }
        }
        
        /* Extra small screens */
        @media (max-width: 360px) {
            h1 {
                font-size: 1.4em;
                margin-bottom: 15px;
            }
            
            body {
                padding: 8px;
            }
            
            .card {
                padding: 12px;
            }
            
            .distance-large {
                font-size: 1.2em;
            }
        }
        
        /* Landscape orientation */
        @media (max-width: 900px) and (orientation: landscape) {
            h1 {
                margin-bottom: 10px;
                font-size: 1.8em;
            }
            
            .status-grid {
                grid-template-columns: repeat(2, 1fr);
                gap: 15px;
                margin-bottom: 15px;
            }
            
            body {
                padding: 10px;
            }
            
            .card {
                padding: 12px;
            }
            
            .card h2 {
                font-size: 1em;
                margin-bottom: 8px;
            }
            
            .card p {
                font-size: 0.85em;
                margin: 4px 0;
            }
        }
        
        /* Touch-friendly spacing */
        @media (hover: none) and (pointer: coarse) {
            button {
                padding: 16px 20px;
                margin-top: 20px;
            }
            
            button:active {
                background: #003300;
                box-shadow: 0 0 15px rgba(0, 255, 0, 0.7);
            }
        }
        
        /* Dark mode optimization for mobile OLED screens */
        @media (prefers-color-scheme: dark) {
            body {
                background: linear-gradient(135deg, #000000 0%, #0a0a0a 100%);
            }
        }
        
        /* High DPI displays (Retina) */
        @media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi) {
            .status-indicator {
                width: 12px;
                height: 12px;
            }
            
            .card {
                border-width: 1px;
            }
        }
        
        /* Accessibility improvements */
        @media (prefers-reduced-motion: reduce) {
            * {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎮 HGE NOTIFIER</h1>
        
        <div style="text-align: center; margin-bottom: 20px; display: flex; gap: 10px; justify-content: center; flex-wrap: wrap;">
            <a href="/timeline" style="background: #001a00; border: 2px solid #00ff00; color: #00ff00; padding: 8px 15px; border-radius: 5px; text-decoration: none; transition: all 0.3s;">📊 Timeline</a>
            <a href="/notifications" style="background: #001a00; border: 2px solid #00ff00; color: #00ff00; padding: 8px 15px; border-radius: 5px; text-decoration: none; transition: all 0.3s;">📢 Notifications</a>
        </div>
        
        <!-- Systems Aggregation Section -->
        <div id="systemsSection" style="margin-bottom: 30px;">
            <!-- Sorting Controls -->
            <div style="margin-bottom: 15px; display: flex; gap: 10px; justify-content: center; flex-wrap: wrap;">
                <label for="sortSelect" style="color: #00ff00; font-weight: bold; display: flex; align-items: center;">Sort by:</label>
                <select id="sortSelect" onchange="updateSystemsDisplay()" style="background: #001a00; border: 2px solid #00ff00; color: #00ff00; padding: 8px 15px; border-radius: 5px; font-family: 'Courier New', monospace; font-size: 0.95em;">
                    <option value="recent">📅 Most Recent</option>
                    <option value="reports">📊 Most Reports</option>
                    <option value="distance">📏 Closest Distance</option>
                </select>
            </div>
            
            <!-- Material Filter Tabs -->
            <div style="margin-bottom: 15px; border-bottom: 2px solid #00ff00; padding-bottom: 10px; display: flex; gap: 8px; justify-content: center; flex-wrap: wrap;" id="materialTabs">
                <button class="material-tab active" data-material="all" onclick="filterByMaterial('all', event)" style="background: #003300; border: 2px solid #00ff00; color: #00ff00; padding: 8px 15px; border-radius: 5px; cursor: pointer; font-family: 'Courier New', monospace; font-size: 0.95em; transition: all 0.3s;">All</button>
            </div>
            
            <!-- Systems Table -->
            <div style="background: rgba(0, 50, 0, 0.3); border: 2px solid #00ff00; border-radius: 5px; overflow-x: auto; box-shadow: 0 0 20px rgba(0, 255, 0, 0.2);">
                <table id="systemsTable" style="width: 100%; border-collapse: collapse; font-family: 'Courier New', monospace; font-size: 0.95em;">
                    <thead>
                        <tr style="border-bottom: 2px solid #00ff00;">
                            <th style="padding: 12px; text-align: left; color: #00ff00;">System</th>
                            <th style="padding: 12px; text-align: left; color: #00ff00;">Allegiance / State</th>
                            <th style="padding: 12px; text-align: left; color: #00ff00;">Materials</th>
                            <th style="padding: 12px; text-align: center; color: #00ff00;">Last Signal</th>
                            <th style="padding: 12px; text-align: center; color: #00ff00;">Reports</th>
                            <th style="padding: 12px; text-align: center; color: #00ff00;">Distance</th>
                            <th style="padding: 12px; text-align: center; color: #00ff00;">Status</th>
                        </tr>
                    </thead>
                    <tbody id="systemsTableBody">
                        <tr>
                            <td colspan="7" style="padding: 30px; text-align: center; color: #008800;">⏳ Loading active systems...</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            
            <!-- Systems Summary -->
            <div style="margin-top: 15px; text-align: center; color: #00ff00;">
                <span>Total systems: <span id="totalSystems" style="color: #ffff00; font-weight: bold;">0</span></span>
                <span style="margin: 0 15px;">|</span>
                <span>Total reports: <span id="totalReports" style="color: #ffff00; font-weight: bold;">0</span></span>
                <span style="margin: 0 15px;">|</span>
                <span>Materials: <span id="totalMaterials" style="color: #ffff00; font-weight: bold;">0</span></span>
            </div>
        </div>
        
        <!-- Classic Status Cards Section -->
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
        
        socket.on('system_group_update', (data) => {
            console.log('🔄 System Group Update:', data);
            // Refresh the systems display when new signal arrives
            updateSystemsDisplay();
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
            
            // Build materials HTML
            let materialsHtml = '';
            if (signal.materials && signal.materials.count > 0) {
                materialsHtml = `
                    <div class="materials-section">
                        <p><span class="label">💎 Possible Materials:</span></p>
                        <ul class="materials-list">
                            ${signal.materials.materials.map(m => 
                                `<li>${m.name} <span class="rarity">(${m.rarity})</span></li>`
                            ).join('')}
                        </ul>
                    </div>
                `;
            } else if (signal.allegiance || signal.state) {
                materialsHtml = `
                    <div class="materials-section">
                        <p><span class="label">System Info:</span></p>
                        <p>${signal.allegiance || 'N/A'} - ${signal.state || 'Unknown state'}</p>
                    </div>
                `;
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
                ${materialsHtml}
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
        
        // =====================================================
        // SYSTEMS AGGREGATION FUNCTIONS
        // =====================================================
        const systemsEndpoint = "/api/systems";
        const materialsEndpoint = "/api/materials";
        
        let currentSortBy = "recent";
        let currentMaterialFilter = "all";
        let allSystems = [];
        let allMaterials = [];
        
        async function loadMaterials() {
            // Load available materials and populate filter tabs
            try {
                const response = await fetch(materialsEndpoint);
                const data = await response.json();
                
                if (data.status !== 'success' || !data.data) {
                    console.warn("No materials available");
                    return;
                }
                
                allMaterials = data.data;
                
                // Populate material tabs
                const tabsContainer = document.getElementById('materialTabs');
                const existingTabs = tabsContainer.querySelectorAll('.material-tab');
                
                // Keep the "All" tab, remove others if needed
                if (existingTabs.length === 1) {
                    // Add new tabs for each material
                    allMaterials.forEach(material => {
                        const btn = document.createElement('button');
                        btn.className = 'material-tab';
                        btn.setAttribute('data-material', material.name);
                        btn.textContent = '💎 ' + material.name + ' (' + material.occurrences + ')';
                        btn.onclick = (e) => filterByMaterial(material.name, e);
                        tabsContainer.appendChild(btn);
                    });
                }
            } catch (error) {
                console.error('Error loading materials:', error);
            }
        }
        
        async function updateSystemsDisplay() {
            // Fetch and display systems based on current filters
            try {
                const sortBy = document.getElementById('sortSelect').value;
                const url = new URL(systemsEndpoint, window.location.origin);
                url.searchParams.append('sort_by', sortBy);
                url.searchParams.append('limit', 100);
                
                if (currentMaterialFilter !== 'all') {
                    url.searchParams.append('material', currentMaterialFilter);
                }
                
                const response = await fetch(url);
                const data = await response.json();
                
                if (data.status !== 'success' || !data.data) {
                    displayNoSystems();
                    return;
                }
                
                allSystems = data.data;
                renderSystemsTable(allSystems);
                updateSystemsSummary(data.count);
            } catch (error) {
                console.error('Error updating systems display:', error);
                displayNoSystems();
            }
        }
        
        function filterByMaterial(materialName, event) {
            // Filter systems by material type
            // Update active tab
            document.querySelectorAll('.material-tab').forEach(tab => {
                tab.classList.remove('active');
            });
            event.target.classList.add('active');
            
            // Update filter and refresh display
            currentMaterialFilter = materialName;
            updateSystemsDisplay();
        }
        
        function renderSystemsTable(systems) {
            // Render systems table with aggregated data
            const tbody = document.getElementById('systemsTableBody');
            
            if (!systems || systems.length === 0) {
                displayNoSystems();
                return;
            }
            
            tbody.innerHTML = systems.map(system => {
                // Determine status indicator
                let statusClass = 'status-fresh';
                let statusEmoji = '🟢';
                const ageStr = system.last_signal_age;
                
                if (ageStr.includes('h') || ageStr.includes('d')) {
                    const match = ageStr.match(/(\d+)/);
                    if (match) {
                        const value = parseInt(match[1]);
                        if (ageStr.includes('d')) {
                            statusClass = 'status-stale';
                            statusEmoji = '🔴';
                        } else if (value >= 2) {
                            statusClass = 'status-old';
                            statusEmoji = '🟠';
                        } else {
                            statusClass = 'status-recent';
                            statusEmoji = '🟡';
                        }
                    }
                }
                
                // Build materials list
                const materialsHtml = system.materials.map(mat => 
                    '<li>💎 ' + mat.name + '<span class="material-count">×' + mat.count + '</span></li>'
                ).join('');
                
                return '<tr>' +
                    '<td><span class="system-name">' + system.system_name + '</span></td>' +
                    '<td>' + (system.allegiance || 'N/A') + ' / ' + (system.state || 'N/A') + '</td>' +
                    '<td><ul class="materials-list-inline">' + materialsHtml + '</ul></td>' +
                    '<td style="text-align: center; font-size: 0.9em;">' + system.last_signal_age + '</td>' +
                    '<td style="text-align: center; color: #ffff00; font-weight: bold;">' + system.total_reports + '</td>' +
                    '<td style="text-align: center;">' + (system.distance_ly ? system.distance_ly.toFixed(2) + ' ly' : 'N/A') + '</td>' +
                    '<td style="text-align: center;"><span class="' + statusClass + '">' + statusEmoji + '</span></td>' +
                    '</tr>';
            }).join('');
        }
        
        function displayNoSystems() {
            // Display message when no systems are available
            const tbody = document.getElementById('systemsTableBody');
            tbody.innerHTML = '<tr><td colspan="7" style="padding: 30px; text-align: center; color: #008800;">⏳ No systems found</td></tr>';
        }
        
        function updateSystemsSummary(count) {
            // Update the systems summary statistics
            const totalReports = allSystems.reduce((sum, sys) => sum + sys.total_reports, 0);
            const uniqueMaterials = new Set();
            
            allSystems.forEach(system => {
                system.materials.forEach(mat => {
                    uniqueMaterials.add(mat.name);
                });
            });
            
            document.getElementById('totalSystems').textContent = count;
            document.getElementById('totalReports').textContent = totalReports;
            document.getElementById('totalMaterials').textContent = uniqueMaterials.size;
        }
        
        // Initial load via REST API
        updateStatusViaREST();
        
        // Load systems and materials
        loadMaterials();
        updateSystemsDisplay();
        
        // Note: Real-time updates are driven by WebSocket events when connected
        // Fallback polling (every 30 seconds) is automatically enabled on disconnect
        
        // =====================================================
        // MOBILE-SPECIFIC OPTIMIZATIONS
        // =====================================================
        
        // Detect if device is touch-enabled
        const isTouchDevice = () => {
            return (('ontouchstart' in window) ||
                    (navigator.maxTouchPoints > 0) ||
                    (navigator.msMaxTouchPoints > 0));
        };
        
        // Track touch gestures
        let touchStartX = 0;
        let touchEndX = 0;
        let touchStartY = 0;
        let touchEndY = 0;
        
        // Handle swipe to refresh
        function handleSwipe() {
            const swipeThreshold = 50;
            const diffX = Math.abs(touchEndX - touchStartX);
            const diffY = Math.abs(touchEndY - touchStartY);
            
            // Swipe down detected (Y threshold > X threshold)
            if (diffY > diffX && touchEndY > touchStartY && diffY > swipeThreshold) {
                console.log('↓ Swipe down detected - Refreshing...');
                refreshStatus();
            }
        }
        
        // Touch event listeners for swipe-to-refresh
        if (isTouchDevice()) {
            document.addEventListener('touchstart', (e) => {
                touchStartX = e.changedTouches[0].screenX;
                touchStartY = e.changedTouches[0].screenY;
            }, false);
            
            document.addEventListener('touchend', (e) => {
                touchEndX = e.changedTouches[0].screenX;
                touchEndY = e.changedTouches[0].screenY;
                handleSwipe();
            }, false);
        }
        
        // Adaptive polling for mobile networks
        function detectNetworkType() {
            if (navigator.connection) {
                const connection = navigator.connection;
                const type = connection.effectiveType;
                
                if (type === '4g') {
                    return { type: '4G', pollInterval: 30000 };
                } else if (type === '3g') {
                    return { type: '3G', pollInterval: 45000 };
                } else if (type === '2g') {
                    return { type: '2G', pollInterval: 60000 };
                } else if (type === 'slow-2g') {
                    return { type: 'Slow 2G', pollInterval: 90000 };
                }
            }
            return { type: 'Unknown', pollInterval: 30000 };
        }
        
        // Log mobile device info
        if (isTouchDevice()) {
            const network = detectNetworkType();
            console.log(`📱 Mobile device detected (${network.type})`);
            console.log('💡 Swipe down to refresh data');
        }
        
        // Orientation change handler
        window.addEventListener('orientationchange', () => {
            const orientation = window.innerHeight > window.innerWidth ? 'portrait' : 'landscape';
            console.log(`📐 Orientation changed to ${orientation}`);
            // Re-render on orientation change for proper responsive layout
            const statusGrid = document.getElementById('statusGrid');
            if (statusGrid && statusGrid.children.length > 0) {
                updateStatusViaREST();
            }
        });
        
        // Prevent accidental zooming on double-tap (mobile)
        let lastTouchEnd = 0;
        document.addEventListener('touchend', (e) => {
            const now = Date.now();
            if (now - lastTouchEnd <= 300) {
                e.preventDefault();
            }
            lastTouchEnd = now;
        }, false);
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
        
        /* ===================================================
           MOBILE RESPONSIVE ENHANCEMENTS (Notifications)
           =================================================== */
        
        /* Touch-friendly sizing */
        @media (max-width: 768px) {
            button {
                padding: 15px 20px;
                font-size: 1.1em;
                min-height: 44px;
                margin-right: 5px;
                margin-bottom: 10px;
            }
        }
        
        /* Small screens */
        @media (max-width: 600px) {
            body {
                padding: 10px;
                font-size: 14px;
            }
            
            h1 {
                font-size: 1.8em;
                margin-bottom: 20px;
            }
            
            .container {
                max-width: 100%;
            }
            
            .stats-grid {
                grid-template-columns: repeat(2, 1fr);
                gap: 15px;
                margin-bottom: 20px;
            }
            
            .stat-card {
                padding: 15px;
            }
            
            .stat-card h3 {
                font-size: 0.85em;
                margin-bottom: 8px;
                padding-bottom: 8px;
            }
            
            .stat-value {
                font-size: 2em;
            }
            
            .history-section {
                padding: 15px;
                margin-bottom: 15px;
            }
            
            .history-section h2 {
                font-size: 1.3em;
                margin-bottom: 15px;
                padding-bottom: 10px;
            }
            
            .notification-item {
                padding: 12px;
                margin-bottom: 12px;
            }
            
            .notification-system {
                font-size: 1.1em;
                margin-bottom: 6px;
            }
            
            .notification-item p {
                font-size: 0.9em;
                margin: 4px 0;
            }
            
            .button-group {
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                justify-content: center;
            }
            
            button {
                flex: 1;
                min-width: 120px;
            }
        }
        
        /* Extra small screens */
        @media (max-width: 360px) {
            h1 {
                font-size: 1.4em;
                margin-bottom: 15px;
            }
            
            body {
                padding: 8px;
            }
            
            .stats-grid {
                grid-template-columns: 1fr;
                gap: 10px;
            }
            
            .stat-card {
                padding: 12px;
            }
            
            .stat-value {
                font-size: 1.6em;
            }
            
            .button-group {
                flex-direction: column;
            }
            
            button {
                width: 100%;
            }
        }
        
        /* Landscape orientation */
        @media (max-width: 900px) and (orientation: landscape) {
            h1 {
                margin-bottom: 10px;
                font-size: 1.6em;
            }
            
            body {
                padding: 10px;
            }
            
            .stats-grid {
                grid-template-columns: repeat(4, 1fr);
                gap: 10px;
                margin-bottom: 15px;
            }
            
            .stat-card {
                padding: 10px;
            }
            
            .stat-card h3 {
                font-size: 0.8em;
                margin-bottom: 5px;
            }
            
            .stat-value {
                font-size: 1.5em;
            }
            
            .history-section {
                padding: 12px;
                max-height: 60vh;
                overflow-y: auto;
            }
        }
        
        /* Touch device optimizations */
        @media (hover: none) and (pointer: coarse) {
            button {
                padding: 16px 20px;
                margin-top: 15px;
            }
            
            button:active {
                background: #003300;
                box-shadow: 0 0 15px rgba(0, 255, 0, 0.7);
            }
        }
        
        /* Accessibility */
        @media (prefers-reduced-motion: reduce) {
            * {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
            }
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
        
        // =====================================================
        // MOBILE-SPECIFIC OPTIMIZATIONS (Notifications Page)
        // =====================================================
        
        // Detect if device is touch-enabled
        const isTouchDevice = () => {
            return (('ontouchstart' in window) ||
                    (navigator.maxTouchPoints > 0) ||
                    (navigator.msMaxTouchPoints > 0));
        };
        
        // Track touch gestures
        let touchStartX = 0;
        let touchEndX = 0;
        let touchStartY = 0;
        let touchEndY = 0;
        
        // Handle swipe to refresh notifications
        function handleSwipe() {
            const swipeThreshold = 50;
            const diffX = Math.abs(touchEndX - touchStartX);
            const diffY = Math.abs(touchEndY - touchStartY);
            
            // Swipe down detected
            if (diffY > diffX && touchEndY > touchStartY && diffY > swipeThreshold) {
                console.log('↓ Swipe down detected - Reloading notifications...');
                loadNotifications();
            }
        }
        
        // Touch event listeners
        if (isTouchDevice()) {
            document.addEventListener('touchstart', (e) => {
                touchStartX = e.changedTouches[0].screenX;
                touchStartY = e.changedTouches[0].screenY;
            }, false);
            
            document.addEventListener('touchend', (e) => {
                touchEndX = e.changedTouches[0].screenX;
                touchEndY = e.changedTouches[0].screenY;
                handleSwipe();
            }, false);
        }
        
        // Orientation change handler
        window.addEventListener('orientationchange', () => {
            const orientation = window.innerHeight > window.innerWidth ? 'portrait' : 'landscape';
            console.log(`📐 Notifications page orientation changed to ${orientation}`);
            // Re-layout on orientation change
            loadNotifications();
        });
        
        // Prevent accidental zooming on double-tap (mobile)
        let lastTouchEnd = 0;
        document.addEventListener('touchend', (e) => {
            const now = Date.now();
            if (now - lastTouchEnd <= 300) {
                e.preventDefault();
            }
            lastTouchEnd = now;
        }, false);
        
        // Log mobile device info
        if (isTouchDevice()) {
            console.log('📱 Mobile device detected');
            console.log('💡 Swipe down to refresh notifications');
        }
    </script>
</body>
</html>
"""


TIMELINE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HGE Timeline - Elite Dangerous</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js"></script>
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
        
        .timeline-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            gap: 20px;
            flex-wrap: wrap;
        }
        
        .timeline-nav {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .timeline-nav button {
            background: #001a00;
            border: 2px solid #00ff00;
            color: #00ff00;
            padding: 10px 15px;
            border-radius: 5px;
            cursor: pointer;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            transition: all 0.3s;
        }
        
        .timeline-nav button:hover {
            background: #003300;
            box-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
        }
        
        .timeline-nav button.active {
            background: #003300;
            box-shadow: 0 0 15px rgba(0, 255, 0, 0.8);
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: rgba(0, 50, 0, 0.3);
            border: 2px solid #00ff00;
            border-radius: 5px;
            padding: 15px;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.2);
        }
        
        .stat-card h3 {
            font-size: 0.9em;
            margin-bottom: 10px;
            color: #00cc00;
        }
        
        .stat-value {
            font-size: 1.5em;
            color: #ffff00;
            font-weight: bold;
        }
        
        .chart-container {
            background: rgba(0, 50, 0, 0.3);
            border: 2px solid #00ff00;
            border-radius: 5px;
            padding: 20px;
            margin-bottom: 30px;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.2);
        }
        
        .chart-title {
            margin-bottom: 20px;
            font-size: 1.3em;
            border-bottom: 1px solid #00ff00;
            padding-bottom: 10px;
        }
        
        .chart-wrapper {
            position: relative;
            height: 400px;
            margin-bottom: 20px;
        }
        
        .timeline-list {
            background: rgba(0, 50, 0, 0.3);
            border: 2px solid #00ff00;
            border-radius: 5px;
            padding: 20px;
            max-height: 600px;
            overflow-y: auto;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.2);
        }
        
        .timeline-list h3 {
            margin-bottom: 15px;
            font-size: 1.2em;
            color: #00cc00;
        }
        
        .timeline-entry {
            background: rgba(0, 30, 0, 0.5);
            border-left: 3px solid #00ff00;
            padding: 12px;
            margin-bottom: 10px;
            border-radius: 3px;
        }
        
        .timeline-entry .time {
            color: #00cc00;
            font-size: 0.9em;
            margin-bottom: 5px;
        }
        
        .timeline-entry .system {
            color: #ffff00;
            font-weight: bold;
            margin: 5px 0;
        }
        
        .timeline-entry .distance {
            color: #00ff00;
            font-size: 0.95em;
        }
        
        .entry-materials {
            color: #ffff00;
            font-size: 0.85em;
            margin-top: 8px;
            padding-top: 8px;
            border-top: 1px solid #00cc00;
            font-style: italic;
        }
        
        .empty-message {
            text-align: center;
            padding: 40px 20px;
            color: #ff6600;
        }
        
        .connection-status {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: rgba(0, 50, 0, 0.3);
            border: 2px solid #00ff00;
            padding: 10px 15px;
            border-radius: 5px;
            font-size: 0.9em;
        }
        
        .connection-status.connected {
            color: #00ff00;
        }
        
        .connection-status.disconnected {
            color: #ff6600;
        }
        
        .nav-link {
            display: inline-block;
            background: #001a00;
            border: 2px solid #00ff00;
            color: #00ff00;
            padding: 8px 15px;
            border-radius: 5px;
            text-decoration: none;
            margin-right: 10px;
            transition: all 0.3s;
        }
        
        .nav-link:hover {
            background: #003300;
            box-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
        }
        
        /* Chart.js theme customization */
        :root {
            --chart-color-primary: #00ff00;
            --chart-color-secondary: #ffff00;
            --chart-color-bg: rgba(0, 50, 0, 0.3);
        }
        
        /* Mobile responsive */
        @media (max-width: 768px) {
            h1 { font-size: 1.8em; }
            .stats-grid { grid-template-columns: repeat(2, 1fr); }
            .chart-wrapper { height: 300px; }
            .timeline-list { max-height: 400px; }
        }
        
        @media (max-width: 600px) {
            h1 { font-size: 1.4em; }
            body { padding: 10px; }
            .stats-grid { grid-template-columns: 1fr; }
            .timeline-header { flex-direction: column; }
            .chart-wrapper { height: 250px; }
            .timeline-list { max-height: 300px; }
            .timeline-nav { width: 100%; }
            .timeline-nav button { flex: 1; }
        }
        
        @media (max-width: 360px) {
            h1 { font-size: 1.2em; }
            .stat-card { padding: 10px; }
            .stat-value { font-size: 1.2em; }
        }
        
        @media (hover: none) and (pointer: coarse) {
            button {
                min-height: 44px;
                padding: 12px 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 HGE Detection Timeline</h1>
        
        <div class="timeline-header">
            <div class="timeline-nav">
                <button onclick="switchView('trends')">📈 Distance Trends</button>
                <button onclick="switchView('hourly')">⏱️ Hourly Distribution</button>
                <button onclick="switchView('list')">📋 Signal List</button>
            </div>
            <a href="/" class="nav-link">← Back to Dashboard</a>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Total Signals Detected</h3>
                <div class="stat-value" id="statTotal">0</div>
            </div>
            <div class="stat-card">
                <h3>Average Distance</h3>
                <div class="stat-value" id="statAvg">0 ly</div>
            </div>
            <div class="stat-card">
                <h3>Minimum Distance</h3>
                <div class="stat-value" id="statMin">0 ly</div>
            </div>
            <div class="stat-card">
                <h3>Maximum Distance</h3>
                <div class="stat-value" id="statMax">0 ly</div>
            </div>
        </div>
        
        <!-- Distance Trends Chart -->
        <div id="trendsView" class="chart-container">
            <div class="chart-title">📊 Distance Trends Over Time</div>
            <div class="chart-wrapper">
                <canvas id="trendsChart"></canvas>
            </div>
        </div>
        
        <!-- Hourly Distribution Chart -->
        <div id="hourlyView" class="chart-container" style="display: none;">
            <div class="chart-title">🕐 Hourly Signal Distribution</div>
            <div class="chart-wrapper">
                <canvas id="hourlyChart"></canvas>
            </div>
        </div>
        
        <!-- Timeline List -->
        <div id="listView" class="chart-container" style="display: none;">
            <div class="timeline-list">
                <h3>📍 Signal Detection History</h3>
                <div id="timelineListContainer"></div>
            </div>
        </div>
        
        <div class="connection-status" id="connectionStatus">
            <span id="statusText">🔌 Connecting...</span>
        </div>
    </div>
    
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <script>
        const statusEndpoint = "/api/status";
        const timelineEndpoint = "/api/timeline";
        const summaryEndpoint = "/api/timeline/summary";
        const trendsEndpoint = "/api/timeline/trends";
        
        let chart1 = null;
        let chart2 = null;
        let currentView = 'trends';
        let isConnected = false;
        
        const socket = io();
        
        socket.on('connect', () => {
            isConnected = true;
            updateConnectionStatus();
            console.log('✅ Timeline connected to WebSocket');
        });
        
        socket.on('disconnect', () => {
            isConnected = false;
            updateConnectionStatus();
            console.log('❌ Timeline disconnected from WebSocket');
        });
        
        socket.on('status', (data) => {
            console.log('📡 Status update received');
            loadTimelineData();
        });
        
        socket.on('hge_signal', (data) => {
            console.log('🔔 New signal received - updating timeline');
            loadTimelineData();
        });
        
        function updateConnectionStatus() {
            const statusEl = document.getElementById('connectionStatus');
            const textEl = document.getElementById('statusText');
            
            if (isConnected) {
                statusEl.className = 'connection-status connected';
                textEl.textContent = '🟢 Real-time connected';
            } else {
                statusEl.className = 'connection-status disconnected';
                textEl.textContent = '🟡 Polling fallback';
            }
        }
        
        function switchView(view) {
            currentView = view;
            
            // Update button states
            document.querySelectorAll('.timeline-nav button').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');
            
            // Hide all views
            document.getElementById('trendsView').style.display = 'none';
            document.getElementById('hourlyView').style.display = 'none';
            document.getElementById('listView').style.display = 'none';
            
            // Show selected view
            if (view === 'trends') {
                document.getElementById('trendsView').style.display = 'block';
                if (!chart1) loadTrendsChart();
            } else if (view === 'hourly') {
                document.getElementById('hourlyView').style.display = 'block';
                if (!chart2) loadHourlyChart();
            } else if (view === 'list') {
                document.getElementById('listView').style.display = 'block';
                loadTimelineList();
            }
        }
        
        async function loadTimelineData() {
            try {
                // Load summary stats
                const summaryResponse = await fetch(summaryEndpoint);
                const summaryData = await summaryResponse.json();
                
                if (summaryData.status === 'success') {
                    const stats = summaryData.data;
                    document.getElementById('statTotal').textContent = stats.total_signals;
                    document.getElementById('statAvg').textContent = stats.avg_distance.toFixed(2) + ' ly';
                    document.getElementById('statMin').textContent = stats.min_distance.toFixed(2) + ' ly';
                    document.getElementById('statMax').textContent = stats.max_distance.toFixed(2) + ' ly';
                }
                
                // Reload current view
                if (currentView === 'trends') {
                    loadTrendsChart();
                } else if (currentView === 'hourly') {
                    loadHourlyChart();
                } else if (currentView === 'list') {
                    loadTimelineList();
                }
            } catch (error) {
                console.error('Error loading timeline data:', error);
            }
        }
        
        async function loadTrendsChart() {
            try {
                const response = await fetch(trendsEndpoint);
                const data = await response.json();
                
                if (data.status !== 'success' || !data.data.length) {
                    document.getElementById('trendsChart').parentElement.innerHTML = '<div class="empty-message">No trend data available</div>';
                    return;
                }
                
                const trends = data.data;
                const labels = trends.map(t => new Date(t.timestamp).toLocaleString());
                const distances = trends.map(t => t.distance);
                
                // Destroy existing chart if present
                if (chart1) chart1.destroy();
                
                const ctx = document.getElementById('trendsChart');
                chart1 = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Distance (LY)',
                            data: distances,
                            borderColor: '#00ff00',
                            backgroundColor: 'rgba(0, 255, 0, 0.1)',
                            borderWidth: 2,
                            fill: true,
                            tension: 0.4,
                            pointBackgroundColor: '#ffff00',
                            pointBorderColor: '#00ff00',
                            pointRadius: 5,
                            pointHoverRadius: 7,
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { labels: { color: '#00ff00' } }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: { color: '#00ff00' },
                                grid: { color: 'rgba(0, 255, 0, 0.1)' },
                                title: { display: true, text: 'Distance (Light Years)', color: '#00ff00' }
                            },
                            x: {
                                ticks: { color: '#00ff00' },
                                grid: { color: 'rgba(0, 255, 0, 0.1)' }
                            }
                        }
                    }
                });
            } catch (error) {
                console.error('Error loading trends chart:', error);
            }
        }
        
        async function loadHourlyChart() {
            try {
                const response = await fetch(summaryEndpoint);
                const data = await response.json();
                
                if (data.status !== 'success') {
                    document.getElementById('hourlyChart').parentElement.innerHTML = '<div class="empty-message">No hourly data available</div>';
                    return;
                }
                
                const hourly = data.data.hourly_distribution || {};
                const labels = Object.keys(hourly).sort();
                const values = labels.map(hour => hourly[hour]);
                
                // Destroy existing chart if present
                if (chart2) chart2.destroy();
                
                const ctx = document.getElementById('hourlyChart');
                chart2 = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Signals per Hour',
                            data: values,
                            backgroundColor: '#00ff00',
                            borderColor: '#ffff00',
                            borderWidth: 2,
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { labels: { color: '#00ff00' } }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: { color: '#00ff00' },
                                grid: { color: 'rgba(0, 255, 0, 0.1)' }
                            },
                            x: {
                                ticks: { color: '#00ff00' },
                                grid: { color: 'rgba(0, 255, 0, 0.1)' }
                            }
                        }
                    }
                });
            } catch (error) {
                console.error('Error loading hourly chart:', error);
            }
        }
        
        async function loadTimelineList() {
            try {
                const response = await fetch(timelineEndpoint + '?limit=100');
                const data = await response.json();
                
                const container = document.getElementById('timelineListContainer');
                
                if (data.status !== 'success' || !data.data.length) {
                    container.innerHTML = '<div class="empty-message">No signal history available</div>';
                    return;
                }
                
                container.innerHTML = data.data.map(entry => {
                    // Build materials HTML
                    let materialsHtml = '';
                    if (entry.materials && entry.materials.count > 0) {
                        materialsHtml = `<div class="entry-materials">
                            💎 Possible Materials: ${entry.materials.materials.map(m => m.name).join(', ')}
                        </div>`;
                    }
                    
                    return `
                        <div class="timeline-entry">
                            <div class="time">⏰ ${new Date(entry.timestamp).toLocaleString()}</div>
                            <div class="system">🎯 ${entry.system_name}</div>
                            <div class="distance">📏 ${entry.distance_ly ? entry.distance_ly.toFixed(2) + ' ly' : 'Unknown'}</div>
                            ${materialsHtml}
                        </div>
                    `;
                }).join('');
            } catch (error) {
                console.error('Error loading timeline list:', error);
            }
        }
        
        // Initial load
        loadTimelineData();
        
        // Periodic refresh (only when disconnected)
        setInterval(() => {
            if (!isConnected) {
                loadTimelineData();
            }
        }, 30000);
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
        ws_manager = WebSocketManager(async_mode="asgi")
        manager.websocket_manager = ws_manager
    
    app = create_app(manager, ws_manager)
    manager.start()
    
    try:
        if ws_manager:
            # Use python-socketio with Flask via ASGIApp for async support
            from socketio import ASGIApp
            from asgiref.wsgi import WsgiToAsgi
            
            # Wrap Flask (WSGI) to ASGI
            flask_asgi = WsgiToAsgi(app)
            
            # Wrap with Socket.IO
            app_with_socketio = ASGIApp(ws_manager.sio, flask_asgi)
            
            import uvicorn
            uvicorn.run(app_with_socketio, host=host, port=port, log_level="info")
        else:
            app.run(host=host, port=port, debug=debug)
    finally:
        manager.stop()
        if ws_manager:
            ws_manager.close()
