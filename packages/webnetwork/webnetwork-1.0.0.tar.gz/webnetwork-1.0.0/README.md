# webnetwork

**webnetwork** is a Python package that automatically monitors your web server traffic, detects DoS/DDoS attacks, and blocks malicious IPs in real-time. It supports Linux, Windows, and macOS servers.

## Features

- Automatic host IP detection
- Web server log monitoring (Nginx, Apache)
- Live packet sniffing for TCP/SYN floods
- Automatic IP blocking (iptables on Linux/macOS, Windows firewall)
- Cross-platform support
- Minimal configuration required

## Installation

```bash
pip install webnetwork
```

## Usage

### Fully Automatic

Automatically detects logs and interfaces:

```python
import webnetwork

webnetwork.start()
```

### Specify Logfile or Network Interface

```python
import webnetwork

# Only monitor log file
webnetwork.start(logfile="/var/log/nginx/access.log")

# Only monitor network interface
webnetwork.start(iface="eth0")

# Monitor both
webnetwork.start(logfile="/var/log/nginx/access.log", iface="eth0")
```

### Notes

* Local blocking requires admin/root privileges.
* Automatically tries to detect common log files (`/var/log/nginx/access.log`, `/var/log/apache2/access.log`, `/var/log/httpd/access_log`).
* Live packet sniffing requires `scapy` and may need root/admin privileges.
* Monitors traffic continuously and logs alerts to `alerts.csv`.

## Configuration

Thresholds for detection can be tuned by modifying `detector.py`:

```python
LOG_CHECK_INTERVAL = 1.0
WINDOW_SECONDS = 10
REQS_PER_IP_THRESHOLD = 50
TOTAL_RPS_THRESHOLD = 200
UNIQUE_IP_ENTROPY_THRESHOLD = 0.5
SYN_RATE_THRESHOLD = 100
SYN_TO_ACK_RATIO = 5.0
```

## License

MIT License

## Author

Your Name – [you@example.com](mailto:mrfidal@proton.me)
