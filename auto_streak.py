#!/usr/bin/env python3
"""
🔥 FREEBUFF AUTOMATED DAILY STREAK BOOSTER (`auto_streak.py`) 🔥
Scans all configured accounts, checks their daily streak status, and automatically
routes a lightweight session turn through the local Freebuff proxy harness for any account
that hasn't registered usage today to boost its streak to 1+ immediately!
"""

import os
import sys
import json
import time
import subprocess
import urllib.request
import urllib.error
import concurrent.futures
from pathlib import Path

SHARED_ACCOUNTS_FILE = os.path.expanduser("~/.config/freebuff-shared-accounts.json")
DELETED_ACCOUNTS_FILE = os.path.expanduser("~/.config/freebuff-deleted-accounts.json")
HOME_INSTANCES_DIR = Path(os.path.expanduser("~/.freebuff-cli-instances"))
INSTANCES_DIR = Path(os.path.expanduser("~/myworks/freebuffallacc/freebuff-cli-instances"))
FREEBUFF2API_BIN = Path(os.path.expanduser("~/myworks/freebuffallacc/freebuff2api"))

FALLBACK_ACCOUNTS = [
    {"name": "gwgdev+hey", "email": "gwgdev+hey@proton.me", "token": "55dd5d3b-c66c-4b50-8f54-a9cace677b50"},
    {"name": "jkiloals", "email": "gwgdev@proton.me", "token": "b270349f-1358-4a89-9898-c9149389908e"},
    {"name": "koalsw", "email": "holapws@proton.me", "token": "6d3f5afa-cfa1-4eaf-8ea7-ed8b9478db96"},
    {"name": "kisolaps", "email": "holapws+hey@proton.me", "token": "c7f61f4d-7f14-4361-82f3-f458b4867b79"},
    {"name": "lpalsa", "email": "lookatcock+hoo@proton.me", "token": "51facf0a-7402-4431-b0f2-08823c3a48e0"},
    {"name": "hirautagao", "email": "hirautagao@gmail.com", "token": "df9fae88-ae23-4581-80fc-efd0b6caebff"},
    {"name": "loopcss", "email": "loopcpp+wo@proton.me", "token": "7789cd96-c2a5-4a7f-9913-6575f99cdde0"},
    {"name": "jiksol", "email": "lookatcock@proton.me", "token": "fb8e91ad-09de-4a95-a637-e9bc984b5ba6"}
]

def load_json(p):
    if os.path.exists(p):
        try:
            return json.load(open(p))
        except Exception:
            pass
    return None

def load_deleted():
    data = load_json(DELETED_ACCOUNTS_FILE)
    if isinstance(data, list):
        return set(a.lower() for a in data if isinstance(a, str))
    return set()

def discover_accounts():
    deleted = load_deleted()
    accs_by_email = {}

    for a in FALLBACK_ACCOUNTS:
        email = a.get("email", "").lower()
        tok = a.get("token")
        if email and tok and email not in deleted and tok.lower() not in deleted:
            accs_by_email[email] = a

    shared = load_json(SHARED_ACCOUNTS_FILE)
    if isinstance(shared, list):
        for a in shared:
            email = a.get("email", "").lower()
            tok = a.get("token")
            if email and tok and email not in deleted and tok.lower() not in deleted:
                accs_by_email[email] = a

    for target_dir in [HOME_INSTANCES_DIR, INSTANCES_DIR]:
        if target_dir.exists():
            for inst in target_dir.glob("instance*"):
                cred = load_json(inst / "home/.config/manicode/credentials.json")
                if cred:
                    for v in cred.values():
                        if isinstance(v, dict) and v.get("authToken") and v.get("email"):
                            email = v["email"].lower()
                            tok = v["authToken"]
                            if email not in deleted and tok.lower() not in deleted and email not in accs_by_email:
                                accs_by_email[email] = {
                                    "name": v.get("name") or email.split("@")[0],
                                    "email": v["email"],
                                    "token": tok
                                }

    return list(accs_by_email.values())

def get_streak_info(token):
    url = "https://www.codebuff.com/api/v1/freebuff/streak"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}", "User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        if e.code in [401, 403]:
            return {"streak": 0, "todayUsed": False, "status": "🔴 Banned/Expired Token"}
        return None
    except Exception:
        return None

