#!/usr/bin/env python3
"""
⚡ FREEBUFF ACCOUNT LOGIN & DISCOVERY TOOL (`./login` / `./addaccount`) ⚡
Registers new Codebuff/Freebuff account tokens for Freebuff Desktop & CLI, or captures web sign-in URLs.
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path

SHARED_ACCOUNTS_FILE = os.path.expanduser("~/.config/freebuff-shared-accounts.json")
DESKTOP_STATE_PATH = os.path.expanduser("~/.config/freebuff-desktop/state.json")
CLI_CRED_PATH = os.path.expanduser("~/.config/manicode/credentials.json")
BUFFDESKTOP_DIR = Path(os.path.expanduser("~/myworks/buffdesktop"))

def load_json(filepath):
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except Exception:
        return None

def save_json(filepath, data):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

def register_account(token, email, name=None, set_desktop=True, set_cli=True):
    token = token.strip()
    email = email.strip()
    name = name.strip() if name else email.split("@")[0]
    user_id = f"usr_{abs(hash(token)) % 1000000}"

    acc = {
        "name": name,
        "email": email,
        "token": token,
        "id": user_id,
        "display_name": name
    }

    # 1. Save to shared accounts store
    shared = load_json(SHARED_ACCOUNTS_FILE) or []
    if not isinstance(shared, list):
        shared = []
    
    # Update existing or append new
    updated = False
    for existing in shared:
        if existing.get("email") == email or existing.get("token") == token:
            existing.update(acc)
            updated = True
            break
    if not updated:
        shared.append(acc)
    
    save_json(SHARED_ACCOUNTS_FILE, shared)
    print(f"✅ Registered account in shared vault: {name} ({email})")

    # 2. Optionally set as active Desktop account
    if set_desktop:
        state = load_json(DESKTOP_STATE_PATH) or {}
        if "authSessions" not in state:
            state["authSessions"] = {}
        state["authSessions"]["https://www.codebuff.com"] = {
            "token": token,
            "user": {
                "id": user_id,
                "email": email,
                "name": name
            }
        }
        save_json(DESKTOP_STATE_PATH, state)
        print(f"🖥️  Freebuff Desktop session updated to: {name} ({email})")

        # Restart Desktop app if running
        res = subprocess.run("pgrep -f '@codebufffreebuff-desktop' || pgrep -f 'runner.py'", shell=True, capture_output=True)
        if res.returncode == 0:
            print("🔄 Restarting Freebuff Desktop app...")
            stop_sh = BUFFDESKTOP_DIR / "stop.sh"
            start_sh = BUFFDESKTOP_DIR / "start.sh"
            if stop_sh.exists():
                subprocess.run(f"bash '{stop_sh}'", shell=True)
            if start_sh.exists():
                subprocess.run(f"bash '{start_sh}' >/dev/null 2>&1 &", shell=True)
                print("🚀 Desktop app restarted with new session!")

    # 3. Optionally set as active CLI account
    if set_cli:
        cli_cred = {
            "default": {
                "id": user_id,
                "name": name,
                "email": email,
                "authToken": token,
                "fingerprintId": "enhanced-yVcxCoXlor63JLczcFjF2FWfppwHAl03jKjalt00oJ0",
                "fingerprintHash": "040ad64de309467a7d7ca1bd2d78e1ddc7b2f6571d14a1a917b69a82d4554c44"
            }
        }
        save_json(CLI_CRED_PATH, cli_cred)
        print(f"💻 Freebuff CLI default credentials updated to: {name} ({email})")

    print("\n🎉 Account login & configuration complete!")

def show_web_login_url():
    print("=" * 60)
    print(" 🔗 FREEBUFF DESKTOP WEB SIGN-IN LINK FINDER")
    print("=" * 60)
    
    url_file = BUFFDESKTOP_DIR / "login_url.txt"
    log_file = BUFFDESKTOP_DIR / "auth_links.log"
    
    if url_file.exists() and url_file.stat().st_size > 0:
        print("Latest Captured Sign-In URL:")
        print(url_file.read_text().strip())
    else:
        print("No sign-in URL captured yet.")
        print("💡 Click 'Sign In' inside Freebuff Desktop GUI to capture a sign-in URL!")

    if log_file.exists():
        print("\nRecent Sign-In Links History:")
        try:
            lines = log_file.read_text().strip().splitlines()
            for line in lines[-10:]:
                print(line)
        except Exception:
            pass
    print("=" * 60)

def main():
    parser = argparse.ArgumentParser(description="Freebuff Account Login & Token Registrar")
    parser.add_argument("token", nargs="?", help="Freebuff Auth Token (or 'web' to show web login URL)")
    parser.add_argument("email", nargs="?", help="Account Email Address")
    parser.add_argument("name", nargs="?", help="Account Label / Display Name (optional)")
    parser.add_argument("--web", action="store_true", help="Show captured web login URLs")
    parser.add_argument("--desktop-only", action="store_true", help="Set active for Desktop GUI only")
    parser.add_argument("--cli-only", action="store_true", help="Set active for CLI only")
    args = parser.parse_args()

    if args.web or (args.token and args.token.lower() == "web"):
        show_web_login_url()
        return

    if args.token and args.email:
        set_dt = not args.cli_only
        set_cli = not args.desktop_only
        register_account(args.token, args.email, args.name, set_desktop=set_dt, set_cli=set_cli)
        return

    # Interactive mode
    print("=" * 60)
    print(" ⚡ FREEBUFF ACCOUNT LOGIN / REGISTRAR ⚡")
    print("=" * 60)
    print("Choose action:")
    print("  [1] Register a new Account Token manually")
    print("  [2] View captured Desktop Web Sign-In URL")
    print("  [q] Quit\n")

    try:
        mode = input("Select option (1/2, default 1): ").strip()
        if mode == "2" or mode.lower() == "web":
            show_web_login_url()
            return
        if mode.lower() == "q":
            return

        print("\n--- Enter Account Credentials ---")
        token = input("1. Enter Freebuff Auth Token: ").strip()
        if not token:
            print("Token is required.")
            return

        email = input("2. Enter Account Email: ").strip()
        if not email:
            print("Email is required.")
            return

        name = input("3. Enter Account Display Name / Label (optional): ").strip()

        print("\nTarget Applications:")
        print("  [1] BOTH Desktop & CLI (Recommended)")
        print("  [2] Desktop GUI only")
        print("  [3] CLI / Terminal only")
        target = input("Choice (1-3, default 1): ").strip()

        set_dt = target in ["1", "2", ""]
        set_cli = target in ["1", "3", ""]

        register_account(token, email, name, set_desktop=set_dt, set_cli=set_cli)

    except (KeyboardInterrupt, EOFError):
        print("\nExiting.")

if __name__ == "__main__":
    main()
