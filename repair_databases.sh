#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "============================================================"
echo "🛑 FORCE-KILLING PROCESSES TO RELEASE ALL FILE LOCKS..."
echo "============================================================"
pkill -9 -f 'bun' || true
pkill -9 -f 'node' || true
pkill -9 -f '@codebufffreebuff-desktop' || true
pkill -9 -f 'Xvnc' || true
pkill -9 -f 'Xvfb' || true
rm -f /tmp/.X*-lock /tmp/.X11-unix/X* || true
sleep 2

echo "============================================================"
echo "🛠️ REPAIRING & ENABLING WAL MODE ON DESKTOP DATABASES"
echo "============================================================"

python3 -c "
import sqlite3, os, shutil

projects = [
    '/teamspace/studios/this_studio/myworks/gamifiedMCQs',
    '/teamspace/studios/this_studio/myworks/nexusgwg',
    '/teamspace/studios/this_studio/myworks/scherp',
    '/teamspace/studios/this_studio/myworks/3m-digi-tech',
    '/teamspace/studios/this_studio/myworks/ahrefclone',
    '/teamspace/studios/this_studio/myworks/3mbrochure',
    '/teamspace/studios/this_studio/myworks/vidoes/dv4-flash',
    '/teamspace/studios/this_studio/work/bsebsolution'
]

for p in projects:
    db = os.path.join(p, '.freebuff', 'desktop-v2.db')
    wal = db + '-wal'
    shm = db + '-shm'
    
    if not os.path.exists(db): continue
    p_name = os.path.basename(p)
    
    if os.path.exists(wal): os.remove(wal)
    if os.path.exists(shm): os.remove(shm)
    
    try:
        conn = sqlite3.connect(db, timeout=10)
        c = conn.cursor()
        c.execute('PRAGMA journal_mode = WAL;')
        jm = c.fetchone()[0]
        c.execute('PRAGMA busy_timeout = 5000;')
        c.execute('PRAGMA synchronous = NORMAL;')
        c.execute('REINDEX;')
        c.execute('VACUUM;')
        conn.close()
        print(f'✅ Project [{p_name}] -> WAL mode enabled ({jm}) & optimized successfully!')
    except Exception as e:
        print(f'❌ Error repairing {p_name}: {e}')
"

echo "============================================================"
echo "🚀 RESTARTING FREEBUFF DESKTOP GUI..."
echo "============================================================"
./start.sh
