#!/usr/bin/env python3
"""
Build script for creating distributable packages of the Dataminer application.
Supports macOS, Windows, and Linux packaging.
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and return the result."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)
    return result

def create_icon():
    """Create app icon from existing assets if needed."""
    assets_dir = Path("assets")
    if not assets_dir.exists():
        return
    
    # For macOS, create .icns if we have a PNG
    if platform.system() == "Darwin":
        png_files = list(assets_dir.glob("*.png"))
        if png_files and not (assets_dir / "icon.icns").exists():
            print("Creating macOS icon from PNG...")
            try:
                # Use the first PNG found as icon
                icon_src = png_files[0]
                # This would require iconutil (macOS) or PIL for cross-platform
                print(f"Note: Convert {icon_src} to icon.icns manually for better results")
            except Exception as e:
                print(f"Could not create icon: {e}")

def build_executable():
    """Build the executable using PyInstaller."""
    print("Building executable with PyInstaller...")
    
    # Install PyInstaller if not available
    try:
        import PyInstaller
    except ImportError:
        print("Installing PyInstaller...")
        run_command([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Clean previous builds
    for dist_dir in ["dist", "build"]:
        if Path(dist_dir).exists():
            shutil.rmtree(dist_dir)
    
    # Check if required directories exist
    required_dirs = ["assets", "styles", "converter"]
    for dir_name in required_dirs:
        if not Path(dir_name).exists():
            print(f"Warning: {dir_name} directory not found")
    
    # Build the executable
    run_command([sys.executable, "-m", "PyInstaller", "--clean", "--onefile", "--windowed", 
                "--add-data=assets:assets", 
                "--add-data=styles:styles", 
                "--add-data=converter:converter",
                "--hidden-import=progress",
                "--name=Dataminer", 
                "app/main.py"])

def create_dmg():
    """Create a DMG installer for macOS."""
    if platform.system() != "Darwin":
        return
    
    print("Creating DMG installer...")
    
    app_path = Path("dist/Dataminer.app")
    if not app_path.exists():
        print("Dataminer.app not found in dist/")
        return
    
    dmg_name = "Dataminer-1.0.0-macOS"
    dmg_path = Path(f"dist/{dmg_name}.dmg")
    
    # Create temporary DMG with both app and scripts
    temp_dmg = Path("dist/temp.dmg")
    run_command([
        "hdiutil", "create", "-volname", "Dataminer", 
        "-srcfolder", "dist/Dataminer.app",
        "-ov", "-format", "UDZO", str(temp_dmg)
    ])
    
    # Create final DMG with proper settings
    run_command([
        "hdiutil", "convert", str(temp_dmg), 
        "-format", "UDZO", "-o", str(dmg_path),
        "-imagekey", "zlib-level=9"
    ])
    
    # Clean up temp DMG
    temp_dmg.unlink()
    print(f"DMG created: {dmg_path}")
    
    # Create installer and uninstaller scripts
    create_macos_installer()
    create_macos_uninstaller()
    
    # Create a DMG that includes the scripts
    create_complete_dmg()

def create_macos_installer():
    """Create macOS installer script."""
    installer_script = """#!/bin/bash
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
"""
    
    with open("dist/install.sh", "w") as f:
        f.write(installer_script)
    
    # Make executable
    os.chmod("dist/install.sh", 0o755)
    print("Created install.sh for macOS")

def create_complete_dmg():
    """Create a complete DMG with app, installer, and uninstaller."""
    print("Creating complete DMG with installer scripts...")
    
    # Create a temporary directory for DMG contents
    dmg_contents = Path("dist/dmg_contents")
    if dmg_contents.exists():
        shutil.rmtree(dmg_contents)
    dmg_contents.mkdir()
    
    # Copy app and scripts to DMG contents
    shutil.copytree("dist/Dataminer.app", dmg_contents / "Dataminer.app")
    shutil.copy("dist/install.sh", dmg_contents / "install.sh")
    shutil.copy("dist/uninstall.sh", dmg_contents / "uninstall.sh")
    
    # Create README for DMG
    readme_content = """# Dataminer Installation

## Quick Install (Recommended)
1. Double-click "install.sh"
2. Follow the prompts
3. Dataminer will be installed to /Applications

