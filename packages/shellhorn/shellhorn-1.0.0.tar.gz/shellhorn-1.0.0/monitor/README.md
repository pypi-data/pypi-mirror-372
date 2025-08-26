# Shellhorn Monitor 🐚📯

A lightweight Docker service that monitors MQTT for orphaned shellhorn commands and sends alerts when commands die unexpectedly.

## What It Does

Shellhorn Monitor solves the "when it dies unexpectedly" problem by:
1. **Tracking active commands** - Listens for `shellhorn/start` messages
2. **Detecting orphans** - Commands that started but never reported completion
3. **Sending alerts** - Pushover notifications when orphaned commands are detected

## Quick Start

### 1. Setup Configuration

```bash
# Copy and customize the config file
cp config/monitor.yaml config/monitor.yaml.local

# Edit configuration (enable Pushover, add your credentials)
nano config/monitor.yaml.local
```

**monitor.yaml.local** (single config file):
```yaml
notifications:
  enabled_events:
    lost: true      # CRITICAL - host disconnects
    fail: true      # Important failures
    start: false    # Usually too noisy
    success: false  # Handle locally
  
  pushover:
    enabled: true   # ENABLE Pushover notifications
    priority:
      lost: 1       # High priority - visible but no retry (change to 2 for emergency)

# Add your credentials here (or use environment variables)
secrets:
  pushover_token: "your_app_token_here"
  pushover_user: "your_user_key_here"
  # mqtt_username: "mqtt_user"        # Optional: MQTT auth
  # mqtt_password: "mqtt_pass"        # Optional: MQTT auth
```

### 2. Run with Docker

**Option A: Docker Compose (Recommended)**

*Use prebuilt image from GHCR:*
```bash
nano .env  # Edit environment (MQTT broker, etc.)
docker-compose -f docker-compose.ghcr.yml up -d
docker-compose -f docker-compose.ghcr.yml logs -f shellhorn-monitor
```

*Or build locally:*
```bash
nano .env  # Edit environment (MQTT broker, etc.)
docker-compose up -d  # builds from Dockerfile
docker-compose logs -f shellhorn-monitor
```

**Option B: Direct Docker Run (GitHub Container Registry)**
```bash
# Run with volume binding for config
docker run -d --name shellhorn-monitor \
  -v "$(pwd)/config:/config:ro" \
  -e MQTT_BROKER=192.168.1.100 \
  ghcr.io/mitchins/shellhorn/monitor:latest
```

### 3. Verify Setup

```bash
# Check monitor is running and config loaded
docker-compose logs shellhorn-monitor

# Should show:
# Loading configuration from /config/monitor.yaml
# Secrets loaded from config (or environment variables)
# Connected to MQTT broker successfully
# Pushover enabled: true

# Test Pushover credentials (optional)
python3 config/../test_notifications.py
```

### 4. Test Lost Command Detection

**Quick Test (90 seconds):**
```bash
# Automated test with short timeout - results in 90 seconds
./quick_test.sh
```

**Manual Test:**
```bash
# Start a command and kill it manually
shellhorn sleep 300 &
kill %1
# Monitor will detect it after the configured timeout
```

**Verify Results:**
```bash
# Universal verification via MQTT (works regardless of monitor location)
mosquitto_sub -h YOUR_MQTT_BROKER -t "shellhorn/monitor/heartbeat" -v

# Local Docker verification
docker-compose logs --tail=20 shellhorn-monitor  

# Should show:
# "Lost command detected: sleep 1800 (host may be down)"
# "Emergency Pushover alert sent"
```

## Configuration

### YAML Configuration (Recommended)

**Single config file:**
- Path: `/config/monitor.yaml` 
- Contains: Settings + secrets in one place

**Docker volume binding:**
- `./config:/config:ro` (docker-compose)
- `-v $(pwd)/config:/config:ro` (docker run)

**Complete monitor.yaml example:**

```yaml
mqtt:
  broker_host: "${MQTT_BROKER:-localhost}"
  broker_port: 1883
  topic_prefix: "shellhorn"

monitoring:
  timeout_minutes: 30           # Orphan detection timeout
  check_interval_seconds: 60    # How often to check for orphans
  status_interval_seconds: 300  # Console logging frequency 
  heartbeat_interval_seconds: 60 # MQTT heartbeat frequency

notifications:
  enabled_events:
    start: false     # Command started (usually noisy)
    success: false   # Command completed (handle locally) 
    fail: true       # Command failed (important)
    lost: true       # Command never finished (CRITICAL)
  
  pushover:
    enabled: true
    priority:
      start: 0       # Normal priority
      success: 0     # Normal priority  
      fail: 1        # High priority - visible but no retry
      lost: 1        # High priority - visible but no retry (change to 2 for emergency)
    
    messages:
      lost: "🚨 Lost command: {command} (host may be down)"
```

### Environment Variables (Fallback)
- `MQTT_BROKER=localhost` - MQTT broker hostname
- `SHELLHORN_TIMEOUT_MINUTES=30` - Orphan timeout
- `SHELLHORN_CHECK_INTERVAL=60` - Check frequency (seconds)
- `SHELLHORN_HEARTBEAT_INTERVAL=60` - MQTT heartbeat frequency (seconds)

## Security Best Practices

### ✅ Recommended: Secrets File
```bash
# Store secrets in mounted file (read-only)
echo '{"pushover_token":"abc123"}' > config/secrets.json
chmod 600 config/secrets.json
```

### ⚠️ Alternative: Environment Variables
```bash
# Less secure, but works
export PUSHOVER_TOKEN=abc123
export PUSHOVER_USER=xyz789
```

