# ⚡ Freebuff Desktop VNC Setup (Ultra-Fast Zero-Lag GUI)

A lightweight, high-performance Linux desktop environment setup for running **Freebuff Desktop GUI** on cloud VMs (Lightning.ai Studio, VPS, Docker, AWS, GCP) with **Native TigerVNC Standalone Server (`Xvnc`)** for 0ms typing response, zero lag, and an **automatic OAuth Sign-In URL capturer**.

---

## 🚀 Features

* **⚡ Native TigerVNC Server (`Xvnc`)**: Built-in C++ Tight/JPEG compression compiled directly into display driver for 0ms typing & scrolling response.
* **🔗 Automatic OAuth Login Link Capturer**: Captures the "Sign In" link automatically when clicked inside the desktop app and saves it for easy copy-pasting.
* **🖥️ 1440x900 Native Monitor Support**: Matches standard laptop & desktop resolutions with auto-maximized app window.
* **🌐 Web & Native VNC Access**: Connect via TigerVNC Viewer (`port 5921`) or Web Browser noVNC (`port 6080`).
* **📦 One-Click Setup Script**: Automatically downloads dependencies, sets up 4GB swap buffer, and extracts Freebuff Desktop Linux AppImage.

---

## 📥 Quick One-Line Installation

Clone this repository and run `install.sh`:

```bash
git clone https://github.com/learnfu/freebuff-desktop-vnc.git ~/myworks/buffdesktop
cd ~/myworks/buffdesktop
chmod +x *.sh bin/*
./install.sh
```

---

## 🎮 Usage Guide

### 1. Start the GUI Environment
```bash
./start.sh
```

### 2. Connect via VNC or Web Browser
* **TigerVNC Viewer (Recommended for 0ms Lag)**: Connect to `localhost:5921` (Display `:21`).
* **Browser Web Access**: Open `http://localhost:6080` (or use Port Viewer Plugin).

### 3. Sign In & Get Login URL
1. Click **Sign In** inside Freebuff Desktop GUI.
2. In your terminal, run:
   ```bash
   ./get_login_url.sh
   ```
   *(Or run `cat login_url.txt`)*
3. Copy and paste the captured URL into your local browser to complete sign-in.

### 4. Stop the Environment
```bash
./stop.sh
```

---

## 📁 Included Files

* `install.sh` - Installs apt packages, Linux GUI libraries, sets up swap, downloads & extracts Freebuff Desktop AppImage.
* `start.sh` - Launcher script that starts the background daemon.
* `stop.sh` - Stops all VNC, Xvnc, websockify, and Freebuff processes cleanly.
* `runner.py` - Core daemon process managing Xvnc (`:21`), window manager, and Electron 2D rendering.
* `bin/xdg-open` - Custom browser wrapper capturing OAuth login URLs.
* `get_login_url.sh` - Displays the latest captured Sign-In URL.
