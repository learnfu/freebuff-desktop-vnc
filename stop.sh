#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "============================================================"
echo "🛑 STOPPING FREEBUFF DESKTOP GUI & VNC SERVER..."
echo "============================================================"

pkill -f 'Xvnc :21' || true
pkill -f 'Xvfb :21' || true
pkill -f 'x11vnc' || true
pkill -f 'websockify' || true
pkill -f '@codebufffreebuff-desktop' || true
pkill -f 'runner.py' || true
rm -f /tmp/.X21-lock || true

echo "✅ All VNC and Freebuff Desktop GUI processes stopped!"
