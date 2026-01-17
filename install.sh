#!/bin/bash
# Dataminer Installer for macOS

echo "Dataminer Installer"
echo "=================="

# Source app location (in DMG)
SOURCE_APP="$(dirname "$0")/Dataminer.app"

# Target installation location
TARGET_APP="/Applications/Dataminer.app"

# Check if source app exists
if [ ! -d "$SOURCE_APP" ]; then
    echo "❌ Error: Dataminer.app not found in the same directory as this installer"
    echo "Please ensure both Dataminer.app and install.sh are in the same location"
    exit 1
fi

echo "Installing Dataminer to /Applications..."

# Check if app already exists
if [ -d "$TARGET_APP" ]; then
    echo "⚠️  Dataminer is already installed at $TARGET_APP"
    read -p "Do you want to replace it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 0
    fi
    
    echo "Removing existing installation..."
    rm -rf "$TARGET_APP"
fi

# Copy app to Applications
echo "Copying Dataminer.app to /Applications..."
cp -R "$SOURCE_APP" "$TARGET_APP"

# Check if copy was successful
if [ -d "$TARGET_APP" ]; then
    echo "✅ Installation completed successfully!"
    echo ""
    echo "🚀 To launch Dataminer:"
    echo "   1. Open Finder → Applications"
    echo "   2. Double-click Dataminer"
    echo "   3. If you see a security warning, right-click and select 'Open'"
    echo ""
    echo "📁 Installation location: $TARGET_APP"
    echo "🗑️  To uninstall: Run uninstall.sh from the DMG"
else
    echo "❌ Installation failed!"
    echo "Please check file permissions and try again."
    exit 1
fi

# Ask if user wants to launch app now
echo ""
read -p "Would you like to launch Dataminer now? (Y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    echo "Launching Dataminer..."
    open "$TARGET_APP"
fi
