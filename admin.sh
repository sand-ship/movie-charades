#!/bin/bash
# Quick admin dashboard access

ADMIN_KEY="ushermein114!"
URL="https://movie-charades.onrender.com/admin?key=${ADMIN_KEY}"

if [ "$1" = "open" ] || [ "$1" = "browser" ]; then
    # Try to open in browser
    if command -v open &> /dev/null; then
        open "$URL"
    elif command -v xdg-open &> /dev/null; then
        xdg-open "$URL"
    else
        echo "Admin URL: $URL"
    fi
else
    echo "Admin URL: $URL"
    echo ""
    echo "Usage: $0 [open|browser]"
    echo "  - Display the admin link (default)"
    echo "  - open: Open in default browser"
fi
