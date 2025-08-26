"""
Configuration management for shellhorn.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from .notifiers import PushoverNotifier, MQTTNotifier, ConsoleNotifier


class Config:
    """Manages shellhorn configuration."""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._get_default_config_path()
        self._config = self._load_config()

    def _get_default_config_path(self) -> str:
        """Get the default configuration file path."""
        home = Path.home()
        config_dir = home / ".config" / "shellhorn"
        config_dir.mkdir(parents=True, exist_ok=True)
        return str(config_dir / "config.json")

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if not os.path.exists(self.config_path):
            return self._get_default_config()

        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"🐚📯 shellhorn: Warning - Could not load config: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "notifications": {
                "pushover": {
                    "enabled": False,
                    "app_token": "",
                    "user_key": "",
                    "device": None
                },
                "mqtt": {
                    "enabled": False,
                    "broker_host": "localhost",
                    "broker_port": 1883,
                    "topic_prefix": "shellhorn",
                    "username": None,
                    "password": None
                },
                "console": {
                    "enabled": False
                }
            },
            "preferences": {
                "notify_start": False,
                "notify_success": True,
                "notify_failure": True,
                "notify_error": True,
                "notify_interrupted": True
            },
            "default_notifications": ["console"]
        }

    def save(self):
        """Save current configuration to file."""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self._config, f, indent=2)

    def get_notifiers(self):
        """Get configured notifiers."""
        notifiers = []

        # Pushover
        pushover_config = self._config["notifications"]["pushover"]
        if (pushover_config["enabled"]
                and pushover_config["app_token"]
                and pushover_config["user_key"]):
            notifiers.append(PushoverNotifier(
                app_token=pushover_config["app_token"],
                user_key=pushover_config["user_key"],
                device=pushover_config.get("device")
            ))

        # MQTT
        mqtt_config = self._config["notifications"]["mqtt"]
        if mqtt_config["enabled"] and mqtt_config["broker_host"]:
            notifiers.append(MQTTNotifier(
                broker_host=mqtt_config["broker_host"],
                broker_port=mqtt_config["broker_port"],
                topic_prefix=mqtt_config["topic_prefix"],
                username=mqtt_config.get("username"),
                password=mqtt_config.get("password")
            ))

        # Console
        console_config = self._config["notifications"]["console"]
        if console_config["enabled"]:
            notifiers.append(ConsoleNotifier())

        # If no notifiers are configured but console is in defaults, add it
        if (not notifiers and "console" in
                self._config.get("default_notifications", [])):
            notifiers.append(ConsoleNotifier())

        return notifiers

    def set_pushover(self, app_token: str, user_key: str,
                     device: Optional[str] = None, enabled: bool = True):
        """Configure Pushover notifications."""
        self._config["notifications"]["pushover"] = {
            "enabled": enabled,
            "app_token": app_token,
            "user_key": user_key,
            "device": device
        }

    def set_mqtt(self, broker_host: str, broker_port: int = 1883,
                 topic_prefix: str = "shellhorn", username: Optional[str] = None,
                 password: Optional[str] = None, enabled: bool = True):
        """Configure MQTT notifications."""
        self._config["notifications"]["mqtt"] = {
            "enabled": enabled,
            "broker_host": broker_host,
            "broker_port": broker_port,
            "topic_prefix": topic_prefix,
            "username": username,
            "password": password
        }

    def enable_console(self, enabled: bool = True):
        """Enable/disable console notifications."""
        self._config["notifications"]["console"]["enabled"] = enabled

    def get_notification_preferences(self) -> Dict[str, bool]:
        """Get notification preferences."""
        return self._config.get("preferences", {
            "notify_start": False,
            "notify_success": True,
            "notify_failure": True,
            "notify_error": True,
            "notify_interrupted": True
        })

    @property
    def config(self) -> Dict[str, Any]:
        """Get current configuration."""
        return self._config.copy()


def get_config_from_env() -> Config:
    """Create config from environment variables."""
    config = Config()

    # Pushover from environment
    pushover_token = os.getenv("SHELLHORN_PUSHOVER_TOKEN")
    pushover_user = os.getenv("SHELLHORN_PUSHOVER_USER")
    pushover_device = os.getenv("SHELLHORN_PUSHOVER_DEVICE")

    if pushover_token and pushover_user:
        config.set_pushover(pushover_token, pushover_user, pushover_device)

    # MQTT from environment
    mqtt_broker = os.getenv("SHELLHORN_MQTT_BROKER")
    mqtt_port = int(os.getenv("SHELLHORN_MQTT_PORT", "1883"))
    mqtt_topic = os.getenv("SHELLHORN_MQTT_TOPIC", "shellhorn")
    mqtt_username = os.getenv("SHELLHORN_MQTT_USERNAME")
    mqtt_password = os.getenv("SHELLHORN_MQTT_PASSWORD")

    if mqtt_broker:
        config.set_mqtt(mqtt_broker, mqtt_port, mqtt_topic,
                        mqtt_username, mqtt_password)

    # Console notifications
    console_enabled = os.getenv(
        "SHELLHORN_CONSOLE_NOTIFICATIONS", "false").lower() == "true"
    config.enable_console(console_enabled)

    return config
