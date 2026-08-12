#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "============================================================"
echo "🛑 STOPPING FREEBUFF DESKTOP GUI & VNC SERVER..."
echo "============================================================"

pkill -9 -f 'Xvnc :21' || true
pkill -9 -f 'Xvfb :21' || true
pkill -9 -f 'x11vnc' || true
pkill -9 -f 'websockify' || true
pkill -9 -f '@codebufffreebuff-desktop' || true
pkill -9 -f 'runner.py' || true
pkill -9 -f 'bun' || true
rm -f /tmp/.X21-lock || true

# Clean up stale orchestrator locks to prevent OrchestratorAlreadyRunningError
STATE_LOCK="$HOME/.config/freebuff-desktop/state.json.orchestrator-lock.sqlite"
rm -f "$STATE_LOCK"* || true

echo "✅ All VNC, orchestrator locks, and Freebuff Desktop GUI processes stopped!"