def boost_account_streak(acc, proxy_port):
    token = acc.get("token")
    email = acc.get("email")
    name = acc.get("name")

    streak_info = get_streak_info(token)
    if not streak_info or streak_info.get("status") == "🔴 Banned/Expired Token":
        return {"name": name, "email": email, "status": "🔴 Banned/Expired Token", "streak": 0, "todayUsed": False}

    if streak_info.get("todayUsed"):
        return {
            "name": name,
            "email": email,
            "status": "✅ Already Active Today",
            "streak": streak_info.get("streak", 0),
            "todayUsed": True,
            "lastUsageDate": streak_info.get("lastUsageDate")
        }

    payload = json.dumps({
        "model": "mimo/mimo-v2.5",
        "messages": [{"role": "user", "content": "hi"}]
    }).encode()

    req = urllib.request.Request(
        f"http://127.0.0.1:{proxy_port}/v1/chat/completions",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "X-Freebuff-Account": email
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            resp.read()
    except Exception as e:
        pass

    time.sleep(2)
    updated_streak = get_streak_info(token)
    if updated_streak and updated_streak.get("todayUsed"):
        return {
            "name": name,
            "email": email,
            "status": f"🚀 Streak Boosted to {updated_streak.get('streak', 0)}d!",
            "streak": updated_streak.get("streak", 0),
            "todayUsed": True,
            "lastUsageDate": updated_streak.get("lastUsageDate")
        }
    else:
        return {
            "name": name,
            "email": email,
            "status": "⚡ Session Turn Sent",
            "streak": updated_streak.get("streak", 0) if updated_streak else 0,
            "todayUsed": updated_streak.get("todayUsed", False) if updated_streak else False,
            "lastUsageDate": updated_streak.get("lastUsageDate", "N/A") if updated_streak else "N/A"
        }

def run_auto_streak():
    accounts = discover_accounts()
    print("=" * 95)
    print(" 🔥 AUTOMATED FREEBUFF DAILY STREAK BOOSTER 🔥")
    print("=" * 95)
    print(f"Checking & boosting daily streaks for {len(accounts)} accounts...\n")

    proxy_port = 8998
    proxy_accounts = []
    seen_keys = set()

    for a in accounts:
        tok = a.get("token")
        email = a.get("email", "").strip()
        name = a.get("name", "").strip()
        if tok:
            if email and email.lower() not in seen_keys:
                proxy_accounts.append({"name": email, "token": tok, "enabled": True})
                proxy_accounts.append({"name": email.lower(), "token": tok, "enabled": True})
                seen_keys.add(email.lower())
            if name and name.lower() not in seen_keys:
                proxy_accounts.append({"name": name, "token": tok, "enabled": True})
                proxy_accounts.append({"name": name.lower(), "token": tok, "enabled": True})
                seen_keys.add(name.lower())

    cfg_data = {
        "listen_addr": f"127.0.0.1:{proxy_port}",
        "upstream_base_url": "https://www.codebuff.com",
        "accounts": proxy_accounts
    }
    cfg_path = "/tmp/auto_streak_proxy_cfg.json"
    json.dump(cfg_data, open(cfg_path, "w"), indent=2)

    proxy_proc = None
    if FREEBUFF2API_BIN.exists():
        proxy_proc = subprocess.Popen(
            [str(FREEBUFF2API_BIN), "-config", cfg_path],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        time.sleep(2)

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        future_to_acc = {executor.submit(boost_account_streak, acc, proxy_port): acc for acc in accounts}
        for future in concurrent.futures.as_completed(future_to_acc):
            try:
                results.append(future.result())
            except Exception:
                pass

    if proxy_proc:
        proxy_proc.terminate()

    results.sort(key=lambda x: [a['email'] for a in accounts].index(x['email']) if x['email'] in [a['email'] for a in accounts] else 0)

    print(f" {'#':<3} | {'Account Name':<16} | {'Email':<30} | {'Streak':<10} | {'Today Used':<10} | Result Status")
    print("-" * 95)

    for i, r in enumerate(results, 1):
        streak_str = f"🔥 {r['streak']}d"
        today_str = "✅ Yes" if r.get("todayUsed") else "❌ No"
        print(f" {i:<3} | {r['name']:<16} | {r['email']:<30} | {streak_str:<10} | {today_str:<10} | {r['status']}")

    print("-" * 95)
    print("🎉 Daily streak booster process complete!\n")

if __name__ == "__main__":
    run_auto_streak()
