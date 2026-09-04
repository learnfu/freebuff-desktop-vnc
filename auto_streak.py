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

# File & Directory Paths
SHARED_ACCOUNTS_FILE = os.path.expanduser("~/.config/freebuff-shared-accounts.json")
DELETED_ACCOUNTS_FILE = os.path.expanduser("~/.config/freebuff-deleted-accounts.json")
DESKTOP_STATE_PATH = os.path.expanduser("~/.config/freebuff-desktop/state.json")
CLI_CRED_PATH = os.path.expanduser("~/.config/manicode/credentials.json")

FREEBUFF_ALLACC_DIR = Path(os.path.expanduser("~/myworks/freebuffallacc"))
INSTANCES_DIR = FREEBUFF_ALLACC_DIR / "freebuff-cli-instances"
HOME_INSTANCES_DIR = Path(os.path.expanduser("~/.freebuff-cli-instances"))
FREEBUFF2API_BIN = FREEBUFF_ALLACC_DIR / "freebuff2api"

FALLBACK_ACCOUNTS = [
    {
        "name": "gwgdev+hey",
        "email": "gwgdev+hey@proton.me",
        "token": "55dd5d3b-c66c-4b50-8f54-a9cace677b50",
        "id": "08141fc2-810b-4960-bd11-d566010e01ab",
        "display_name": "ksopls"
    },
    {
        "name": "jkiloals",
        "email": "gwgdev@proton.me",
        "token": "b270349f-1358-4a89-9898-c9149389908e",
        "id": "e7f66312-3f69-41a8-bb40-42c5f9747921",
        "display_name": "jkiloals"
    },
    {
        "name": "koalsw",
        "email": "holapws@proton.me",
        "token": "6d3f5afa-cfa1-4eaf-8ea7-ed8b9478db96",
        "id": "626ddad4-0012-42ae-99d0-f6f8d1bb365c",
        "display_name": "koalsw"
    },
    {
        "name": "iolpsa",
        "email": "huisjal+3@proton.me",
        "token": "e8fbecc5-839b-4443-97d2-30a8538707c9",
        "id": "5af03bd7-9453-4aee-877d-f7630cb7bdc9",
        "display_name": "iolpsa"
    },
    {
        "name": "kisolaps",
        "email": "holapws+hey@proton.me",
        "token": "c7f61f4d-7f14-4361-82f3-f458b4867b79",
        "id": "b0836c8c-d294-4972-aff7-87914f22ab86",
        "display_name": "kisolaps"
    },
    {
        "name": "lpalsa",
        "email": "lookatcock+hoo@proton.me",
        "token": "51facf0a-7402-4431-b0f2-08823c3a48e0",
        "id": "246ff27d-8041-4431-b505-8cd15583e5f6",
        "display_name": "lpalsa"
    },
    {
        "name": "hirautagao",
        "email": "hirautagao@gmail.com",
        "token": "df9fae88-ae23-4581-80fc-efd0b6caebff",
        "id": "usr_slot_6",
        "display_name": "hirautagao"
    },
    {
        "name": "loopcss",
        "email": "loopcpp+wo@proton.me",
        "token": "7789cd96-c2a5-4a7f-9913-6575f99cdde0",
        "id": "97a877c5-fd9f-4838-a597-575229c39d82",
        "display_name": "loopcss"
    },
    {
        "name": "jiksol",
        "email": "lookatcock@proton.me",
        "token": "fb8e91ad-09de-4a95-a637-e9bc984b5ba6",
        "id": "91163d31-c53d-4063-baf2-a3407664d462",
        "display_name": "jiksol"
    }
]

def load_json(filepath):
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except Exception:
        return None

def load_deleted():
    data = load_json(DELETED_ACCOUNTS_FILE)
    if isinstance(data, list):
        return set(a.lower() for a in data if isinstance(a, str))
    return set()