## Manual Install
1. Drag Dataminer.app to /Applications folder
2. Right-click and select "Open" on first launch

## Uninstall
1. Double-click "uninstall.sh"
2. Follow the prompts to remove Dataminer

## Security Notice
If you see a security warning on first launch:
- Right-click Dataminer.app
- Select "Open"
- Click "Open" in the dialog
"""
    
    with open(dmg_contents / "README.txt", "w") as f:
        f.write(readme_content)
    
    # Create the final DMG
    dmg_name = "Dataminer-1.0.0-macOS"
    dmg_path = Path(f"dist/{dmg_name}.dmg")
    
    if dmg_path.exists():
        dmg_path.unlink()
    
    run_command([
        "hdiutil", "create", "-volname", "Dataminer", 
        "-srcfolder", str(dmg_contents),
        "-ov", "-format", "UDZO", str(dmg_path),
        "-imagekey", "zlib-level=9"
    ])
    
    # Clean up
    shutil.rmtree(dmg_contents)
    
    print(f"✅ Complete DMG created: {dmg_path}")
    print("DMG contains: Dataminer.app, install.sh, uninstall.sh, README.txt")

def create_macos_uninstaller():
    """Create macOS uninstaller script."""
    uninstaller_script = """#!/bin/bash
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
"""
    
    with open("dist/uninstall.sh", "w") as f:
        f.write(uninstaller_script)
    
    # Make executable
    os.chmod("dist/uninstall.sh", 0o755)
    print("Created uninstall.sh for macOS")

def create_windows_installer():
    """Create an installer for Windows using NSIS."""
    if platform.system() != "Windows":
        return
    
    print("Creating Windows installer...")
    
    exe_path = Path("dist/Dataminer.exe")
    if not exe_path.exists():
        print("Dataminer.exe not found in dist/")
        return
    
    # Create NSIS script with uninstaller
    nsis_script = """
!define APPNAME "Dataminer"
!define VERSION "1.0.0"
!define PUBLISHER "Unit404"

Name "${APPNAME}"
OutFile "Dataminer-1.0.0-Windows-Setup.exe"
InstallDir "$PROGRAMFILES\\${APPNAME}"
RequestExecutionLevel admin

Page directory
Page instfiles

Section "MainSection" SEC01
    SetOutPath "$INSTDIR"
    File "dist\\Dataminer.exe"
    File "dist\\uninstall.exe"
    
    CreateShortCut "$DESKTOP\\${APPNAME}.lnk" "$INSTDIR\\Dataminer.exe"
    CreateDirectory "$SMPROGRAMS\\${APPNAME}"
    CreateShortCut "$SMPROGRAMS\\${APPNAME}\\${APPNAME}.lnk" "$INSTDIR\\Dataminer.exe"
    CreateShortCut "$SMPROGRAMS\\${APPNAME}\\Uninstall ${APPNAME}.lnk" "$INSTDIR\\uninstall.exe"
    
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "DisplayName" "${APPNAME}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "UninstallString" "$INSTDIR\\uninstall.exe"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "DisplayVersion" "${VERSION}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "Publisher" "${PUBLISHER}"
SectionEnd
"""
    
    with open("dist/installer.nsi", "w") as f:
        f.write(nsis_script)
    
    # Create uninstaller
    create_windows_uninstaller()
    
    # Try to build with NSIS if available
    try:
        run_command(["makensis", "dist/installer.nsi"])
        print("Windows installer created successfully")
    except FileNotFoundError:
        print("NSIS not found. Install NSIS to create Windows installer.")
        print("Manual installer script created at dist/installer.nsi")

def create_windows_uninstaller():
    """Create Windows uninstaller executable."""
    uninstaller_script = """#!/usr/bin/env python3
# Dataminer Uninstaller for Windows

import os
import sys
import shutil
from pathlib import Path

