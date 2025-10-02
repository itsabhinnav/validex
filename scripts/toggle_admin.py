#!/usr/bin/env python3
"""
Script to toggle admin section on/off
Usage: python scripts/toggle_admin.py [enable|disable]
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import config

def toggle_admin(enable=True):
    """Toggle admin section on or off"""
    try:
        config.set('app.admin_enabled', enable)
        status = "enabled" if enable else "disabled"
        print(f"✅ Admin section has been {status}")
        print(f"📝 Configuration updated in: {config.config_file}")
        
        if enable:
            print("\n🔧 Admin features now available:")
            print("   - Admin dashboard")
            print("   - JFrog configuration")
            print("   - Sync management")
            print("   - Admin role selection")
        else:
            print("\n🚫 Admin features now disabled:")
            print("   - Admin dashboard hidden")
            print("   - Admin role selection hidden")
            print("   - Admin routes protected")
            
    except Exception as e:
        print(f"❌ Error updating configuration: {e}")
        return False
    
    return True

def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/toggle_admin.py [enable|disable]")
        print("\nExamples:")
        print("  python scripts/toggle_admin.py enable   # Enable admin section")
        print("  python scripts/toggle_admin.py disable  # Disable admin section")
        sys.exit(1)
    
    action = sys.argv[1].lower()
    
    if action == 'enable':
        success = toggle_admin(True)
    elif action == 'disable':
        success = toggle_admin(False)
    else:
        print(f"❌ Invalid action: {action}")
        print("Valid actions: enable, disable")
        sys.exit(1)
    
    if success:
        print(f"\n🔄 Restart the application to apply changes")
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()

