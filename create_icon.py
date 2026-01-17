#!/usr/bin/env python3
"""
Script to create app icons for Dataminer.
Creates .icns (macOS), .ico (Windows), and .png (Linux) icons.
"""

import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import subprocess

def create_macos_icon_from_source(source_file):
    """Create macOS .icns icon from source PNG."""
    try:
        # Check if iconutil is available
        iconutil_path = "/usr/bin/iconutil"
        if not Path(iconutil_path).exists():
            print("❌ iconutil not found. Using fallback method...")
            return create_fallback_macos_icon()
        
        # Create iconset directory
        iconset_dir = Path("assets/Dataminer.iconset")
        iconset_dir.mkdir(exist_ok=True)
        
        # Required sizes for macOS iconset
        sizes = [16, 32, 64, 128, 256, 512, 1024]
        
        print(f"Using source file: {source_file}")
        
        # Generate different sizes
        for size in sizes:
            img = Image.open(source_file)
            img = img.resize((size, size), Image.Resampling.LANCZOS)
            output_file = iconset_dir / f"icon_{size}x{size}.png"
            img.save(output_file, "PNG")
            print(f"✅ Created {output_file}")
        
        # Create @2x versions for Retina displays
        for size in [16, 32, 128, 256]:
            img = Image.open(source_file)
            img = img.resize((size * 2, size * 2), Image.Resampling.LANCZOS)
            output_file = iconset_dir / f"icon_{size}x{size}@2x.png"
            img.save(output_file, "PNG")
            print(f"✅ Created {output_file}")
        
        # Create .icns file
        iconset_path = iconset_dir.with_suffix('.iconset')
        result = subprocess.run([
            iconutil_path, '-c', 'icns', 
            str(iconset_path)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Created macOS icon: assets/Dataminer.icns")
            return True
        else:
            print(f"❌ Failed to create .icns: {result.stderr}")
            return create_fallback_macos_icon()
            
    except Exception as e:
        print(f"❌ Error creating macOS icon: {e}")
        return create_fallback_macos_icon()

def create_fallback_macos_icon():
    """Create a simple macOS icon using PIL."""
    try:
        # Create a simple icon with "D" for Dataminer
        size = 1024
        img = Image.new('RGBA', (size, size), (0, 123, 255, 255))  # Blue background
        
        # Add text
        draw = ImageDraw.Draw(img)
        
        # Try to use a nice font, fallback to default
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", int(size * 0.6))
        except:
            font = ImageFont.load_default()
        
        text = "D"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Center the text
        x = (size - text_width) // 2
        y = (size - text_height) // 2
        
        draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
        
        # Create iconset
        iconset_dir = Path("assets/Dataminer.iconset")
        iconset_dir.mkdir(exist_ok=True)
        
        # Save different sizes
        sizes = [16, 32, 64, 128, 256, 512, 1024]
        for size in sizes:
            resized_img = img.resize((size, size), Image.Resampling.LANCZOS)
            output_file = iconset_dir / f"icon_{size}x{size}.png"
            resized_img.save(output_file, "PNG")
        
        # Create .icns using iconutil
        iconset_path = iconset_dir.with_suffix('.iconset')
        result = subprocess.run([
            '/usr/bin/iconutil', '-c', 'icns', 
            str(iconset_path)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Created fallback macOS icon: assets/Dataminer.icns")
            return True
        else:
            print(f"❌ Failed to create fallback .icns: {result.stderr}")
            return False
        
    except Exception as e:
        print(f"❌ Error creating fallback macOS icon: {e}")
        return False

def create_windows_icon():
    """Create Windows .ico icon from PNG."""
    try:
        from PIL import Image
        
        # Find source PNG files
        source_files = list(Path("assets").glob("*.png"))
        if not source_files:
            print("❌ No PNG files found in assets directory")
            return False
        
        source_file = source_files[0]
        print(f"Using source file: {source_file}")
        
        # Create different sizes for ICO
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        
        images = []
        for size in sizes:
            img = Image.open(source_file)
            img = img.resize(size, Image.Resampling.LANCZOS)
            images.append(img)
        
        # Save as ICO
        ico_file = Path("assets/Dataminer.ico")
        images[0].save(ico_file, format='ICO', sizes=[size[1] for size in sizes])
        print(f"✅ Created Windows icon: {ico_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating Windows icon: {e}")
        return False

def create_linux_icon():
    """Create Linux .png icon (just copy the best PNG)."""
    try:
        # Find source PNG files
        source_files = list(Path("assets").glob("*.png"))
        if not source_files:
            print("❌ No PNG files found in assets directory")
            return False
        
        source_file = source_files[0]
        target_file = Path("assets/Dataminer.png")
        
        # Use the largest PNG found
        largest_file = max(source_files, key=lambda f: f.stat().st_size)
        
        import shutil
        shutil.copy2(largest_file, target_file)
        print(f"✅ Created Linux icon: {target_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating Linux icon: {e}")
        return False

def create_fallback_icon():
    """Create a simple fallback icon if no PNG files exist."""
    try:
        # Create a simple icon with "D" for Dataminer
        size = 512
        img = Image.new('RGBA', (size, size), (0, 123, 255, 255))  # Blue background
        
        # Add text
        draw = ImageDraw.Draw(img)
        
        # Try to use a nice font, fallback to default
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", int(size * 0.6))
        except:
            font = ImageFont.load_default()
        
        text = "D"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Center the text
        x = (size - text_width) // 2
        y = (size - text_height) // 2
        
        draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
        
        # Save as PNG
        icon_file = Path("assets/Dataminer.png")
        img.save(icon_file, "PNG")
        print(f"✅ Created fallback icon: {icon_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating fallback icon: {e}")
        return False

def main():
    """Main icon creation process."""
    print("=== Dataminer Icon Creator ===")
    
    # Ensure assets directory exists
    assets_dir = Path("assets")
    if not assets_dir.exists():
        assets_dir.mkdir()
        print("Created assets directory")
    
    # Check if PIL is available
    try:
        from PIL import Image
    except ImportError:
        print("❌ PIL (Pillow) not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "Pillow"])
        from PIL import Image
    
    success = True
    
    # Check if logo.png exists and use it
    logo_file = assets_dir / "logo.png"
    if logo_file.exists():
        print("\n🎨 Found existing logo.png - using it as icon source")
        source_file = logo_file
    else:
        print("\n⚠️  No logo.png found, creating fallback icon")
        source_files = list(assets_dir.glob("*.png"))
        if source_files:
            source_file = source_files[0]
        else:
            success &= create_fallback_icon()
            if success:
                print("\n✅ Icon creation completed!")
                print("Icons created:")
                print("  - macOS: assets/Dataminer.icns")
                print("  - Windows: assets/Dataminer.ico") 
                print("  - Linux: assets/Dataminer.png")
            return
    
    # Create platform-specific icons from the source
    if sys.platform == "darwin":
        print("\n🍎 Creating macOS icon...")
        success &= create_macos_icon_from_source(source_file)
    elif sys.platform == "win32":
        print("\n🪟 Creating Windows icon...")
        success &= create_windows_icon_from_source(source_file)
    elif sys.platform.startswith("linux"):
        print("\n🐧 Creating Linux icon...")
        success &= create_linux_icon_from_source(source_file)
    
    if success:
        print("\n✅ Icon creation completed!")
        print("Icons created:")
        print("  - macOS: assets/Dataminer.icns")
        print("  - Windows: assets/Dataminer.ico") 
        print("  - Linux: assets/Dataminer.png")
    else:
        print("\n❌ Icon creation failed!")
    
    return success

if __name__ == "__main__":
    main()
