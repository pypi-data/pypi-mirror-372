"""
Notification implementations for various services.
"""

import json
import requests
import paho.mqtt.client as mqtt
from datetime import datetime
from typing import Optional, Dict, Any
from .core import BaseNotifier


class PushoverNotifier(BaseNotifier):
    """Sends notifications via Pushover."""

    def __init__(self, app_token: str, user_key: str, device: Optional[str] = None):
        self.app_token = app_token
        self.user_key = user_key
        self.device = device
        self.api_url = "https://api.pushover.net/1/messages.json"

    def _send_notification(self, message: str, title: str, priority: int = 0):
        """Send a notification to Pushover."""
        data = {
            "token": self.app_token,
            "user": self.user_key,
            "message": message,
            "title": title,
            "priority": priority,
        }

        if self.device:
            data["device"] = self.device

        try:
            response = requests.post(self.api_url, data=data, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            raise Exception(f"Pushover notification failed: {e}")

    def notify_start(self, command: str, pid: int):
        """Notify about command start."""
        message = f"Command started: {command}\nPID: {pid}"
        self._send_notification(message, "🐚📯 Shellhorn: Command Started")

    def notify_success(self, command: str, duration: float, return_code: int):
        """Notify about successful completion."""
        message = f"Command completed successfully in {duration:.2f}s\n{command}"
        self._send_notification(message, "🐚📯 Shellhorn: Success")

    def notify_failure(self, command: str, return_code: int, duration: float):
        """Notify about command failure."""
        message = (f"Command failed (exit code {return_code}) "
                   f"after {duration:.2f}s\n{command}")
        self._send_notification(message, "🐚📯 Shellhorn: Failed", priority=1)

    def notify_error(self, command: str, error: str):
        """Notify about unexpected errors."""
        message = f"Unexpected error: {error}\nCommand: {command}"
        self._send_notification(message, "🐚📯 Shellhorn: Error", priority=1)

    def notify_interrupted(self, command: str, duration: float):
        """Notify about command interruption."""
        message = f"Command interrupted after {duration:.2f}s\n{command}"
        self._send_notification(message, "🐚📯 Shellhorn: Interrupted", priority=1)


class MQTTNotifier(BaseNotifier):
    """Publishes command status to MQTT for centralized monitoring."""

    def __init__(self, broker_host: str, broker_port: int = 1883,
                 topic_prefix: str = "shellhorn", username: Optional[str] = None,
                 password: Optional[str] = None, client_id: Optional[str] = None):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.topic_prefix = topic_prefix
        self.username = username
        self.password = password
        self.client_id = client_id or f"shellhorn_{datetime.now().timestamp()}"
        self._is_status_publisher = True  # Mark as status publisher, not notifier

    def _publish(self, topic_suffix: str, payload: Dict[str, Any]):
        """Publish a message to MQTT."""
        client = mqtt.Client(client_id=self.client_id)

        if self.username and self.password:
            client.username_pw_set(self.username, self.password)

        try:
            client.connect(self.broker_host, self.broker_port, 60)
            topic = f"{self.topic_prefix}/{topic_suffix}"
            message = json.dumps({
                **payload,
                "timestamp": datetime.now().isoformat(),
                "client_id": self.client_id
            })

            client.publish(topic, message, qos=1)
            client.disconnect()
        except Exception as e:
            raise Exception(f"MQTT publish failed: {e}")

    def notify_start(self, command: str, pid: int):
        """Publish command start to MQTT."""
        self._publish("start", {
            "command": command,
            "pid": pid,
            "status": "started"
        })

    def notify_success(self, command: str, duration: float, return_code: int):
        """Publish successful completion to MQTT."""
        self._publish("complete", {
            "command": command,
            "duration": duration,
            "return_code": return_code,
            "status": "success"
        })

    def notify_failure(self, command: str, return_code: int, duration: float):
        """Publish command failure to MQTT."""
        self._publish("complete", {
            "command": command,
            "return_code": return_code,
            "duration": duration,
            "status": "failed"
        })

    def notify_error(self, command: str, error: str):
        """Publish unexpected errors to MQTT."""
        self._publish("error", {
            "command": command,
            "error": error,
            "status": "error"
        })

    def notify_interrupted(self, command: str, duration: float):
        """Publish command interruption to MQTT."""
        self._publish("interrupt", {
            "command": command,
            "duration": duration,
            "status": "interrupted"
        })


class ConsoleNotifier(BaseNotifier):
    """Simple console output notifier for debugging."""

    def notify_start(self, command: str, pid: int):
        print(f"[NOTIFIER] Started: {command} (PID: {pid})")

    def notify_success(self, command: str, duration: float, return_code: int):
        print(f"[NOTIFIER] Success: {command} ({duration:.2f}s)")

    def notify_failure(self, command: str, return_code: int, duration: float):
        print(f"[NOTIFIER] Failed: {command} (code: {return_code}, {duration:.2f}s)")

    def notify_error(self, command: str, error: str):
        print(f"[NOTIFIER] Error: {command} - {error}")

    def notify_interrupted(self, command: str, duration: float):
        print(f"[NOTIFIER] Interrupted: {command} ({duration:.2f}s)")
