#!/usr/bin/env python3
"""
Deployment script for creating distributable packages and preparing for web deployment.
This script handles the complete build and deployment pipeline.
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path
import zipfile
import hashlib

def get_file_hash(filepath):
    """Calculate SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()

def create_release_notes():
    """Create release notes file."""
    notes = """# Dataminer v1.0.0 Release Notes

## Installation Instructions

### macOS
- Download `Dataminer-1.0.0-macOS.dmg`
- Double-click to mount and drag to Applications
- Right-click and "Open" on first launch to bypass Gatekeeper

### Windows  
- Download `Dataminer-1.0.0-Windows-Setup.exe`
- Run installer and follow prompts
- Launch from Start Menu

### Linux
- Download `Dataminer-1.0.0-Linux.AppImage`
- Make executable: `chmod +x Dataminer-1.0.0-Linux.AppImage`
- Run directly: `./Dataminer-1.0.0-Linux.AppImage`

## System Requirements
- **macOS**: 10.15 (Catalina) or later
- **Windows**: Windows 10 or later  
- **Linux**: Most modern distributions (Ubuntu 18.04+, Fedora 30+, etc.)

## What's New
- Initial release with core data transformation capabilities
- User-friendly GUI interface
- PDF report generation
- Cross-platform support

## File Hashes (for verification)
"""
    return notes

def build_all_platforms():
    """Build packages for all platforms (requires cross-platform build environment)."""
    print("Building packages for current platform...")
    
    # Run the main build script
    result = subprocess.run([sys.executable, "build.py"], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Build failed: {result.stderr}")
        return False
    
    print("Build completed successfully!")
    return True

def create_deployment_package():
    """Create a deployment package with all distributables."""
    dist_dir = Path("dist")
    deploy_dir = Path("deploy")
    
    if not dist_dir.exists():
        print("No dist directory found. Run build first.")
        return False
    
    # Clean and create deploy directory
    if deploy_dir.exists():
        shutil.rmtree(deploy_dir)
    deploy_dir.mkdir()
    
    # Copy all distributables
    files_copied = []
    for file_path in dist_dir.iterdir():
        if file_path.is_file() and not file_path.name.startswith('.'):
            dest = deploy_dir / file_path.name
            shutil.copy2(file_path, dest)
            files_copied.append(dest)
    
    # Create release notes with file hashes
    notes = create_release_notes()
    for file_path in files_copied:
        file_hash = get_file_hash(file_path)
        notes += f"\n{file_path.name}: {file_hash}"
    
    with open(deploy_dir / "RELEASE_NOTES.txt", "w") as f:
        f.write(notes)
    
    # Create checksums file
    with open(deploy_dir / "checksums.txt", "w") as f:
        for file_path in files_copied:
            file_hash = get_file_hash(file_path)
            f.write(f"{file_hash}  {file_path.name}\n")
    
    print(f"Deployment package created in {deploy_dir}/")
    print(f"Files included: {len(files_copied)}")
    
    return True

def create_web_package():
    """Create a web-ready package with download structure."""
    deploy_dir = Path("deploy")
    web_dir = deploy_dir / "web"
    
    if not deploy_dir.exists():
        print("Deploy directory not found. Run create_deployment_package first.")
        return False
    
    # Create web directory structure
    web_dir.mkdir(exist_ok=True)
    
    # Create download page
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dataminer - Download</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .download-section { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }
        .download-btn { display: inline-block; padding: 12px 24px; background: #007cba; color: white; text-decoration: none; border-radius: 4px; margin: 10px 0; }
        .download-btn:hover { background: #005a8b; }
        .platform { font-weight: bold; color: #333; }
        .file-info { font-size: 0.9em; color: #666; margin: 5px 0; }
    </style>
</head>
<body>
    <h1>Dataminer - Download</h1>
    <p>Dataminer is an OpenSource project for exploring and transforming personal data from big tech companies.</p>
    
    <div class="download-section">
        <h2><span class="platform">macOS</span></h2>
        <p>For macOS 10.15 (Catalina) or later</p>
        <a href="Dataminer-1.0.0-macOS.dmg" class="download-btn">Download for macOS</a>
        <div class="file-info">Format: DMG Installer | Size: ~40MB</div>
    </div>
    
    <div class="download-section">
        <h2><span class="platform">Windows</span></h2>
        <p>For Windows 10 or later</p>
        <a href="Dataminer-1.0.0-Windows-Setup.exe" class="download-btn" style="background: #ccc;">Download for Windows (Coming Soon)</a>
        <div class="file-info">Format: EXE Installer | Size: ~45MB</div>
    </div>
    
    <div class="download-section">
        <h2><span class="platform">Linux</span></h2>
        <p>For most modern Linux distributions</p>
        <a href="Dataminer-1.0.0-Linux.AppImage" class="download-btn" style="background: #ccc;">Download for Linux (Coming Soon)</a>
        <div class="file-info">Format: AppImage | Size: ~42MB</div>
    </div>
    
    <h2>Installation Instructions</h2>
    <p>Please refer to the <a href="RELEASE_NOTES.txt">Release Notes</a> for detailed installation instructions and system requirements.</p>
    
    <h2>Verification</h2>
    <p>You can verify the integrity of downloaded files using the checksums provided in <a href="checksums.txt">checksums.txt</a></p>
</body>
</html>"""
    
    with open(web_dir / "index.html", "w") as f:
        f.write(html_content)
    
    print(f"Web package created at {web_dir}/")
    print("Upload the contents of this directory to your web server.")
    
    return True

def main():
    """Main deployment process."""
    print("=== Dataminer Deployment Pipeline ===")
    
    # Step 1: Build packages
    if not build_all_platforms():
        print("Build failed. Exiting.")
        return
    
    # Step 2: Create deployment package
    if not create_deployment_package():
        print("Deployment package creation failed. Exiting.")
        return
    
    # Step 3: Create web package
    if not create_web_package():
        print("Web package creation failed. Exiting.")
        return
    
    print("\n=== Deployment Complete ===")
    print("1. Distributable packages are in 'dist/'")
    print("2. Deployment package is in 'deploy/'")
    print("3. Web-ready files are in 'deploy/web/'")
    print("\nTo deploy:")
    print("- Upload 'deploy/web/' contents to your website")
    print("- Or directly link to files in 'deploy/' for downloads")

if __name__ == "__main__":
    main()
