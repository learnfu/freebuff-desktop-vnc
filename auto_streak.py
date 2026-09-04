#!/usr/bin/env python3
"""
🔥 FREEBUFF AUTOMATED DAILY STREAK BOOSTER (`auto_streak.py`) 🔥
Scans all configured accounts, checks their daily streak status, and automatically
routes a lightweight session turn through local proxy or direct Codebuff agent-run harness
for any account that hasn't registered usage today to boost its streak to 1+ immediately!
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
BUFFDESKTOP_DIR = Path(os.path.expanduser("~/myworks/buffdesktop"))
INSTANCES_DIR = FREEBUFF_ALLACC_DIR / "freebuff-cli-instances"
HOME_INSTANCES_DIR = Path(os.path.expanduser("~/.freebuff-cli-instances"))
FREEBUFF2API_BIN = FREEBUFF_ALLACC_DIR / "freebuff2api"

FALLBACK_ACCOUNTS = []

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
    slot_accounts = {}
    for slot in range(1, 9):
        slot_accounts[slot] = {
            "name": f"freebuff-cli-slot-{slot}",
            "email": "not logged in",
            "token": "",
            "id": f"usr_slot_{slot}",
            "display_name": f"slot-{slot}",
            "slot": slot
        }

    for i, acc in enumerate(FALLBACK_ACCOUNTS, 1):
        if acc["email"].lower() in deleted or acc["token"].lower() in deleted:
            slot_accounts[i] = {
                "name": f"freebuff-cli-slot-{i}",
                "email": "not logged in",
                "token": "",
                "id": f"usr_slot_{i}",
                "display_name": f"slot-{i}",
                "slot": i
            }
        else:
            slot_accounts[i] = {
                "name": acc["name"],
                "email": acc["email"],
                "token": acc["token"],
                "id": acc["id"],
                "display_name": acc["display_name"],
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
                            slot_accounts[slot] = {
                                "name": v.get("name") or v["email"].split("@")[0],
                                "email": v["email"],
                                "token": v["authToken"],
                                "id": v.get("id") or f"usr_slot_{slot}",
                                "display_name": v.get("name") or v["email"].split("@")[0],
                                "slot": slot
                            }

    accounts_by_key = {}
    for slot in range(1, 9):
        acc = slot_accounts[slot]
        if acc["email"] != "not logged in":
            accounts_by_key[acc["email"].lower()] = acc

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

    return [a for a in accounts_by_key.values() if a["email"].lower() not in deleted and a["token"].lower() not in deleted]

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

    last_error = None

    # Tier 1: Local Proxy Turn
    try:
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
        with urllib.request.urlopen(req, timeout=20) as resp:
            resp.read()
    except urllib.error.HTTPError as e:
        last_error = f"Proxy HTTP {e.code}"
    except Exception as e:
        last_error = str(e)

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

    # Tier 2: Direct Agent-Run Fallback
    try:
        start_req = urllib.request.Request(
            "https://www.codebuff.com/api/v1/agent-runs",
            data=json.dumps({"action": "START", "agentId": "mimo/mimo-v2.5"}).encode(),
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0"
            }
        )
        run_id = None
        with urllib.request.urlopen(start_req, timeout=10) as s_resp:
            s_data = json.loads(s_resp.read().decode())
            run_id = s_data.get("runId")

        if run_id:
            finish_req = urllib.request.Request(
                "https://www.codebuff.com/api/v1/agent-runs",
                data=json.dumps({
                    "action": "FINISH",
                    "runId": run_id,
                    "status": "completed",
                    "totalSteps": 1,
                    "directCredits": 0,
                    "totalCredits": 0
                }).encode(),
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0"
                }
            )
            with urllib.request.urlopen(finish_req, timeout=10) as f_resp:
                f_resp.read()
    except urllib.error.HTTPError as e:
        last_error = f"Direct AgentRun HTTP {e.code}"
    except Exception as e:
        last_error = str(e)

    time.sleep(2)
    final_streak = get_streak_info(token)
    if final_streak and final_streak.get("todayUsed"):
        return {
            "name": name,
            "email": email,
            "status": f"🚀 Streak Boosted to {final_streak.get('streak', 0)}d!",
            "streak": final_streak.get("streak", 0),
            "todayUsed": True,
            "lastUsageDate": final_streak.get("lastUsageDate")
        }
    else:
        err_msg = f"❌ Failed ({last_error})" if last_error else "⚡ Turn Sent (Streak Pending Midnight Reset)"
        return {
            "name": name,
            "email": email,
            "status": err_msg,
            "streak": final_streak.get("streak", 0) if final_streak else 0,
            "todayUsed": final_streak.get("todayUsed", False) if final_streak else False,
            "lastUsageDate": final_streak.get("lastUsageDate", "N/A") if final_streak else "N/A"
        }

def run_auto_streak():
    accounts = discover_accounts()
    print("=" * 95)
    print(" 🔥 AUTOMATED FREEBUFF DAILY STREAK BOOSTER 🔥")
    print("=" * 95)

    if not accounts:
        print("No active accounts found.")
        print("Log in or add an account using ./switch add <token> <email>.\n")
        return

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
