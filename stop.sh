#!/usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🛑 Stopping Freebuff Desktop GUI & VNC servers..."

pkill -f "runner.py" 2>/dev/null || true
pkill -f "squashfs-root/@codebufffreebuff-desktop" 2>/dev/null || true
pkill -f "Freebuff-Desktop.AppImage" 2>/dev/null || true
pkill -f "x11vnc.*5921" 2>/dev/null || true
pkill -f "websockify.*6080" 2>/dev/null || true
pkill -f "Xvfb :21" 2>/dev/null || true
pkill -f "fluxbox" 2>/dev/null || true
rm -f "/tmp/.X21-lock" 2>/dev/null || true

echo "✅ All Freebuff Desktop GUI & VNC processes stopped!"
