#!/usr/bin/env python3
"""
Shellhorn Monitor - Watches for orphaned commands via MQTT.

Tracks commands that start but never finish (due to crashes, network issues, etc.)
and sends alerts when commands are detected as orphaned.
"""

import json
import os
import time
import logging
import threading
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

import paho.mqtt.client as mqtt
import requests
import yaml


# Configure logging
logging.basicConfig(
    level=logging.DEBUG if os.getenv('DEBUG') else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('shellhorn-monitor')


@dataclass
class ActiveCommand:
    """Represents an active command being monitored."""
    command: str
    client_id: str
    start_time: datetime
    pid: Optional[int] = None
    last_seen: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['start_time'] = self.start_time.isoformat()
        if self.last_seen:
            data['last_seen'] = self.last_seen.isoformat()
        return data

    @property
    def age_seconds(self) -> float:
        """Get age of command in seconds."""
        age = (datetime.now() - self.start_time).total_seconds()
        # Log if age is negative (indicates timestamp parsing issue)
        if age < 0:
            logger.warning(
                f"Negative age detected for command {self.command}: {age}s "
                f"(start_time: {self.start_time}, now: {datetime.now()})")
        return age

    def is_orphaned(self, timeout_minutes: int) -> bool:
        """Check if command is considered orphaned."""
        return self.age_seconds > (timeout_minutes * 60)


class ShellhornMonitor:
    """Monitors MQTT for shellhorn command lifecycle and detects orphans."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.active_commands: Dict[str, ActiveCommand] = {}
        self.mqtt_client = None
        self.running = False
        self.lock = threading.Lock()

    def load_secrets(self) -> Dict[str, Any]:
        """Load secrets from config or environment variables."""
        secrets = {}

        # First check if secrets are in the main config
        if 'secrets' in self.config:
            secrets = self.config['secrets'].copy()
            logger.debug("Loading secrets from config file")
        else:
            # Legacy: try to load from separate secrets file
            secrets_file = self.config.get('secrets_file')
            if secrets_file and os.path.exists(secrets_file):
                logger.info(f"Loading secrets from legacy file {secrets_file}")
                try:
                    with open(secrets_file, 'r') as f:
                        secrets = json.load(f)
                except Exception as e:
                    logger.error(f"Failed to load secrets file: {e}")

        # Environment variables always take precedence
        env_secrets = {
            'mqtt_username': os.getenv('MQTT_USERNAME'),
            'mqtt_password': os.getenv('MQTT_PASSWORD'),
            'pushover_token': os.getenv('PUSHOVER_TOKEN'),
            'pushover_user': os.getenv('PUSHOVER_USER'),
            'pushover_device': os.getenv('PUSHOVER_DEVICE'),
        }

        # Merge, preferring env vars over config/file
        for key, value in env_secrets.items():
            if value is not None:
                secrets[key] = value

        # Filter out empty values from config expansion
        secrets = {k: v for k, v in secrets.items() if v}

        return secrets

    def setup_mqtt(self):
        """Setup MQTT client connection."""
        secrets = self.load_secrets()

        client_id = self.config.get(
            'client_id', f"shellhorn-monitor-{int(time.time())}")
        self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,
                                       client_id=client_id,
                                       clean_session=False)

        # Authentication
        username = secrets.get('mqtt_username')
        password = secrets.get('mqtt_password')
        if username and password:
            self.mqtt_client.username_pw_set(username, password)
            logger.info(f"MQTT authentication configured for user: {username}")

        # Callbacks
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_disconnect = self.on_disconnect
        self.mqtt_client.on_message = self.on_message

        # Set reconnect delay
        self.mqtt_client.reconnect_delay_set(1, 30)

        # Set will message for offline status
        topic_prefix = self.config['mqtt']['topic_prefix']
        self.mqtt_client.will_set(
            f"{topic_prefix}/status",
            "offline",
            qos=1,
            retain=True)

        # Connect
        broker_host = self.config['mqtt']['broker_host']
        broker_port = self.config['mqtt']['broker_port']

        logger.info(f"Connecting to MQTT broker: {broker_host}:{broker_port}")
        self.mqtt_client.connect(broker_host, broker_port, 60)

    def on_connect(self, client, userdata, flags, rc, properties=None):
        """MQTT connection callback."""
        if rc == 0:
            logger.info("Connected to MQTT broker successfully")
            topic_prefix = self.config['mqtt']['topic_prefix']

            # Publish online status
            client.publish(f"{topic_prefix}/status", "online", qos=1, retain=True)

            topics = [
                f"{topic_prefix}/start",
                f"{topic_prefix}/complete",
                f"{topic_prefix}/error",
                f"{topic_prefix}/interrupt"
            ]
            for topic in topics:
                client.subscribe(topic, qos=1)
                logger.info(f"Subscribed to topic: {topic}")
        else:
            logger.error(f"Failed to connect to MQTT broker: {rc}")

    def on_disconnect(self, client, userdata, rc, properties=None):
        """MQTT disconnection callback."""
        # rc==0 means the client called disconnect() – expected
        if rc == 0:
            logger.info("Disconnected cleanly")
        else:
            logger.warning(f"Unexpected MQTT disconnection rc={rc}")

    def on_message(self, client, userdata, msg):
        """Handle incoming MQTT messages."""
        try:
            topic_parts = msg.topic.split('/')
            event_type = topic_parts[-1]  # start, complete, error, interrupt

            payload = json.loads(msg.payload.decode())
            command_key = f"{payload['client_id']}:{payload['command']}"

            with self.lock:
                if event_type == "start":
                    self.handle_command_start(command_key, payload)
                elif event_type in ["complete", "error", "interrupt"]:
                    self.handle_command_end(command_key, payload, event_type)

        except Exception as e:
            logger.error(f"Error processing message from {msg.topic}: {e}")

    def handle_command_start(self, command_key: str, payload: Dict[str, Any]):
        """Handle command start event."""
        # Parse timestamp - handle both ISO format and Unix timestamp
        timestamp_val = payload['timestamp']
        logger.debug(
            f"Received timestamp: {timestamp_val} (type: {type(timestamp_val)})")

        # Always use current time to avoid timezone issues
        # Log the received timestamp for debugging but use local time
        logger.debug(f"Received timestamp: {timestamp_val}, using local time instead")
        start_time = datetime.now()

        # This ensures commands are tracked correctly regardless of timezone mismatches

        command = ActiveCommand(
            command=payload['command'],
            client_id=payload['client_id'],
            start_time=start_time,
            pid=payload.get('pid'),
            last_seen=datetime.now()
        )

        self.active_commands[command_key] = command
        logger.info(
            f"Tracking new command: {command.command} (client: {command.client_id})")

        # Send notification for command start
        self.send_event_notification(command, "start")

    def handle_command_end(self, command_key: str,
                           payload: Dict[str, Any], event_type: str):
        """Handle command end event (complete/error/interrupt)."""
        if command_key in self.active_commands:
            command = self.active_commands.pop(command_key)
            duration = command.age_seconds
            logger.info(
                f"Command finished ({event_type}): {command.command} "
                f"after {duration:.2f}s")

            # Send notification for command completion
            if event_type == "complete":
                self.send_event_notification(command, "success", duration)
            else:  # error or interrupt
                self.send_event_notification(command, "fail", duration)
        else:
            logger.warning(
                f"Received {event_type} for unknown command: {payload.get('command')}")

    def check_orphaned_commands(self):
        """Check for orphaned commands and send alerts."""
        timeout_minutes = self.config['monitoring']['timeout_minutes']
        logger.debug(
            f"Checking for orphaned commands (timeout: {timeout_minutes} minutes)")

        with self.lock:
            orphaned = []
            for key, command in list(self.active_commands.items()):
                age_minutes = command.age_seconds / 60
                logger.debug(
                    f"Checking command {command.command}: age={age_minutes:.2f}m, "
                    f"timeout={timeout_minutes}m")
                if command.is_orphaned(timeout_minutes):
                    orphaned.append(command)
                    # Remove from active tracking after alerting
                    del self.active_commands[key]

        for command in orphaned:
            age_minutes = command.age_seconds / 60
            logger.warning(
                f"Orphaned command detected: {command.command} "
                f"(age: {age_minutes:.1f} minutes, started: {command.start_time})")
            logger.info(f"Sending lost command notification for: {command.command}")
            self.send_event_notification(command, "lost")

    def send_event_notification(
            self,
            command: ActiveCommand,
            event_type: str,
            duration: float = None):
        """Send notification for command events."""
        # Check if notifications are enabled for this event type
        enabled_events = self.config.get('notifications', {}).get('enabled_events', {})
        if not enabled_events.get(event_type, False):
            logger.debug(f"Notification for event type '{event_type}' is disabled")
            return

        logger.debug(
            f"Processing {event_type} notification for command: {command.command}")

        secrets = self.load_secrets()
        pushover_config = self.config.get('notifications', {}).get('pushover', {})

        if not pushover_config.get('enabled', False):
            return

        pushover_token = secrets.get('pushover_token')
        pushover_user = secrets.get('pushover_user')

        if not (pushover_token and pushover_user):
            logger.warning(
                f"Pushover credentials not configured "
                f"(token: {bool(pushover_token)}, user: {bool(pushover_user)}), "
                f"skipping notification")
            logger.debug(f"Available secrets keys: {list(secrets.keys())}")
            return

        logger.debug(f"Pushover credentials found, sending {event_type} notification")

        # Build message based on event type
        message_templates = pushover_config.get('messages', {})
        base_message = message_templates.get(
            event_type, f"Command {event_type}: {{command}}")

        # Format message with command details
        message_vars = {
            'command': command.command,
            'client_id': command.client_id,
            'start_time': command.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'pid': command.pid or 'Unknown'
        }

        if event_type == "lost":
            age_minutes = command.age_seconds / 60
            message_vars.update({
                'age_minutes': f"{age_minutes:.1f}",
                'age_seconds': f"{command.age_seconds:.0f}"
            })
            message = f"{base_message.format(**message_vars)}\n\n" \
                f"Client: {command.client_id}\n" \
                f"Started: {command.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n" \
                f"Age: {age_minutes:.1f} minutes\n" \
                f"PID: {command.pid or 'Unknown'}\n\n" \
                f"Host may have disconnected or shut down unexpectedly."
        elif duration is not None:
            message_vars['duration'] = f"{duration:.2f}s"
            message = f"{base_message.format(**message_vars)}\n" \
                f"Duration: {duration:.2f}s\n" \
                f"Client: {command.client_id}"
        else:
            message = f"{base_message.format(**message_vars)}\n" \
                f"Client: {command.client_id}"

        # Get priority for this event type
        priority = pushover_config.get('priority', {}).get(event_type, 0)

        try:
            self.send_pushover_alert(
                pushover_token,
                pushover_user,
                secrets.get('pushover_device'),
                message,
                priority,
                event_type)
            logger.info(
                f"Pushover {event_type} notification sent for command: "
                f"{command.command}")
        except Exception as e:
            logger.error(f"Failed to send Pushover {event_type} notification: {e}")

    def send_pushover_alert(self, token: str, user: str, device: Optional[str],
                            message: str, priority: int = 0, event_type: str = 'alert'):
        """Send Pushover notification."""
        title_map = {
            'start': '🚀 Shellhorn: Command Started',
            'success': '✅ Shellhorn: Command Completed',
            'fail': '❌ Shellhorn: Command Failed',
            'lost': '🚨 Shellhorn: Lost Command Alert'
        }

        data = {
            'token': token,
            'user': user,
            'message': message,
            'title': title_map.get(event_type, '🐚📯 Shellhorn Monitor Alert'),
            'priority': priority,
        }

        # For emergency priority, add retry and expire
        if priority == 2:
            emergency_config = self.config.get(
                'notifications',
                {}).get(
                'pushover',
                {}).get(
                'emergency',
                {})
            data['retry'] = emergency_config.get(
                'retry', 60)        # Default: retry every 60 seconds
            data['expire'] = emergency_config.get(
                'expire', 3600)    # Default: stop after 1 hour

        if device:
            data['device'] = device

        response = requests.post('https://api.pushover.net/1/messages.json',
                                 data=data, timeout=10)
        response.raise_for_status()

    def status_report(self):
        """Generate status report."""
        with self.lock:
            active_count = len(self.active_commands)

            if active_count > 0:
                logger.info(f"Currently monitoring {active_count} active command(s):")
                for _key, command in self.active_commands.items():
                    age_seconds = command.age_seconds
                    age_minutes = age_seconds / 60
                    # Show both age and start time for debugging
                    logger.info(
                        f"  - {command.command} (age: {age_minutes:.1f}m, "
                        f"started: {command.start_time}, age_sec: {age_seconds:.1f})")
            else:
                logger.info("No active commands being monitored")

    def publish_heartbeat(self):
        """Publish monitor status/heartbeat to MQTT."""
        with self.lock:
            active_count = len(self.active_commands)

            # Create status message
            status_data = {
                'timestamp': datetime.now().isoformat(),
                'active_commands': active_count,
                'uptime_seconds': (
                    round(time.time() - self.start_time)
                    if hasattr(self, 'start_time') else 0),
                'monitor_id': self.config.get(
                    'client_id',
                    'shellhorn-monitor'),
                'commands': []}

            # Add command details
            for _key, command in self.active_commands.items():
                age_minutes = command.age_seconds / 60
                status_data['commands'].append({
                    'command': command.command,
                    'client_id': command.client_id,
                    'age_minutes': round(age_minutes, 1),
                    'start_time': command.start_time.isoformat(),
                    'pid': command.pid
                })

            # Publish heartbeat to MQTT
            topic_prefix = self.config['mqtt']['topic_prefix']
            try:
                self.mqtt_client.publish(f"{topic_prefix}/monitor/heartbeat",
                                         json.dumps(status_data), qos=1, retain=True)
                logger.debug(f"Published heartbeat: {active_count} active commands")
            except Exception as e:
                logger.error(f"Failed to publish heartbeat: {e}")

    def run(self):
        """Main monitoring loop."""
        logger.info("Starting Shellhorn Monitor")
        self.start_time = time.time()

        # Setup MQTT
        self.setup_mqtt()

        # Start MQTT client
        self.mqtt_client.loop_start()
        self.running = True

        check_interval = self.config['monitoring']['check_interval_seconds']
        status_interval = self.config['monitoring']['status_interval_seconds']
        heartbeat_interval = self.config['monitoring'].get(
            'heartbeat_interval_seconds', 60)

        last_status_report = time.time()
        last_heartbeat = time.time()

        try:
            while self.running:
                time.sleep(check_interval)

                # Check for orphaned commands
                self.check_orphaned_commands()

                # Periodic console status report
                if time.time() - last_status_report > status_interval:
                    self.status_report()
                    last_status_report = time.time()

                # Periodic MQTT heartbeat
                if time.time() - last_heartbeat > heartbeat_interval:
                    self.publish_heartbeat()
                    last_heartbeat = time.time()

        except KeyboardInterrupt:
            logger.info("Received interrupt signal, shutting down...")
        finally:
            self.running = False
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
            logger.info("Shellhorn Monitor stopped")


def expand_env_vars(config: Any) -> Any:
    """Recursively expand environment variables in config values."""
    if isinstance(config, dict):
        return {key: expand_env_vars(value) for key, value in config.items()}
    elif isinstance(config, list):
        return [expand_env_vars(item) for item in config]
    elif isinstance(config, str):
        # Simple ${VAR:-default} expansion
        import re

        def replace_env(match):
            var_expr = match.group(1)
            if ':-' in var_expr:
                var_name, default = var_expr.split(':-', 1)
                return os.getenv(var_name.strip(), default.strip())
            else:
                return os.getenv(var_expr.strip(), '')
        return re.sub(r'\$\{([^}]+)\}', replace_env, config)
    else:
        return config


def load_config() -> Dict[str, Any]:
    """Load configuration from YAML/JSON file or use defaults."""
    # Try YAML first, then JSON, then use defaults
    config_paths = [
        os.getenv('SHELLHORN_MONITOR_CONFIG'),
        '/config/monitor.yaml',
        '/config/config.yaml',
        '/config/config.json'
    ]

    default_config = {
        'mqtt': {
            'broker_host': os.getenv('MQTT_BROKER', 'localhost'),
            'broker_port': int(os.getenv('MQTT_PORT', '1883')),
            'topic_prefix': os.getenv('MQTT_TOPIC_PREFIX', 'shellhorn')
        },
        'monitoring': {
            'timeout_minutes': int(os.getenv('SHELLHORN_TIMEOUT_MINUTES', '30')),
            'check_interval_seconds': int(os.getenv('SHELLHORN_CHECK_INTERVAL', '60')),
            'status_interval_seconds': int(
                os.getenv('SHELLHORN_STATUS_INTERVAL', '300')),
            'heartbeat_interval_seconds': int(
                os.getenv('SHELLHORN_HEARTBEAT_INTERVAL', '60'))
        },
        'notifications': {
            'enabled_events': {
                'start': False,
                'success': False,
                'fail': True,
                'lost': True
            },
            'pushover': {
                'enabled': True,
                'priority': {
                    'start': 0,
                    'success': 0,
                    'fail': 1,
                    'lost': 2
                },
                'messages': {
                    'start': '🚀 Command started: {command}',
                    'success': '✅ Command completed: {command}',
                    'fail': '❌ Command failed: {command}',
                    'lost': '🚨 Lost command detected: {command} (host may be down)'
                }
            }
        },
        'client_id': os.getenv('SHELLHORN_CLIENT_ID', f'shellhorn-monitor-{int(time.time())}'),
        'secrets_file': os.getenv('SHELLHORN_SECRETS_FILE')  # Legacy support only
    }

    # Try to load config file (prefer YAML)
    config_file = None
    for path in config_paths:
        if path and os.path.exists(path):
            config_file = path
            break

    if config_file:
        logger.info(f"Loading configuration from {config_file}")
        try:
            with open(config_file, 'r') as f:
                if config_file.endswith(('.yaml', '.yml')):
                    file_config = yaml.safe_load(f)
                else:
                    file_config = json.load(f)

                if file_config:
                    # Expand environment variables
                    file_config = expand_env_vars(file_config)

                    # Deep merge file config with defaults
                    def deep_merge(base: dict, update: dict) -> dict:
                        for key, value in update.items():
                            if key in base and isinstance(
                                    base[key],
                                    dict) and isinstance(
                                    value,
                                    dict):
                                base[key] = deep_merge(base[key], value)
                            else:
                                base[key] = value
                        return base

                    default_config = deep_merge(default_config, file_config)
        except Exception as e:
            logger.error(f"Failed to load config file: {e}")
            logger.info("Using default configuration")
    else:
        logger.info("No config file found, using defaults")

    return default_config


def main():
    """Main entry point."""
    config = load_config()
    monitor = ShellhornMonitor(config)
    monitor.run()


if __name__ == '__main__':
    main()
