# Shellhorn

**Get phone notifications when your long-running shell commands finish.** Perfect for ML training, builds, or any command you don't want to babysit.

[![CI](https://github.com/mitchins/shellhorn/actions/workflows/ci.yml/badge.svg)](https://github.com/mitchins/shellhorn/actions/workflows/ci.yml)
[![codecov](https://codecov.io/github/mitchins/shellhorn/graph/badge.svg?token=SHELLHORN_CODECOV_TOKEN)](https://codecov.io/github/mitchins/shellhorn)
[![PyPI version](https://badge.fury.io/py/shellhorn.svg)](https://badge.fury.io/py/shellhorn)
[![Docker](https://img.shields.io/badge/docker-ghcr.io-blue.svg)](https://ghcr.io/mitchins/shellhorn/monitor)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

```bash
# Install
pip install shellhorn

# Just prepend any command
shellhorn python3 my-training-script.py  # Get notified when done
```

## Quick Setup

**Pushover (phone notifications):**
```bash
shellhorn config set notifications.pushover.app_token YOUR_TOKEN
shellhorn config set notifications.pushover.user_key YOUR_USER  
shellhorn config set notifications.pushover.enabled true
```

**MQTT (centralized monitoring):**
```bash
shellhorn config set notifications.mqtt.broker_host mqtt.example.com
shellhorn config set notifications.mqtt.enabled true
```

**Test it:**
```bash
shellhorn config test  # Sends test notification
```

## Usage

```bash
# Any command works - just prepend with shellhorn
shellhorn make build && make test
shellhorn ./deploy-script.sh
shellhorn python3 -m pytest --long-running-tests
shellhorn npm run build

```

**What you get:**
- Success notifications with duration
- Failure alerts with exit codes  
- Orphaned process detection (via MQTT monitor)
- Works with pipes, redirects, and complex commands
- **Start notifications disabled by default** (you know when you started it!)

## More Options

<details>
<summary><b>Environment Variables</b> (alternative to config commands)</summary>

```bash
export SHELLHORN_PUSHOVER_TOKEN=your_app_token
export SHELLHORN_PUSHOVER_USER=your_user_key
export SHELLHORN_MQTT_BROKER=mqtt.example.com
```
</details>

<details>
<summary><b>CLI Override</b> (one-time config)</summary>

```bash
shellhorn --pushover-token=xxx --pushover-user=yyy python3 script.py
shellhorn --mqtt-broker=localhost python3 script.py
```
</details>

<details>
<summary><b>Config Commands</b></summary>

```bash
shellhorn config show        # View current config
shellhorn config test        # Test notifications
shellhorn --version          # Show version

# Notification preferences (start notifications off by default)
shellhorn config set preferences.notify_start true    # Enable start notifications
shellhorn config set preferences.notify_success false # Disable success notifications
```
</details>

<details>
<summary><b>MQTT Details</b></summary>

**Topics:**
- `shellhorn/start` - Command started
- `shellhorn/complete` - Command finished
- `shellhorn/error` - Unexpected errors  
- `shellhorn/interrupt` - Interrupted (Ctrl+C)

**Message format:**
```json
{
  "command": "python3 script.py",
  "status": "success", 
  "duration": 123.45,
  "client_id": "shellhorn_123456789"
}
```
</details>

<details>
<summary><b>Monitor (Centralized Alerts)</b></summary>

Deploy the monitor to get alerts when hosts disconnect unexpectedly:

```bash
# Quick start with Docker (from GitHub Container Registry)
docker run -d --name shellhorn-monitor \
  -e MQTT_BROKER=192.168.1.100 \
  -e PUSHOVER_TOKEN=xxx -e PUSHOVER_USER=yyy \
  ghcr.io/mitchins/shellhorn/monitor:latest

# Or with config file (YAML)
docker run -d -v ./monitor.yaml:/config/monitor.yaml \
  ghcr.io/mitchins/shellhorn/monitor:latest
```

**Perfect for detecting lost commands** when machines shut down or disconnect. See `monitor/` directory for full setup.
</details>

---

*Perfect for ML training, CI/CD pipelines, data processing, or any command you don't want to babysit. The name "Shellhorn" comes from **shell** (command wrapper) + **horn** (notification alerts) 🐚📯*
