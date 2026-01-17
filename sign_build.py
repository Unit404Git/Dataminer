#!/usr/bin/env python3
"""
Script to create a properly signed macOS application.
This requires an Apple Developer certificate.
"""

import subprocess
import sys
import os
from pathlib import Path

def check_codesign():
    """Check if codesign is available."""
    try:
        result = subprocess.run(["codesign", "--version"], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def get_developer_identity():
    """Get available developer identities for code signing."""
    try:
        result = subprocess.run(["security", "find-identity", "-v", "-p", "codesigning"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            identities = []
            for line in result.stdout.split('\n'):
                if 'Apple Development' in line or 'Apple Distribution' in line:
                    # Extract identity hash
                    parts = line.strip().split('"')
                    if len(parts) >= 2:
                        identities.append(parts[1])
            return identities
    except Exception as e:
        print(f"Error checking identities: {e}")
    return []

def sign_app(app_path, identity):
    """Sign the application with the given identity."""
    try:
        print(f"Signing {app_path} with identity: {identity}")
        
        # Sign the app
        result = subprocess.run([
            "codesign", 
            "--force", 
            "--deep", 
            "--sign", identity,
            str(app_path)
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Signing failed: {result.stderr}")
            return False
        
        # Verify the signature
        verify_result = subprocess.run([
            "codesign", 
            "--verify", 
            "--verbose", 
            str(app_path)
        ], capture_output=True, text=True)
        
        if verify_result.returncode == 0:
            print("✅ App successfully signed and verified")
            return True
        else:
            print(f"Verification failed: {verify_result.stderr}")
            return False
            
    except Exception as e:
        print(f"Error during signing: {e}")
        return False

def create_notarized_dmg(app_path):
    """Create a notarized DMG (requires Apple Developer account)."""
    print("Note: Full notarization requires Apple Developer account and Xcode tools")
    print("This is optional for distribution - basic code signing prevents most security warnings")
    
    # Basic DMG creation (already done in build.py)
    return True

def main():
    """Main signing process."""
    print("=== macOS App Code Signing ===")
    
    # Check if codesign is available
    if not check_codesign():
        print("❌ codesign not found. Install Xcode Command Line Tools:")
        print("   xcode-select --install")
        return False
    
    # Check for existing app
    app_path = Path("dist/Dataminer.app")
    if not app_path.exists():
        print("❌ Dataminer.app not found in dist/. Run build.py first.")
        return False
    
    # Get available identities
    identities = get_developer_identity()
    
    if not identities:
        print("❌ No code signing identities found.")
        print("\nTo fix this:")
        print("1. Enroll in Apple Developer Program ($99/year)")
        print("2. Create a certificate in Xcode or Apple Developer portal")
        print("3. Download and install the certificate")
        print("\nAlternative: Use ad-hoc signing (free, but still shows warnings)")
        
        # Offer ad-hoc signing
        try:
            print("\nTrying ad-hoc signing...")
            if sign_app(app_path, "-"):
                print("✅ Ad-hoc signing completed")
                print("Note: Users will still need to right-click → Open on first run")
                return True
        except Exception as e:
            print(f"Ad-hoc signing failed: {e}")
        
        return False
    
    print(f"Found {len(identities)} signing identity/ies:")
    for i, identity in enumerate(identities, 1):
        print(f"  {i}. {identity}")
    
    # Use the first identity
    selected_identity = identities[0]
    
    # Sign the app
    if sign_app(app_path, selected_identity):
        print("\n✅ App successfully signed!")
        print("The app should now open without security warnings for most users.")
        
        # Recreate DMG with signed app
        print("\nRecreating DMG with signed app...")
        try:
            dmg_result = subprocess.run([
                "python3", "build.py"
            ], capture_output=True, text=True)
            
            if dmg_result.returncode == 0:
                print("✅ DMG recreated with signed app")
            else:
                print(f"DMG recreation failed: {dmg_result.stderr}")
                
        except Exception as e:
            print(f"Error recreating DMG: {e}")
        
        return True
    
    return False

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n⚠️  For immediate distribution without signing:")
        print("1. Users can right-click → Open to bypass the warning")
        print("2. This only needs to be done once per user")
        print("3. Consider adding instructions to your download page")
