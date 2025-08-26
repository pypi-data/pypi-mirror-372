#!/usr/bin/env python3
"""
Simple integration tests for Shellhorn Monitor with proper mocking.
"""

import json
import time
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, Mock
import os
import sys

# Add paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'monitor'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shellhorn'))

from shellhorn_monitor import ShellhornMonitor, ActiveCommand


class TestShellhornMonitorIntegration(unittest.TestCase):
    """Integration tests for Shellhorn Monitor with proper mocking."""
    
    def setUp(self):
        """Set up test environment."""
        self.config = {
            'mqtt': {
                'broker_host': 'localhost',
                'broker_port': 1883,
                'topic_prefix': 'test_shellhorn'
            },
            'monitoring': {
                'timeout_minutes': 1,
                'check_interval_seconds': 1,
                'status_interval_seconds': 10
            },
            'notifications': {
                'enabled_events': {
                    'start': True,
                    'success': True,
                    'fail': True,
                    'lost': True
                },
                'pushover': {
                    'enabled': True,
                    'priority': {'start': 0, 'success': 0, 'fail': 1, 'lost': 2},
                    'messages': {
                        'start': 'Command started: {command}',
                        'success': 'Command completed: {command}',
                        'fail': 'Command failed: {command}',
                        'lost': 'Lost command: {command}'
                    }
                }
            },
            'client_id': 'test-monitor'
        }
        
        self.monitor = ShellhornMonitor(self.config)
    
    def test_config_loading(self):
        """Test that configuration is loaded correctly."""
        self.assertEqual(
            self.monitor.config['mqtt']['topic_prefix'],
            'test_shellhorn'
        )
        self.assertEqual(
            self.monitor.config['monitoring']['timeout_minutes'], 
            1
        )
    
    def test_active_command_tracking(self):
        """Test basic command tracking without MQTT."""
        # Create a test command directly
        command = ActiveCommand(
            command='test command',
            client_id='test-client',
            start_time=datetime.now(),
            pid=12345
        )
        
        # Add to monitor's tracking
        command_key = f"{command.client_id}:{command.command}"
        self.monitor.active_commands[command_key] = command
        
        # Verify it's tracked
        self.assertEqual(len(self.monitor.active_commands), 1)
        self.assertIn(command_key, self.monitor.active_commands)
        
        # Test command age calculation
        age = command.age_seconds
        self.assertGreaterEqual(age, 0)
        self.assertLess(age, 1)  # Should be very recent
    
    def test_orphan_detection_logic(self):
        """Test orphan detection without MQTT."""
        # Create an old command
        old_time = datetime.now() - timedelta(minutes=2)
        command = ActiveCommand(
            command='old command',
            client_id='test-client',
            start_time=old_time,
            pid=12345
        )
        
        # Add to tracking
        command_key = f"{command.client_id}:{command.command}"
        self.monitor.active_commands[command_key] = command
        
        # Mock the notification method to avoid actual HTTP calls
        with patch.object(self.monitor, 'send_event_notification') as mock_notify:
            # Run orphan check
            self.monitor.check_orphaned_commands()
            
            # Verify orphan was detected and notification was sent
            mock_notify.assert_called_once()
            args, kwargs = mock_notify.call_args
            self.assertEqual(args[1], 'lost')  # event_type
    
    @patch('shellhorn_monitor.ShellhornMonitor.load_secrets')
    def test_notification_preferences(self, mock_load_secrets):
        """Test notification preference handling."""
        # Mock secrets
        mock_load_secrets.return_value = {
            'pushover_token': 'test_token',
            'pushover_user': 'test_user'
        }
        
        command = ActiveCommand(
            command='test command',
            client_id='test-client',
            start_time=datetime.now(),
            pid=12345
        )
        
        # Test that notification checks preferences
        with patch('requests.post') as mock_post:
            mock_post.return_value.raise_for_status = Mock()
            
            # Test success notification (should be enabled)
            self.monitor.send_event_notification(command, 'success', 1.5)
            mock_post.assert_called_once()
            
            # Reset mock
            mock_post.reset_mock()
            
            # Disable success notifications
            self.monitor.config['notifications']['enabled_events']['success'] = False
            self.monitor.send_event_notification(command, 'success', 1.5)
            
            # Should not have been called
            mock_post.assert_not_called()
    
    def test_message_processing_logic(self):
        """Test message processing logic without actual MQTT."""
        # Test command start handling
        payload = {
            'command': 'test command',
            'client_id': 'test-client',
            'timestamp': datetime.now().isoformat(),
            'pid': 12345
        }
        
        command_key = f"{payload['client_id']}:{payload['command']}"
        
        # Process start message
        self.monitor.handle_command_start(command_key, payload)
        
        # Verify command is tracked
        self.assertEqual(len(self.monitor.active_commands), 1)
        self.assertIn(command_key, self.monitor.active_commands)
        
        tracked_command = self.monitor.active_commands[command_key]
        self.assertEqual(tracked_command.command, payload['command'])
        self.assertEqual(tracked_command.client_id, payload['client_id'])
        self.assertEqual(tracked_command.pid, payload['pid'])
        
        # Process completion message
        self.monitor.handle_command_end(command_key, payload, 'complete')
        
        # Verify command is removed from tracking
        self.assertEqual(len(self.monitor.active_commands), 0)


if __name__ == '__main__':
    unittest.main()