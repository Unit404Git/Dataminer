#!/bin/bash
# Dataminer Uninstaller for macOS

echo "Dataminer Uninstaller"
echo "===================="

APP_PATH="/Applications/Dataminer.app"
USER_PREFS="$HOME/Library/Preferences/com.unit404.dataminer.plist"
APP_SUPPORT="$HOME/Library/Application Support/Dataminer"
CACHE="$HOME/Library/Caches/com.unit404.dataminer"

if [ -d "$APP_PATH" ]; then
    echo "Removing application..."
    rm -rf "$APP_PATH"
    echo "✅ Removed $APP_PATH"
else
    echo "Application not found at $APP_PATH"
fi

if [ -f "$USER_PREFS" ]; then
    echo "Removing preferences..."
    rm "$USER_PREFS"
    echo "✅ Removed $USER_PREFS"
fi

if [ -d "$APP_SUPPORT" ]; then
    echo "Removing application support..."
    rm -rf "$APP_SUPPORT"
    echo "✅ Removed $APP_SUPPORT"
fi

if [ -d "$CACHE" ]; then
    echo "Removing cache..."
    rm -rf "$CACHE"
    echo "✅ Removed $CACHE"
fi

echo ""
echo "Uninstallation complete!"
echo "Note: You may need to manually remove Dataminer from your Dock."
