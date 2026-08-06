#!/usr/bin/env python3
import json, os

config_dir = os.path.expanduser("~/.config/manicode")
out_md = os.path.expanduser("~/myworks/buffdesktop/conversations_summary.md")

lines = ["# 📜 Freebuff Desktop & CLI Conversations Export\n"]

# 1. Export Global Message History
mh_file = os.path.join(config_dir, "message-history.json")
if os.path.exists(mh_file):
    lines.append("## 💬 Global Prompt & Message History\n")
    try:
        data = json.load(open(mh_file))
        if isinstance(data, list):
            for i, msg in enumerate(data, 1):
                txt = str(msg).strip()
                lines.append(f"### {i}. Message")
                lines.append(f"```text\n{txt}\n```\n")
    except Exception as e:
        lines.append(f"Error reading message-history.json: {e}\n")

# 2. Export Project Specific Conversations
projects_dir = os.path.join(config_dir, "projects")
if os.path.exists(projects_dir):
    lines.append("## 📁 Project Chat Sessions\n")
    for proj in os.listdir(projects_dir):
        p_path = os.path.join(projects_dir, proj, "chats")
        if os.path.exists(p_path):
            lines.append(f"### Project: `{proj}`\n")
            for c in sorted(os.listdir(p_path), reverse=True):
                c_dir = os.path.join(p_path, c)
                msg_file = os.path.join(c_dir, "chat-messages.json")
                if os.path.exists(msg_file):
                    try:
                        msgs = json.load(open(msg_file))
                        lines.append(f"#### Session `{c}` ({len(msgs)} messages)\n")
                        for idx, m in enumerate(msgs, 1):
                            role = m.get("role", "user") if isinstance(m, dict) else "user"
                            text = m.get("content", "") if isinstance(m, dict) else str(m)
                            lines.append(f"**[{role.upper()}]**: {text}\n")
                    except Exception: pass

with open(out_md, "w") as f:
    f.write("\n".join(lines))

print(f"✅ Exported conversations summary to {out_md}")
