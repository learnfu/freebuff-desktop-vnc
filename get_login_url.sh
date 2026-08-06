#!/usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "============================================================"
echo "🔗 FREEBUFF DESKTOP SIGN-IN LINK FINDER"
echo "============================================================"

if [ -f "$DIR/login_url.txt" ] && [ -s "$DIR/login_url.txt" ]; then
    echo "Latest Sign-In URL:"
    cat "$DIR/login_url.txt"
else
    echo "No Sign-In URL captured yet."
    echo "Click 'Sign In' inside the Freebuff Desktop GUI, and run this script again!"
fi

echo ""
if [ -f "$DIR/auth_links.log" ]; then
    echo "Recent Captured Links History:"
    tail -n 10 "$DIR/auth_links.log"
fi
echo "============================================================"