def main():
    print("Dataminer Uninstaller")
    print("===================")
    
    # Get installation directory from registry or default
    install_dir = Path(os.environ.get("PROGRAMFILES", "C:\\Program Files")) / "Dataminer"
    
    if not install_dir.exists():
        install_dir = Path(os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)")) / "Dataminer"
    
    if not install_dir.exists():
        print("Dataminer installation not found.")
        return
    
    # Remove application files
    try:
        shutil.rmtree(install_dir)
        print(f"✅ Removed {install_dir}")
    except Exception as e:
        print(f"❌ Could not remove {install_dir}: {e}")
    
    # Remove shortcuts
    desktop = Path.home() / "Desktop"
    for shortcut in desktop.glob("Dataminer*.lnk"):
        try:
            shortcut.unlink()
            print(f"✅ Removed shortcut: {shortcut}")
        except Exception as e:
            print(f"❌ Could not remove shortcut {shortcut}: {e}")
    
    # Remove Start Menu shortcuts
    start_menu = Path(os.environ.get("PROGRAMDATA", "C:\\ProgramData")) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
    for shortcut in start_menu.glob("Dataminer*.lnk"):
        try:
            shortcut.unlink()
            print(f"✅ removed Start Menu shortcut: {shortcut}")
        except Exception as e:
            print(f"❌ Could not remove Start Menu shortcut {shortcut}: {e}")
    
    print("\\nUninstallation complete!")

if __name__ == "__main__":
    main()
"""
    
    with open("dist/uninstall.py", "w") as f:
        f.write(uninstaller_script)
    
    print("Created uninstall.py for Windows")

def create_appimage():
    """Create an AppImage for Linux."""
    if platform.system() != "Linux":
        return
    
    print("Creating AppImage for Linux...")
    
    exe_path = Path("dist/Dataminer")
    if not exe_path.exists():
        print("Dataminer executable not found in dist/")
        return
    
    # Create AppImage directory structure
    appdir = Path("dist/Dataminer.AppDir")
    if appdir.exists():
        shutil.rmtree(appdir)
    
    appdir.mkdir()
    
    # Copy executable
    shutil.copy(exe_path, appdir / "AppRun")
    (appdir / "AppRun").chmod(0o755)
    
    # Create desktop file
    desktop_entry = """[Desktop Entry]
Type=Application
Name=Dataminer
Comment=Data transformation tool
Exec=AppRun
Icon=dataminer
Categories=Utility;
"""
    
    with open(appdir / "Dataminer.desktop", "w") as f:
        f.write(desktop_entry)
    
    # Create AppRun script
    apprun_script = """#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")"
export LD_LIBRARY_PATH="${HERE}/usr/lib:${LD_LIBRARY_PATH}"
exec "${HERE}/usr/bin/Dataminer" "$@"
"""
    
    with open(appdir / "AppRun", "w") as f:
        f.write(apprun_script)
    (appdir / "AppRun").chmod(0o755)
    
    # Create uninstaller
    create_linux_uninstaller()
    
    print("AppImage structure created. Use appimagetool to create final AppImage.")

def create_linux_uninstaller():
    """Create Linux uninstaller script."""
    uninstaller_script = """#!/bin/bash
# Dataminer Uninstaller for Linux

echo "Dataminer Uninstaller"
echo "===================="

DESKTOP_ENTRY="$HOME/.local/share/applications/Dataminer.desktop"
DESKTOP_ICON="$HOME/Desktop/Dataminer.AppImage"
LOCAL_BIN="$HOME/bin/Dataminer"
APPIMAGE_FILE="$HOME/Dataminer.AppImage"

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

if [ -f "$APPIMAGE_FILE" ]; then
    echo "Removing AppImage..."
    rm "$APPIMAGE_FILE"
    echo "✅ Removed $APPIMAGE_FILE"
fi

echo ""
echo "Uninstallation complete!"
"""
    
    with open("dist/uninstall.sh", "w") as f:
        f.write(uninstaller_script)
    
    # Make executable
    os.chmod("dist/uninstall.sh", 0o755)
    print("Created uninstall.sh for Linux")

def main():
    """Main build process."""
    print(f"Building Dataminer for {platform.system()}...")
    
    # Create icon if needed
    create_icon()
    
    # Build executable
    build_executable()
    
    # Platform-specific packaging
    if platform.system() == "Darwin":
        create_dmg()
    elif platform.system() == "Windows":
        create_windows_installer()
    elif platform.system() == "Linux":
        create_appimage()
    
    print("Build completed!")
    print("Check the 'dist' directory for distributable packages.")

if __name__ == "__main__":
    main()
