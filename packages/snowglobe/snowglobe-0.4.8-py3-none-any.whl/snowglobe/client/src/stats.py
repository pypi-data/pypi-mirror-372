"""
Shared statistics tracking for Snowglobe client.
This module avoids circular imports by providing a neutral location
for stats that both app.py and cli.py need to access.
"""

import datetime

# Tracking state
ui_stats = {
    "last_activity_time": None,
    "start_time": None,
    "total_messages": 0,
    "experiment_totals": {},  # experiment_name -> total_count
}


def initialize_stats():
    """Initialize stats tracking when server starts"""
    ui_stats["start_time"] = datetime.datetime.now()


def track_batch_completion(experiment_name: str, count: int):
    """Track completed batch of scenarios"""
    ui_stats["total_messages"] += count
    if experiment_name not in ui_stats["experiment_totals"]:
        ui_stats["experiment_totals"][experiment_name] = 0
    ui_stats["experiment_totals"][experiment_name] += count
    ui_stats["last_activity_time"] = datetime.datetime.now()


def get_shutdown_stats():
    """Get stats for graceful shutdown summary"""
    if not ui_stats["start_time"]:
        return None

    uptime = datetime.datetime.now() - ui_stats["start_time"]
    hours = int(uptime.total_seconds() // 3600)
    minutes = int((uptime.total_seconds() % 3600) // 60)
    seconds = int(uptime.total_seconds() % 60)

    if hours > 0:
        uptime_str = f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        uptime_str = f"{minutes}m {seconds}s"
    else:
        uptime_str = f"{seconds}s"

    return {
        "total_messages": ui_stats["total_messages"],
        "experiment_totals": ui_stats["experiment_totals"],
        "uptime": uptime_str,
    }
