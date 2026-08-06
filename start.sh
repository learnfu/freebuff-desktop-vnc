#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

python3 "$DIR/runner.py"

echo "============================================================"
echo "🎉 FREEBUFF DESKTOP GUI IS LIVE & RUNNING SMOOTH!"
echo "============================================================"
echo "📌 VNC Viewer Port:  localhost:5921 (Display :21)"
echo "📌 Web Browser Port: http://localhost:6080 (Port Viewer Plugin)"
echo "   App Logs:         $DIR/freebuff-app.log"
echo "   VNC Logs:         $DIR/x11vnc.log"
echo "   Stop Command:     ./stop.sh"
echo "============================================================"
