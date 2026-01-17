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
    
    # Create temporary DMG
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

def create_windows_installer():
    """Create an installer for Windows using NSIS."""
    if platform.system() != "Windows":
        return
    
    print("Creating Windows installer...")
    
    exe_path = Path("dist/Dataminer.exe")
    if not exe_path.exists():
        print("Dataminer.exe not found in dist/")
        return
    
    # Create NSIS script
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
    CreateShortCut "$DESKTOP\\${APPNAME}.lnk" "$INSTDIR\\Dataminer.exe"
    CreateDirectory "$SMPROGRAMS\\${APPNAME}"
    CreateShortCut "$SMPROGRAMS\\${APPNAME}\\${APPNAME}.lnk" "$INSTDIR\\Dataminer.exe"
SectionEnd
"""
    
    with open("dist/installer.nsi", "w") as f:
        f.write(nsis_script)
    
    # Try to build with NSIS if available
    try:
        run_command(["makensis", "dist/installer.nsi"])
        print("Windows installer created successfully")
    except FileNotFoundError:
        print("NSIS not found. Install NSIS to create Windows installer.")
        print("Manual installer script created at dist/installer.nsi")

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
    
    print("AppImage structure created. Use appimagetool to create final AppImage.")

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
