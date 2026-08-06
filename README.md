# ⚡ Freebuff Desktop VNC Setup (Ultra-Fast Zero-Lag GUI)

A lightweight, high-performance Linux desktop environment setup for running **Freebuff Desktop GUI** on cloud VMs (Lightning.ai Studio, VPS, Docker, AWS, GCP) with **Native TigerVNC Standalone Server (`Xvnc`)** for 0ms typing response, zero lag, custom port support, and an **automatic OAuth Sign-In URL capturer**.

---

## 🚀 Features

* **⚡ Native TigerVNC Server (`Xvnc`)**: Built-in C++ Tight/JPEG compression compiled directly into display driver for 0ms typing & scrolling response.
* **🛡️ Zero Crashes & Robust Fallback**: Auto-installs `Xvnc` or falls back seamlessly to `Xvfb` + `x11vnc` if missing — never crashes with `FileNotFoundError`.
* **🔌 Custom Port Support**: Easily launch on any custom VNC or Web ports directly via `./start.sh [vnc_port] [web_port]` or `./start.sh --vnc 5922 --web 6082`.
* **🔗 Automatic OAuth Login Link Capturer**: Captures the "Sign In" link automatically when clicked inside the desktop app and saves it for easy copy-pasting.
* **🖥️ 1440x900 Native Monitor Support**: Matches standard laptop & desktop resolutions with auto-maximized app window.
* **🌐 Web & Native VNC Access**: Connect via TigerVNC Viewer or Web Browser noVNC.
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

* **Default Ports (VNC: 5921, Web: 6080)**:
  ```bash
  ./start.sh
  ```
* **Custom Ports Example (VNC: 5922, Web: 6082)**:
  ```bash
  ./start.sh 5922 6082
  ```
  *or with flags*:
  ```bash
  ./start.sh --vnc 5925 --web 6085
  ```

### 2. Connect via VNC or Web Browser
* **TigerVNC Viewer (Recommended for 0ms Lag)**: Connect to `localhost:5921` (or your custom VNC port).
* **Browser Web Access**: Open `http://localhost:6080` (or your custom Web port).

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
