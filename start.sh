#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

VNC_PORT="5921"
WEB_PORT="6080"

# Parse positional arguments or flags
if [[ $# -ge 1 && "$1" != --* ]]; then
  VNC_PORT="$1"
fi
if [[ $# -ge 2 && "$2" != --* ]]; then
  WEB_PORT="$2"
fi

while [[ $# -gt 0 ]]; do
  case $1 in
    --vnc)
      VNC_PORT="$2"
      shift 2
      ;;
    --web)
      WEB_PORT="$2"
      shift 2
      ;;
    *)
      shift
      ;;
  esac
done

python3 "$DIR/runner.py" --vnc "$VNC_PORT" --web "$WEB_PORT"

echo "============================================================"
echo "🎉 FREEBUFF DESKTOP GUI IS LIVE & RUNNING SMOOTH!"
echo "============================================================"
echo "📌 VNC Viewer Port:  localhost:$VNC_PORT (Display :21)"
echo "📌 Web Browser Port: http://localhost:$WEB_PORT (Port Viewer Plugin)"
echo "   App Logs:         $DIR/freebuff-app.log"
echo "   VNC Logs:         $DIR/xvnc.log"
echo "   Stop Command:     ./stop.sh"
echo "============================================================"
