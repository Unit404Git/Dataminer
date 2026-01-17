#!/usr/bin/env python3
"""
Uninstall script for Dataminer.
This script removes the application and its associated files.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def get_app_paths():
    """Get common installation paths for Dataminer."""
    paths = {
        'macos': [
            Path.home() / "Applications" / "Dataminer.app",
            Path.home() / "Desktop" / "Dataminer.app",
        ],
        'windows': [
            Path(os.environ.get("PROGRAMFILES", "C:\\Program Files")) / "Dataminer",
            Path(os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)")) / "Dataminer",
            Path.home() / "Desktop" / "Dataminer.exe",
            Path.home() / "AppData" / "Local" / "Dataminer",
        ],
        'linux': [
            Path.home() / ".local" / "share" / "applications" / "Dataminer.desktop",
            Path.home() / "Desktop" / "Dataminer.AppImage",
            Path.home() / "bin" / "Dataminer",
            Path("/opt") / "Dataminer",
        ]
    }
    
    platform = sys.platform
    if platform == "darwin":
        return paths['macos']
    elif platform == "win32":
        return paths['windows']
    else:
        return paths['linux']

def remove_shortcuts():
    """Remove desktop shortcuts and menu entries."""
    platform = sys.platform
    
    if platform == "darwin":
        # Remove Dock icon (this is more complex, usually just remove from Dock manually)
        pass
    elif platform == "win32":
        # Remove desktop shortcuts
        desktop = Path.home() / "Desktop"
        for shortcut in desktop.glob("Dataminer*.lnk"):
            try:
                shortcut.unlink()
                print(f"Removed shortcut: {shortcut}")
            except Exception as e:
                print(f"Could not remove shortcut {shortcut}: {e}")
        
        # Remove Start Menu shortcuts
        start_menu = Path(os.environ.get("PROGRAMDATA", "C:\\ProgramData")) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
        for shortcut in start_menu.glob("Dataminer*.lnk"):
            try:
                shortcut.unlink()
                print(f"Removed Start Menu shortcut: {shortcut}")
            except Exception as e:
                print(f"Could not remove Start Menu shortcut {shortcut}: {e}")
    
    elif platform == "linux":
        # Remove desktop entries
        desktop_dir = Path.home() / ".local" / "share" / "applications"
        desktop_file = desktop_dir / "Dataminer.desktop"
        if desktop_file.exists():
            try:
                desktop_file.unlink()
                print(f"Removed desktop entry: {desktop_file}")
            except Exception as e:
                print(f"Could not remove desktop entry {desktop_file}: {e}")

def remove_application_files():
    """Remove the main application files."""
    removed_files = []
    failed_files = []
    
    app_paths = get_app_paths()
    
    for path in app_paths:
        if path.exists():
            try:
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
                removed_files.append(str(path))
                print(f"✅ Removed: {path}")
            except Exception as e:
                failed_files.append((str(path), str(e)))
                print(f"❌ Could not remove {path}: {e}")
    
    return removed_files, failed_files

def remove_user_data():
    """Remove user data and preferences (optional)."""
    user_data_paths = {
        'macos': [
            Path.home() / "Library" / "Preferences" / "com.unit404.dataminer.plist",
            Path.home() / "Library" / "Application Support" / "Dataminer",
            Path.home() / "Library" / "Caches" / "com.unit404.dataminer",
        ],
        'windows': [
            Path.home() / "AppData" / "Local" / "Dataminer",
            Path.home() / "AppData" / "Roaming" / "Dataminer",
            Path.home() / "AppData" / "Local" / "com.unit404.dataminer",
        ],
        'linux': [
            Path.home() / ".local" / "share" / "Dataminer",
            Path.home() / ".config" / "Dataminer",
            Path.home() / ".cache" / "Dataminer",
        ]
    }
    
    platform = sys.platform
    if platform == "darwin":
        paths = user_data_paths['macos']
    elif platform == "win32":
        paths = user_data_paths['windows']
    else:
        paths = user_data_paths['linux']
    
    removed_data = []
    failed_data = []
    
    for path in paths:
        if path.exists():
            try:
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
                removed_data.append(str(path))
                print(f"✅ Removed user data: {path}")
            except Exception as e:
                failed_data.append((str(path), str(e)))
                print(f"❌ Could not remove user data {path}: {e}")
    
    return removed_data, failed_data

def create_uninstaller():
    """Create a platform-specific uninstaller executable."""
    platform = sys.platform
    
    if platform == "win32":
        # Create NSIS uninstaller script
        uninstaller_script = """
