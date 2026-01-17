# Dataminer - Installation Guide

This guide provides step-by-step installation instructions for Dataminer on macOS and Windows.

## 📥 Download

Download the latest version from the official website or repository:
- **macOS**: `Dataminer-1.0.0-macOS.dmg`
- **Windows**: `Dataminer-1.0.0-Windows-Setup.exe`

---

## 🍎 macOS Installation

### System Requirements
- macOS 10.15 (Catalina) or later
- Apple Silicon (M1/M2) or Intel Mac
- 100MB free disk space
- 4GB RAM (recommended)

### Installation Steps

#### Method 1: DMG Installer (Recommended)

1. **Download the DMG file**
   - Download `Dataminer-1.0.0-macOS.dmg` from the official website

2. **Open the DMG file**
   - Double-click the downloaded `.dmg` file
   - A new window will open showing the Dataminer app

3. **Install the application**
   - Drag the `Dataminer` app icon to your `Applications` folder
   - Wait for the copy process to complete

4. **First Launch**
   - Open `Finder` → `Applications`
   - Find `Dataminer` and right-click it
   - Select **"Open"** (this bypasses Gatekeeper security on first run)
   - Click **"Open"** in the security dialog
   - The app will launch and you can now use it normally

5. **Create shortcut (optional)**
   - Drag Dataminer from Applications to your Dock for quick access

#### Method 2: Command Line Installation

```bash
# Mount the DMG
hdiutil attach Dataminer-1.0.0-macOS.dmg

# Copy to Applications
cp -r "/Volumes/Dataminer/Dataminer.app" /Applications/

# Unmount
hdiutil detach "/Volumes/Dataminer"
```

### Troubleshooting macOS

#### "Damaged" or "Unidentified Developer" Error
If you see this error:
```
"Dataminer" cannot be opened because the developer cannot be verified.
```

**Solution:**
1. Right-click the app and select **"Open"**
2. Click **"Open"** in the confirmation dialog
3. This only needs to be done once

#### App Crashes on Launch
1. Ensure you're on macOS 10.15 or later
2. Check you have at least 4GB free RAM
3. Try restarting your Mac
4. Contact support if issues persist

---

## 🪟 Windows Installation

### System Requirements
- Windows 10 (version 1903) or later
- Windows 11 (all versions)
- 100MB free disk space
- 4GB RAM (recommended)
- .NET Framework 4.7.2 or later (usually pre-installed)

### Installation Steps

#### Method 1: GUI Installer (Recommended)

1. **Download the installer**
   - Download `Dataminer-1.0.0-Windows-Setup.exe` from the official website

2. **Run the installer**
   - Double-click the downloaded `.exe` file
   - Windows may show a security warning - click **"More info"** then **"Run anyway"**

3. **Follow the installation wizard**
   - Welcome screen: Click **"Next"**
   - License agreement: Read and click **"I Agree"**
   - Installation location: Accept default or choose custom location
   - Start menu: Choose folder (default is recommended)
   - Ready to install: Click **"Install"**

4. **Complete installation**
   - Wait for the installation to complete
   - Click **"Finish"** to close the installer
   - Ensure **"Launch Dataminer"** is checked if you want to start immediately

5. **Launch the application**
   - From Start Menu: `Start` → `Dataminer` → `Dataminer`
   - From Desktop: Double-click the desktop shortcut (if created)
   - From File Explorer: Navigate to installation folder and run `Dataminer.exe`

#### Method 2: Silent Installation

For system administrators or automated deployment:

```cmd
# Run installer silently
Dataminer-1.0.0-Windows-Setup.exe /S

# Install to custom directory
Dataminer-1.0.0-Windows-Setup.exe /S /D=C:\Custom\Path\Dataminer
```

### Troubleshooting Windows

#### Windows Defender Warning
If Windows Defender blocks the installation:
1. Click **"More info"** in the security dialog
2. Click **"Run anyway"**
3. This is normal for new applications

#### "This app can't run on your PC" Error
1. Ensure you're running Windows 10 version 1903 or later
2. Check if your system is 64-bit (Dataminer requires 64-bit Windows)
3. Try running as Administrator

#### Application Won't Start
1. Install Microsoft Visual C++ Redistributable (included in installer)
2. Update Windows to the latest version
3. Restart your computer
4. Try running as Administrator

