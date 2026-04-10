# 🏎️ RC Race Control — BusTWeek Smart Car 2026

> **1st Place — BusTWeek Smart Car Race | Howest Bruges, April 2026**
> *Record-breaking lap time achieved with this codebase.*

---

## 🏆 About This Project

This repository contains the complete software stack powering our RC racecar, built and raced during **BusTWeek** — the annual Smart Car Race organized at **Howest University of Applied Sciences, Bruges**.

The challenge: build a remotely controlled car from scratch using a **Raspberry Pi 4** and electronic components, then race it against other teams. We didn't just compete — **we won, setting the fastest time of the event.**

<p align="center">
  <img src="media/certificate.png" alt="Winner's Certificate" width="600">
</p>

---

## 🧠 How It Works

The car is controlled entirely through a **web browser** — no app install needed, works on any phone or laptop on the same network. The architecture is a clean three-layer system running entirely on the Pi:

```
Browser (UI)
    │  HTTP fetch requests
    ▼
Apache CGI (steering.cgi / car_control.cgi)
    │  Unix socket commands
    ▼
car_daemon.py (persistent GPIO process)
    │  GPIO signals
    ▼
L298N Motor Driver → DC Motors
```

### Why a daemon?
GPIO pins reset to off the moment a process exits. A naive approach (run a script per request) means motors fire for microseconds then die. The daemon holds GPIO state indefinitely, only changing when a new command arrives — giving smooth, reliable control.

---

## ⚙️ Hardware

| Component | Details |
|-----------|---------|
| **SBC** | Raspberry Pi 4 |
| **Motor Driver** | L298N H-Bridge |
| **Motors** | 4× DC motors (4-wheel differential drive) |
| **Power (Pi)** | Power bank |
| **Power (Motors)** | 2× stacks of 4× AA batteries |
| **Chassis** | Custom RC car frame |

**GPIO Pin Mapping:**

| Pin (BCM) | Function |
|-----------|----------|
| GPIO 5 | IN1 — Left side backward |
| GPIO 6 | IN2 — Left side forward |
| GPIO 13 | IN3 — Right side backward |
| GPIO 19 | IN4 — Right side forward |

---

## 🕹️ Features

### Control Modes
- **D-Pad** — 8-directional button grid (FL, F, FR, L, R, BL, B, BR)
- **Virtual Joystick** — drag-to-steer touch interface for mobile
- **Keyboard** — arrow keys to drive, Space to stop, diagonals supported

### Smart Behaviors
- **Hold-to-move** — car moves while button is held, stops instantly on release
- **Combined directions** — forward-left, forward-right, backward-left, backward-right simultaneously
- **Spin in place** — dedicated spin-left / spin-right for tight maneuvering
- **Auto-stop** — car stops automatically if browser loses focus or tab switches
- **Live telemetry** — real-time direction and steering display in the UI

### Architecture
- Zero-latency daemon via Unix socket (no process spawn overhead per request)
- Pure CGI — no framework, no dependencies beyond Python stdlib + gpiozero
- Single-file UI — works on any browser, no install, no app

---

## 🚀 Installation

### Prerequisites
```bash
sudo apt update
sudo apt install apache2 python3 python3-gpiozero libgpiod2 -y
sudo a2enmod cgid
```

### Deploy Files
```bash
sudo cp car_daemon.py car_control.py car_control.cgi steering.cgi /var/www/cgi-bin/
sudo chmod +x /var/www/cgi-bin/steering.cgi
sudo chmod +x /var/www/cgi-bin/car_control.cgi
sudo chmod +x /var/www/cgi-bin/car_control.py
sudo chmod +x /var/www/cgi-bin/car_daemon.py
```

### Install & Enable the Daemon Service
```bash
sudo cp car_daemon.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable car_daemon
sudo systemctl start car_daemon
```

### Verify
```bash
sudo systemctl status car_daemon
ls -la /var/run/car.sock   # should show srwxrwxrwx
```

### Access
Open a browser on any device on the same network:
```
http://<raspberry-pi-ip>/cgi-bin/steering.cgi
```
Find your Pi's IP with `hostname -I`.

---

## 📁 File Structure

```
├── media/
│   └── certificate.png     # Official winner's certificate
├── steering.cgi        # Main UI — full controller interface served as HTML
├── car_control.cgi     # Lightweight CGI endpoint called by JS fetch requests
├── car_control.py      # Unix socket client — sends commands to the daemon
├── car_daemon.py       # Persistent GPIO daemon — holds motor state
├── car_daemon.service  # systemd unit — auto-starts daemon on boot
├── .gitignore          # Excludes logs and runtime files
└── README.md
```

> No virtual environment or `.env` needed — this project has no third-party pip dependencies beyond `gpiozero` which is installed system-wide on Raspberry Pi OS.

---

## 🔧 Troubleshooting

**Car doesn't move via web but works via terminal:**
Apache runs in a private `/tmp` namespace. Make sure the socket path is `/var/run/car.sock` (not `/tmp/`) and `PrivateTmp=false` is set in the Apache systemd unit.

**`GPIO busy` error on daemon start:**
A previous daemon instance didn't clean up. Reboot the Pi or run:
```bash
sudo systemctl stop car_daemon && sudo systemctl start car_daemon
```

**Blank page on steering.cgi:**
Check Apache error logs: `sudo tail -20 /var/log/apache2/error.log`

---

## 🎓 Event

**BusTWeek Smart Car Race**
Howest University of Applied Sciences, Bruges
April 2026

Organized under the Applied Informatics programme.
Programme Manager: **Joachim François**

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

*Built under pressure. Raced to victory. 🏁*