#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "============================================================"
echo "🛑 STOPPING FREEBUFF DESKTOP GUI & VNC SERVER..."
echo "============================================================"

# Kill VNC displays & servers
pkill -9 -f 'Xvnc :21' || true
pkill -9 -f 'Xvfb :21' || true
pkill -9 -f 'x11vnc' || true
pkill -9 -f 'websockify' || true
rm -f /tmp/.X21-lock /tmp/.X11-unix/X21 || true

# Kill Freebuff Desktop, runner, Bun, and Orchestrator processes
pkill -9 -f '@codebufffreebuff-desktop' || true
pkill -9 -f 'runner.py' || true
pkill -9 -f 'resources/bun/bun' || true
pkill -9 -f 'orchestrator.js' || true
pkill -9 -f 'bun' || true

# Clean up stale orchestrator locks to prevent OrchestratorAlreadyRunningError
STATE_LOCK="$HOME/.config/freebuff-desktop/state.json.orchestrator-lock.sqlite"
rm -f "$STATE_LOCK"* || true

echo "✅ All VNC, orchestrator locks, and Freebuff Desktop GUI processes stopped!"