#### Missing .NET Framework
If you get a .NET Framework error:
1. Download .NET Framework 4.7.2 from Microsoft's website
2. Install it and restart your computer
3. Try launching Dataminer again

---

## 🔧 Post-Installation Setup

### First Run Configuration

1. **Launch the application** using the method above
2. **Welcome screen** will appear with basic instructions
3. **Choose default settings** or customize as needed
4. **Grant permissions** when prompted for file access

### Updating the Application

#### macOS
1. Download the latest DMG from the website
2. Follow installation steps - it will automatically update your existing version

#### Windows
1. Download the latest installer from the website
2. Run the installer - it will automatically update your existing version
3. Or use built-in update checker (if available in future versions)

---

## 🗑️ Uninstallation

### macOS
1. **Automatic Uninstall** (Recommended):
   - Open Terminal and run: `./uninstall.sh` (from the DMG location)
   - Or download and run the uninstall script

2. **Manual Uninstall**:
   - Open `Finder` → `Applications`
   - Drag `Dataminer` to the Trash
   - Empty Trash to complete removal
   - Optionally remove preferences from `~/Library/Preferences/`

3. **Complete Cleanup**:
   ```bash
   # Remove app
   rm -rf "/Applications/Dataminer.app"
   
   # Remove preferences
   rm -f "$HOME/Library/Preferences/com.unit404.dataminer.plist"
   
   # Remove app support
   rm -rf "$HOME/Library/Application Support/Dataminer"
   
   # Remove cache
   rm -rf "$HOME/Library/Caches/com.unit404.dataminer"
   ```

### Windows
1. **Automatic Uninstall** (Recommended):
   - Open **Control Panel** → **Programs and Features**
   - Find "Dataminer" and click **"Uninstall"**
   - Or use the "Uninstall Dataminer" shortcut in Start Menu

2. **Manual Uninstall**:
   - Open `Settings` → `Apps` → `Apps & features`
   - Find `Dataminer` in the list
   - Click **"Uninstall"** and follow the prompts

3. **Complete Cleanup**:
   - Delete installation folder (usually `C:\Program Files\Dataminer`)
   - Remove desktop shortcut
   - Clean registry entries (optional)

### Linux
1. **Automatic Uninstall** (Recommended):
   - Run the uninstall script: `./uninstall.sh`
   - Or remove the AppImage: `rm Dataminer.AppImage`

2. **Manual Uninstall**:
   - Remove AppImage file
   - Remove desktop entry: `rm ~/.local/share/applications/Dataminer.desktop`
   - Remove desktop shortcut if created

3. **Complete Cleanup**:
   ```bash
   # Remove desktop entry
   rm -f "$HOME/.local/share/applications/Dataminer.desktop"
   
   # Remove AppImage
   rm -f "$HOME/Dataminer.AppImage"
   
   # Remove desktop shortcut
   rm -f "$HOME/Desktop/Dataminer.AppImage"
   
   # Remove local binary
   rm -f "$HOME/bin/Dataminer"
   ```

---

## 📞 Support

If you encounter issues during installation:

### Check These First
- Verify your system meets the minimum requirements
- Ensure you downloaded the correct version for your OS
- Try restarting your computer before reinstalling

### Get Help
- **Documentation**: Check the main README.md file
- **Issues**: Report problems on the project repository
- **Email**: Contact unit@404.net for technical support
- **Community**: Join discussions in the project forums

### Include in Support Requests
- Your operating system and version
- Dataminer version you're trying to install
- Any error messages you received
- Steps you've already tried

---

## 🔒 Security & Verification

### Verify Download Integrity
Each release includes checksums for file verification:

**macOS:**
```bash
shasum -a 256 Dataminer-1.0.0-macOS.dmg
```

**Windows (PowerShell):**
```powershell
Get-FileHash Dataminer-1.0.0-Windows-Setup.exe -Algorithm SHA256
```

Compare the output with the checksums provided in `checksums.txt` on the download page.

### Security Notes
- Dataminer only accesses files you explicitly select
- No data is sent to external servers without your consent
- The application is open source for security transparency

---

## 📚 Additional Resources

- **Main README**: Complete feature documentation
- **Source Code**: Available on the project repository
- **Contributing**: Guidelines for developers
- **Changelog**: Version history and updates

---

**Last Updated**: January 2026  
**Version**: 1.0.0  
**License**: See LICENSE file for details
