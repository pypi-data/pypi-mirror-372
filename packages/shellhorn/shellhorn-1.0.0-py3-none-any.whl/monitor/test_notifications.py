#!/usr/bin/env python3
"""
Test script for Shellhorn Monitor notifications
"""
import sys
import os
from datetime import datetime

# Add current directory to path for imports  # noqa: E402
sys.path.append(os.path.dirname(__file__))  # noqa: E402

# Import project modules  # noqa: E402
from shellhorn_monitor import ShellhornMonitor, ActiveCommand, load_config  # noqa: E402


def test_notifications():
    """Test different notification types"""
    config = load_config()
    ShellhornMonitor(config)

    # Create a test command
    ActiveCommand(
        command="test -f /some/file.txt",
        client_id="test_client_123",
        start_time=datetime.now(),
        pid=12345
    )

    print("Testing notification system...")
    print(f"Config loaded: {config['notifications']}")

    # Test each notification type
    notification_types = ['start', 'success', 'fail', 'lost']

    for event_type in notification_types:
        enabled = config['notifications']['enabled_events'].get(event_type, False)
        print(f"\n{event_type.upper()} notifications: "
              f"{'ENABLED' if enabled else 'DISABLED'}")

        if enabled:
            priority = config['notifications']['pushover']['priority'].get(
                event_type, 0)
            message = config['notifications']['pushover']['messages'].get(
                event_type)
            print(f"  Priority: {priority}")
            print(f"  Message template: {message}")

            # Uncomment to actually send test notification
            # monitor.send_event_notification(test_command, event_type)


if __name__ == "__main__":
    test_notifications()