### Docker Security Features
- **Non-root user** (UID 1001)
- **Read-only filesystem**
- **Resource limits** (64MB RAM, 0.1 CPU)
- **Minimal privileges**
- **Health checks**

## Monitoring Scenarios

### Home Lab Setup
```yaml
# docker-compose.yml
services:
  shellhorn-monitor:
    environment:
      - MQTT_BROKER=mqtt.homelab.local
      - SHELLHORN_TIMEOUT_MINUTES=15  # Shorter timeout
```

### Production Setup
```yaml
services:
  shellhorn-monitor:
    environment:
      - MQTT_BROKER=mqtt.prod.company.com
      - SHELLHORN_TIMEOUT_MINUTES=60  # Longer timeout
      - SHELLHORN_CHECK_INTERVAL=30   # Check more frequently
```

### Multiple Environments
```bash
# Different configs for different environments
docker run -d --name shellhorn-monitor-dev \
  -v ./config-dev:/config:ro \
  -e MQTT_BROKER=mqtt-dev.local \
  ghcr.io/mitchins/shellhorn/monitor:latest

docker run -d --name shellhorn-monitor-prod \
  -v ./config-prod:/config:ro \
  -e MQTT_BROKER=mqtt-prod.local \
  ghcr.io/mitchins/shellhorn/monitor:latest
```

## MQTT Topics

### Monitored Topics
- `shellhorn/start` - Command started → **start** event
- `shellhorn/complete` - Command finished successfully → **success** event
- `shellhorn/error` - Command had an error → **fail** event  
- `shellhorn/interrupt` - Command was interrupted → **fail** event

### Published Topics
- `shellhorn/status` - Monitor online/offline status (retained will message)
- `shellhorn/monitor/heartbeat` - Monitor health & active command status (configurable interval)

### Heartbeat Messages
The monitor publishes heartbeat messages to `shellhorn/monitor/heartbeat`:
```json
{
  "timestamp": "2025-08-26T01:53:05.123Z",
  "active_commands": 1,
  "uptime_seconds": 3600,
  "monitor_id": "shellhorn-monitor",
  "commands": [
    {
      "command": "sleep 3600",
      "client_id": "shellhorn_1756173185.354534", 
      "age_minutes": 25.2,
      "start_time": "2025-08-26T01:28:05.123Z",
      "pid": 12345
    }
  ]
}
```

**Heartbeat Frequency Options:**
- `heartbeat_interval_seconds: 30` - High frequency monitoring
- `heartbeat_interval_seconds: 60` - Standard (recommended)
- `heartbeat_interval_seconds: 300` - Low frequency (reduces MQTT traffic)

**Notification Priority Levels:**
- `priority: 0` - **Normal** - Quiet notification
- `priority: 1` - **High** - Visible notification (default for lost commands)  
- `priority: 2` - **Emergency** - Repeats every 60s until acknowledged (for critical systems)

```yaml
# For critical production systems that need emergency alerting:
priority:
  lost: 2        # Emergency - will retry every 60s for 1 hour

# For most users (default):
priority: 
  lost: 1        # High priority - visible but won't bug you
```

### Lost Command Detection
Commands that publish `start` but never publish `complete/error/interrupt` are detected as **lost** after the timeout period. This indicates the host likely disconnected or shut down unexpectedly.

## Notification System

### Event Types
- **start**: Command begins (usually disabled - too noisy)
- **success**: Command completes successfully (handle locally)
- **fail**: Command fails or interrupted (important for debugging)
- **lost**: Command never finishes (CRITICAL - indicates host issues)

### Smart Defaults
The monitor uses intelligent defaults:
- **Local events** (start/success): Disabled for central monitoring
- **Important events** (fail): High priority notifications
- **Critical events** (lost): High priority notifications (emergency available)

### Alert Examples

**Lost Command (High Priority)**:
```
🚨 Lost command detected: backup_database.sh (host may be down)

Client: server-01
Started: 2024-08-24 14:30:15
Age: 45.2 minutes
PID: 12345

Host may have disconnected or shut down unexpectedly.
```

**Failed Command (High Priority)**:
```
❌ Command failed: deploy_app.sh

Duration: 12.4s
Client: ci-runner-03
```

## Troubleshooting

### Check MQTT Connection
```bash
# Test MQTT connectivity from container
docker exec shellhorn-monitor python -c "
import socket
s = socket.socket()
s.settimeout(5)
result = s.connect_ex(('mqtt-broker', 1883))
print('MQTT OK' if result == 0 else 'MQTT FAILED')
"
```

### Debug Logging
```bash
# Enable debug logging
docker-compose exec shellhorn-monitor python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
"
```

### Manual Testing
```bash
# Send test MQTT message
mosquitto_pub -h localhost -t shellhorn/start -m '{
  "command": "test-command", 
  "client_id": "test-client",
  "timestamp": "2024-08-24T14:30:00",
  "pid": 12345
}'
```

## Resource Usage

- **Memory**: ~16MB typical, 64MB limit
- **CPU**: ~0.05% typical, 0.1% limit  
- **Network**: Minimal (MQTT messages only)
- **Storage**: Stateless (no persistence needed)

## Advanced Features

### Connection Resilience
- **MQTT v2 API** - No deprecation warnings
- **Smart reconnection** - Exponential backoff (1-30s)
- **Will messages** - Publishes offline status on disconnect
- **Session persistence** - Maintains subscriptions across reconnects
- **Clean disconnect detection** - No false alarms when publishers disconnect normally

### Notification Intelligence
- **Event filtering** - Only notify on enabled event types
- **Priority levels** - Different urgency for different events
- **Custom messages** - Template-based notifications
- **Emergency alerts** - Auto-retry for critical lost commands

Perfect for running alongside other services in resource-constrained environments like Raspberry Pi or small VPS instances.