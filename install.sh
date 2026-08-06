#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "============================================================"
echo "📦 INSTALLING FREEBUFF DESKTOP & VNC GUI DEPENDENCIES"
echo "============================================================"

# 1. Verify/Setup Swap Memory
if ! swapon --show | grep -q '/swapfile'; then
    echo "⚙️ Setting up 4GB Swap memory buffer..."
    sudo fallocate -l 4G /swapfile 2>/dev/null || sudo dd if=/dev/zero of=/swapfile bs=1M count=4096 2>/dev/null || true
    sudo chmod 600 /swapfile 2>/dev/null || true
    sudo mkswap /swapfile 2>/dev/null || true
    sudo swapon /swapfile 2>/dev/null || true
fi

# 2. Install Linux GUI, Window Managers, TigerVNC, and Electron dependencies
echo "📥 Installing apt packages (tigervnc-standalone-server, xvfb, x11vnc, fluxbox, openbox, websockify, novnc, wmctrl, xdotool)..."
sudo apt-get update -qq && sudo apt-get install -y -qq tigervnc-standalone-server xvfb x11vnc fluxbox openbox websockify novnc wmctrl xdotool libfuse2 libgtk-3-0 libnss3 libasound2 libgbm1 libxss1 >/dev/null 2>&1 || true

# 3. Download Freebuff Desktop AppImage if missing
APPIMAGE="$DIR/Freebuff-Desktop.AppImage"
if [ ! -f "$APPIMAGE" ]; then
    echo "📥 Downloading Freebuff Desktop AppImage from official server..."
    curl -fsSL -L "https://freebuff.com/api/desktop/download/linux" -o "$APPIMAGE"
    chmod +x "$APPIMAGE"
fi

# 4. Extract AppImage for high performance / no-FUSE execution
if [ ! -d "$DIR/squashfs-root" ]; then
    echo "📦 Extracting AppImage for fast Linux execution..."
    "$APPIMAGE" --appimage-extract >/dev/null 2>&1 || true
fi

echo ""
echo "============================================================"
echo "✅ INSTALLATION COMPLETE!"
echo "   Run ./start.sh to launch Freebuff Desktop GUI on VNC port 5921!"
echo "   Custom Ports Example: ./start.sh 5922 6082"
echo "============================================================"