def discover_accounts():
    deleted = load_deleted()
    accounts_by_key = {}

    for i, acc in enumerate(FALLBACK_ACCOUNTS, 1):
        email_lc = acc["email"].lower()
        tok_lc = acc["token"].lower()
        if email_lc not in deleted and tok_lc not in deleted:
            accounts_by_key[email_lc] = {
                "name": acc.get("name") or acc["email"].split("@")[0],
                "email": acc["email"],
                "token": acc["token"],
                "id": acc.get("id") or f"usr_slot_{i}",
                "display_name": acc.get("display_name") or acc.get("name") or acc["email"].split("@")[0],
                "slot": i
            }

    for slot in range(1, 9):
        for target_dir in [HOME_INSTANCES_DIR, INSTANCES_DIR]:
            cred = load_json(target_dir / f"instance{slot}" / "home/.config/manicode/credentials.json")
            if cred:
                for k, v in cred.items():
                    if isinstance(v, dict) and v.get("authToken") and v.get("email"):
                        email_lc = v["email"].lower()
                        tok_lc = v["authToken"].lower()
                        if email_lc not in deleted and tok_lc not in deleted:
                            accounts_by_key[email_lc] = {
                                "name": v.get("name") or v["email"].split("@")[0],
                                "email": v["email"],
                                "token": v["authToken"],
                                "id": v.get("id") or f"usr_slot_{slot}",
                                "display_name": v.get("name") or v["email"].split("@")[0],
                                "slot": slot
                            }

    def add_extra_acc(token, email, name=None, user_id=None):
        if not token or not isinstance(token, str) or len(token) < 10:
            return
        key = email.lower() if email else token
        if key in deleted or token.lower() in deleted:
            return
        if key not in accounts_by_key:
            accounts_by_key[key] = {
                "name": name or (email.split("@")[0] if email else "Account"),
                "email": email or "unknown@email.com",
                "token": token,
                "id": user_id or f"usr_{hash(token) % 1000000}",
                "display_name": name or (email.split("@")[0] if email else "Account")
            }

    shared = load_json(SHARED_ACCOUNTS_FILE)
    if isinstance(shared, list):
        for acc in shared:
            add_extra_acc(acc.get("token"), acc.get("email"), acc.get("name"), acc.get("id"))

    desktop_state = load_json(DESKTOP_STATE_PATH)
    if desktop_state and "authSessions" in desktop_state:
        for host, auth in desktop_state["authSessions"].items():
            if isinstance(auth, dict) and auth.get("token"):
                user = auth.get("user", {})
                add_extra_acc(auth.get("token"), user.get("email"), user.get("name"), user.get("id"))

    cli_cred = load_json(CLI_CRED_PATH)
    if cli_cred:
        for k, v in cli_cred.items():
            if isinstance(v, dict) and v.get("authToken"):
                add_extra_acc(v.get("authToken"), v.get("email"), v.get("name"), v.get("id"))

    return list(accounts_by_key.values())

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
        with urllib.request.urlopen(req, timeout=20) as resp:
            resp.read()
    except Exception:
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
        display_name = a.get("display_name", "").strip()
        slot = a.get("slot")

        if tok:
            keys_to_add = [email, email.lower(), name, name.lower(), display_name, display_name.lower()]
            if slot:
                keys_to_add.extend([f"freebuff-cli-slot-{slot}", f"slot-{slot}"])
            for k in keys_to_add:
                if k and k.lower() not in seen_keys:
                    proxy_accounts.append({"name": k, "token": tok, "enabled": True})
                    seen_keys.add(k.lower())

    cfg_data = {
        "listen_addr": f"127.0.0.1:{proxy_port}",
        "upstream_base_url": "https://www.codebuff.com",
        "accounts": proxy_accounts
    }
    cfg_path = "/tmp/auto_streak_proxy_cfg.json"
    with open(cfg_path, "w") as f:
        json.dump(cfg_data, f, indent=2)

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
