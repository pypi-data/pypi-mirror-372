"""
Command-line interface for shellhorn.
"""

import sys
import argparse
from typing import List
from .core import CommandRunner
from .config import Config, get_config_from_env


def create_argument_parser():
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog='shellhorn',
        description='A lightweight command wrapper with notification and monitoring',
        add_help=False  # We'll handle help manually
    )

    parser.add_argument('--help', action='help', help='Show this help message and exit')
    parser.add_argument('--version', action='store_true',
                        help='Show version information')
    parser.add_argument('-c', '--config', help='Path to configuration file')
    parser.add_argument('--pushover-token', help='Pushover app token')
    parser.add_argument('--pushover-user', help='Pushover user key')
    parser.add_argument('--pushover-device', help='Pushover device name')
    parser.add_argument('--mqtt-broker', help='MQTT broker host')
    parser.add_argument('--mqtt-port', type=int, default=1883, help='MQTT broker port')
    parser.add_argument('--mqtt-topic', default='shellhorn', help='MQTT topic prefix')
    parser.add_argument('--mqtt-username', help='MQTT username')
    parser.add_argument('--mqtt-password', help='MQTT password')
    parser.add_argument('--console-notifications', action='store_true',
                        help='Enable console notifications')

    return parser


def handle_config_subcommand(args: List[str]):
    """Handle config subcommands."""
    if not args:
        print("Usage: shellhorn config {show,set,test}")
        return

    subcommand = args[0]

    if subcommand == "show":
        config = Config()
        print("Current configuration:")
        import json
        print(json.dumps(config.config, indent=2))

    elif subcommand == "set":
        if len(args) < 3:
            print("Usage: shellhorn config set KEY VALUE")
            return

        key, value = args[1], args[2]
        config = Config()

        # Parse the key path
        keys = key.split('.')
        current = config._config

        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        # Set the value, handling type conversion
        final_key = keys[-1]
        if value.lower() == 'true':
            current[final_key] = True
        elif value.lower() == 'false':
            current[final_key] = False
        elif value.lower() == 'null':
            current[final_key] = None
        elif value.isdigit():
            current[final_key] = int(value)
        else:
            current[final_key] = value

        config.save()
        print(f"Set {key} = {value}")

    elif subcommand == "test":
        config = Config()
        notifiers = config.get_notifiers()

        if not notifiers:
            print("No notifiers configured")
            return

        print(f"Testing {len(notifiers)} notifier(s)...")

        for notifier in notifiers:
            try:
                notifier.notify_success("shellhorn config test", 1.23, 0)
                print(f"✓ {type(notifier).__name__} - OK")
            except Exception as e:
                print(f"✗ {type(notifier).__name__} - ERROR: {e}")

    else:
        print(f"Unknown config subcommand: {subcommand}")
        print("Available: show, set, test")


def main():
    """Main entry point."""
    # Handle special cases first
    if len(sys.argv) > 1:
        if sys.argv[1] == '--version':
            from . import __version__
            print(f"shellhorn version {__version__}")
            return

        if sys.argv[1] == 'config':
            handle_config_subcommand(sys.argv[2:])
            return

    # Parse arguments, but be lenient about unknown args (they're the command to run)
    parser = create_argument_parser()

    # Find where options end and command begins
    options_end = len(sys.argv)
    for i, arg in enumerate(sys.argv[1:], 1):
        if not arg.startswith('-'):
            # Check if this is a known shellhorn subcommand
            if arg in ['config', 'version']:
                break
            options_end = i
            break

    # Parse known options
    try:
        args, unknown = parser.parse_known_intermixed_args(sys.argv[1:options_end])
        command_args = sys.argv[options_end:] + unknown
    except SystemExit:
        # argparse called sys.exit (help or version), re-raise
        raise
    except Exception:
        # If parsing fails, assume everything after the first non-option is the command
        args = parser.parse_args([])  # Default values
        command_args = sys.argv[1:]

    # If no command provided, show help
    if not command_args:
        parser.print_help()
        return

    # Create config from environment and override with CLI options
    config = Config(args.config) if args.config else get_config_from_env()

    # Override with CLI options
    if args.pushover_token and args.pushover_user:
        config.set_pushover(args.pushover_token, args.pushover_user,
                            args.pushover_device)

    if args.mqtt_broker:
        config.set_mqtt(args.mqtt_broker, args.mqtt_port, args.mqtt_topic,
                        args.mqtt_username, args.mqtt_password)

    if args.console_notifications:
        config.enable_console(True)

    # Get notifiers and run command
    notifiers = config.get_notifiers()
    preferences = config.get_notification_preferences()
    runner = CommandRunner(command_args, notifiers, preferences)
    exit_code = runner.run()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
