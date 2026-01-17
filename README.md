# Dataminer

A OpenSource Project exploring and transforming the massive amounts of personal data in the hands of big tech, relying on the European DSGVO.

## Download and Installation

### For macOS Users

1. **Download the DMG installer**: [Dataminer-1.0.0-macOS.dmg](dist/Dataminer-1.0.0-macOS.dmg)
2. **Install**: 
   - Double-click the downloaded DMG file
   - Drag the Dataminer app to your Applications folder
   - Right-click the app and select "Open" (to bypass Gatekeeper on first run)
3. **Launch**: Find Dataminer in your Applications folder or Launchpad

### For Windows Users

1. **Download the installer**: [Dataminer-1.0.0-Windows-Setup.exe](dist/Dataminer-1.0.0-Windows-Setup.exe) *(available after building on Windows)*
2. **Install**: 
   - Double-click the installer
   - Follow the installation wizard
   - Launch from Start Menu or desktop shortcut

### For Linux Users

1. **Download the AppImage**: [Dataminer.AppImage](dist/Dataminer.AppImage) *(available after building on Linux)*
2. **Install**: 
   - Make the file executable: `chmod +x Dataminer.AppImage`
   - Run directly: `./Dataminer.AppImage`

## Building from Source

If you prefer to build from source or need to create packages for other platforms:

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Quick Build
```bash
# Clone the repository
git clone <repository-url>
cd dataminer

# Run the build script
python3 build.py
```

The build script will automatically:
- Install required dependencies
- Build the executable for your platform
- Create platform-specific installers (DMG for macOS, EXE for Windows, AppImage for Linux)

### Manual Build
```bash
# Install dependencies
pip install -r setup/requirements.txt

# Build executable
pyinstaller --onefile --windowed --add-data=assets:assets --add-data=styles:styles --add-data=converter:converter --hidden-import=progress --name=Dataminer app/main.py
```

## Platform-Specific Build Requirements

### macOS
- Xcode Command Line Tools
- `hdiutil` (included with macOS)

### Windows
- NSIS (for creating installers)
- Microsoft Visual C++ Redistributable

### Linux
- `appimagetool` (for creating AppImages)

## Features

- **User-friendly GUI**: Built with PySide6 for a modern interface
- **Data Processing**: Transform and analyze personal data exports
- **PDF Generation**: Create reports from processed data
- **Cross-platform**: Works on macOS, Windows, and Linux

## Support

For issues, feature requests, or contributions:
- Open an issue on the project repository
- Check the documentation for detailed usage instructions

## License

See LICENSE file for details.