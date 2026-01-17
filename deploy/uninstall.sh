#!/bin/bash
# Dataminer Uninstaller for macOS

echo "Dataminer Uninstaller"
echo "===================="

# Possible installation locations
APP_LOCATIONS=(
    "/Applications/Dataminer.app"
    "$HOME/Applications/Dataminer.app"
    "$(dirname "$0")/Dataminer.app"
    "$HOME/Desktop/Dataminer.app"
    "$HOME/Downloads/Dataminer.app"
)

# User data locations
USER_PREFS="$HOME/Library/Preferences/com.unit404.dataminer.plist"
APP_SUPPORT="$HOME/Library/Application Support/Dataminer"
CACHE="$HOME/Library/Caches/com.unit404.dataminer"

# Find and remove app
APP_FOUND=false
for APP_PATH in "${APP_LOCATIONS[@]}"; do
    if [ -d "$APP_PATH" ]; then
        echo "Removing application from $APP_PATH..."
        rm -rf "$APP_PATH"
        echo "✅ Removed $APP_PATH"
        APP_FOUND=true
    fi
done

if [ "$APP_FOUND" = false ]; then
    echo "No Dataminer.app found in standard locations."
    echo "Searching system-wide..."
    
    # Search entire system for Dataminer.app
    SYSTEM_APPS=$(find /Users -name "Dataminer.app" -type d 2>/dev/null | grep -v "/Library/Developer/CoreSimulator/Devices")
    
    if [ -n "$SYSTEM_APPS" ]; then
        echo "Found Dataminer.app at:"
        echo "$SYSTEM_APPS"
        echo ""
        read -p "Do you want to remove these locations? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "$SYSTEM_APPS" | while read -r line; do
                if [ -d "$line" ]; then
                    echo "Removing $line..."
                    rm -rf "$line"
                    echo "✅ Removed $line"
                fi
            done
        fi
    else
        echo "No Dataminer.app installations found."
    fi
fi

# Remove user data
echo ""
echo "Removing user data..."

if [ -f "$USER_PREFS" ]; then
    echo "Removing preferences..."
    rm "$USER_PREFS"
    echo "✅ Removed $USER_PREFS"
else
    echo "Preferences not found at $USER_PREFS"
fi

if [ -d "$APP_SUPPORT" ]; then
    echo "Removing application support..."
    rm -rf "$APP_SUPPORT"
    echo "✅ Removed $APP_SUPPORT"
else
    echo "Application support not found at $APP_SUPPORT"
fi

if [ -d "$CACHE" ]; then
    echo "Removing cache..."
    rm -rf "$CACHE"
    echo "✅ Removed $CACHE"
else
    echo "Cache not found at $CACHE"
fi

echo ""
echo "Uninstallation complete!"
echo "Note: You may need to manually remove Dataminer from your Dock."