!define APPNAME "Dataminer"
!define VERSION "1.0.0"

Name "${APPNAME} Uninstaller"
OutFile "uninstall.exe"
InstallDir "$PROGRAMFILES\\${APPNAME}"
RequestExecutionLevel admin

Page instfiles

Section "Uninstall"
    Delete "$INSTDIR\\Dataminer.exe"
    Delete "$INSTDIR\\uninstall.exe"
    RMDir "$INSTDIR"
    
    Delete "$DESKTOP\\${APPNAME}.lnk"
    Delete "$SMPROGRAMS\\${APPNAME}\\${APPNAME}.lnk"
    RMDir "$SMPROGRAMS\\${APPNAME}"
    
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}"
SectionEnd
"""
        
        with open("uninstall.nsi", "w") as f:
            f.write(uninstaller_script)
        
        print("Created uninstall.nsi for Windows")
        print("Run with: makensis uninstall.nsi")
    
    elif platform == "darwin":
        # Create macOS uninstaller script
        uninstaller_script = """#!/bin/bash
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
"""
        
        with open("uninstall.sh", "w") as f:
            f.write(uninstaller_script)
        
        # Make executable
        os.chmod("uninstall.sh", 0o755)
        print("Created uninstall.sh for macOS")
    
    else:
        # Create Linux uninstaller script
        uninstaller_script = """#!/bin/bash
# Dataminer Uninstaller for Linux

echo "Dataminer Uninstaller"
echo "===================="

DESKTOP_ENTRY="$HOME/.local/share/applications/Dataminer.desktop"
DESKTOP_ICON="$HOME/Desktop/Dataminer.AppImage"
LOCAL_BIN="$HOME/bin/Dataminer"

if [ -f "$DESKTOP_ENTRY" ]; then
    echo "Removing desktop entry..."
    rm "$DESKTOP_ENTRY"
    echo "✅ Removed $DESKTOP_ENTRY"
fi

if [ -f "$DESKTOP_ICON" ]; then
    echo "Removing desktop icon..."
    rm "$DESKTOP_ICON"
    echo "✅ Removed $DESKTOP_ICON"
fi

if [ -f "$LOCAL_BIN" ]; then
    echo "Removing local binary..."
    rm "$LOCAL_BIN"
    echo "✅ Removed $LOCAL_BIN"
fi

echo ""
echo "Uninstallation complete!"
"""
        
        with open("uninstall.sh", "w") as f:
            f.write(uninstaller_script)
        
        # Make executable
        os.chmod("uninstall.sh", 0o755)
        print("Created uninstall.sh for Linux")

def main():
    """Main uninstall process."""
    print("=== Dataminer Uninstaller ===")
    print("This will remove Dataminer from your system.")
    print()
    
    # Ask for confirmation
    response = input("Do you want to continue? (y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("Uninstallation cancelled.")
        return
    
    print("\n🗑️  Removing application files...")
    removed_files, failed_files = remove_application_files()
    
    print("\n🔗 Removing shortcuts...")
    remove_shortcuts()
    
    # Ask about user data
    print("\n📁 Remove user data and preferences?")
    response = input("This will remove your settings and saved data. Continue? (y/N): ").strip().lower()
    if response in ['y', 'yes']:
        removed_data, failed_data = remove_user_data()
    else:
        removed_data, failed_data = [], []
        print("User data preserved.")
    
    # Summary
    print("\n=== Uninstallation Summary ===")
    if removed_files:
        print(f"✅ Removed {len(removed_files)} application files:")
        for file in removed_files:
            print(f"   - {file}")
    
    if failed_files:
        print(f"❌ Could not remove {len(failed_files)} files:")
        for file, error in failed_files:
            print(f"   - {file}: {error}")
    
    if removed_data:
        print(f"✅ Removed {len(removed_data)} user data files:")
        for file in removed_data:
            print(f"   - {file}")
    
    if failed_data:
        print(f"❌ Could not remove {len(failed_data)} user data files:")
        for file, error in failed_data:
            print(f"   - {file}: {error}")
    
    if not removed_files and not removed_data:
        print("No Dataminer files found to remove.")
    else:
        print("\n✅ Uninstallation completed!")
        print("Note: You may need to manually remove any remaining shortcuts or restart your computer.")

if __name__ == "__main__":
    # Check if we should create uninstaller or run it
    if len(sys.argv) > 1 and sys.argv[1] == "--create":
        create_uninstaller()
    else:
        main()
