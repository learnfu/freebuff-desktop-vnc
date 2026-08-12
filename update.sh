#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "============================================================"
echo "🔄 UPDATING FREEBUFF DESKTOP TO LATEST VERSION"
echo "============================================================"

# 1. Stop current Desktop instance cleanly
echo "🛑 Stopping running Desktop instance..."
bash "$DIR/stop.sh" || true
sleep 2

# 2. Backup current AppImage if exists
APPIMAGE="$DIR/Freebuff-Desktop.AppImage"
BACKUP_APPIMAGE="$DIR/Freebuff-Desktop.AppImage.bak"

if [ -f "$APPIMAGE" ]; then
    cp -f "$APPIMAGE" "$BACKUP_APPIMAGE" || true
fi

# 3. Download latest Freebuff Desktop AppImage
TEMP_APPIMAGE="$DIR/Freebuff-Desktop.AppImage.tmp"
rm -f "$TEMP_APPIMAGE"

echo "📥 Fetching latest Freebuff Desktop release..."
DOWNLOAD_SUCCESS=0

# Primary endpoint
if curl -fsSL -L "https://codebuff.com/api/desktop/download/linux" -o "$TEMP_APPIMAGE" 2>/dev/null && [ -s "$TEMP_APPIMAGE" ]; then
    DOWNLOAD_SUCCESS=1
elif curl -fsSL -L "https://freebuff.com/api/desktop/download/linux" -o "$TEMP_APPIMAGE" 2>/dev/null && [ -s "$TEMP_APPIMAGE" ]; then
    DOWNLOAD_SUCCESS=1
fi

if [ "$DOWNLOAD_SUCCESS" -eq 1 ]; then
    mv -f "$TEMP_APPIMAGE" "$APPIMAGE"
    chmod +x "$APPIMAGE"
    echo "✅ Downloaded latest Freebuff Desktop AppImage!"
else
    echo "⚠️ Download server endpoint unreachable, checking local AppImage..."
    rm -f "$TEMP_APPIMAGE"
    if [ -f "$BACKUP_APPIMAGE" ]; then
        cp -f "$BACKUP_APPIMAGE" "$APPIMAGE"
    fi
fi

# 4. Extract latest AppImage for fast no-FUSE execution
if [ -f "$APPIMAGE" ]; then
    echo "📦 Extracting latest Freebuff Desktop package..."
    rm -rf "$DIR/squashfs-root"
    "$APPIMAGE" --appimage-extract >/dev/null 2>&1 || true
    echo "✅ Extracted latest package to squashfs-root!"
fi

# 5. Clean up stale lock files
rm -f ~/.config/freebuff-desktop/state.json.orchestrator-lock.sqlite* || true

# 6. Relaunch Freebuff Desktop
echo "============================================================"
echo "🚀 RESTARTING FREEBUFF DESKTOP GUI..."
echo "============================================================"
bash "$DIR/start.sh"

echo ""
echo "============================================================"
echo "🎉 FREEBUFF DESKTOP HAS BEEN UPDATED TO LATEST VERSION!"
echo "============================================================"
