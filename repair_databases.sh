#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "============================================================"
echo "🛠️ REPAIRING FREEBUFF DESKTOP SQLITE DATABASES"
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
    
    try:
        conn = sqlite3.connect(db)
        c = conn.cursor()
        c.execute('PRAGMA wal_checkpoint(FULL);')
        c.execute('REINDEX;')
        c.execute('VACUUM;')
        c.execute('PRAGMA integrity_check;')
        res = c.fetchone()[0]
        conn.close()
        
        dump_cmd = f'sqlite3 \"{db}\" \".dump\" | sqlite3 \"{db}.clean\"'
        os.system(dump_cmd)
        if os.path.exists(f'{db}.clean') and os.path.getsize(f'{db}.clean') > 1000:
            shutil.copyfile(f'{db}.clean', db)
            os.remove(f'{db}.clean')
            if os.path.exists(wal): os.remove(wal)
            if os.path.exists(shm): os.remove(shm)
            print(f'✅ Project [{p_name}] database repaired successfully ({os.path.getsize(db)} bytes)!')
    except Exception as e:
        print(f'❌ Error repairing {p_name}: {e}')
"

echo "============================================================"
echo "🎉 ALL DATABASES REPAIRED & READY!"
echo "============================================================"
