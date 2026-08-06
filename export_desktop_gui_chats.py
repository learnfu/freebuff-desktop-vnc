import sqlite3, os, json

out_md = os.path.expanduser("~/myworks/buffdesktop/freebuff_desktop_gui_conversations.md")

projects = [
    ('/teamspace/studios/this_studio/myworks/nexusgwg', 'nexusgwg'),
    ('/teamspace/studios/this_studio/myworks/ahrefclone', 'ahrefclone'),
    ('/teamspace/studios/this_studio/myworks/scherp', 'scherp'),
    ('/teamspace/studios/this_studio/myworks/gamifiedMCQs', 'gamifiedMCQs'),
    ('/teamspace/studios/this_studio/myworks/3m-digi-tech', '3m-digi-tech'),
    ('/teamspace/studios/this_studio/myworks/3mbrochure', '3mbrochure'),
    ('/teamspace/studios/this_studio/myworks/vidoes/dv4-flash', 'dv4-flash'),
    ('/teamspace/studios/this_studio/work/bsebsolution', 'bsebsolution')
]

out_lines = []
out_lines.append("# 🖥️ Freebuff Desktop GUI Conversations Export (from VNC Desktop App)\n")

grand_total = 0

for p_path, p_name in projects:
    db_file = os.path.join(p_path, '.freebuff', 'desktop-v2.db')
    if not os.path.exists(db_file):
        continue
    
    out_lines.append(f"## 📁 Project: {p_name}")
    out_lines.append(f"*Database Path: `{db_file}`*\n")
    
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM threads;")
        t_rows = cursor.fetchall()
        threads = {t[0]: t[3] for t in t_rows}
        
        cursor.execute("SELECT * FROM messages;")
        messages = cursor.fetchall()
        grand_total += len(messages)
        
        current_thread = None
        for row in messages:
            m_id = row[0]
            thread_id = row[1]
            role = row[4]
            content = row[5]
            
            if thread_id != current_thread:
                current_thread = thread_id
                t_name = threads.get(thread_id, thread_id)
                out_lines.append(f"### 💬 Thread ID: `{thread_id}` ({t_name})\n")
            
            text_val = ""
            try:
                c_json = json.loads(content)
                if isinstance(c_json, list):
                    for item in c_json:
                        if isinstance(item, dict) and item.get("kind") == "text":
                            text_val += item.get("text", "")
                else:
                    text_val = str(c_json)
            except Exception:
                text_val = str(content)
            
            if text_val.strip():
                out_lines.append(f"**[{str(role).upper()}]**:")
                out_lines.append(f"```text\n{text_val.strip()}\n```\n")
                
        conn.close()
    except Exception as e:
        print(f"Error for {p_name}: {e}")
        out_lines.append(f"Error reading DB: {e}\n")

with open(out_md, "w") as f:
    f.write("\n".join(out_lines))

print(f"✅ Successfully exported {grand_total} Freebuff Desktop GUI messages to {out_md}")
