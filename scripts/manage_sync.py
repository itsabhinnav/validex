#!/usr/bin/env python3
"""
Sync Management Script for Validex
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.background_sync_service import get_background_sync_service

def main():
    """Main sync management function"""
    if len(sys.argv) < 2:
        print("Usage: python manage_sync.py <command>")
        print("Commands:")
        print("  start    - Start background sync")
        print("  stop     - Stop background sync")
        print("  status   - Show sync status")
        print("  force    - Force immediate sync")
        print("  stats    - Show sync statistics")
        return
    
    command = sys.argv[1].lower()
    
    try:
        background_sync = get_background_sync_service()
        if not background_sync:
            print("❌ Background sync service not available")
            return
        
        if command == 'start':
            background_sync.start_background_sync()
            print("✅ Background sync started")
            
        elif command == 'stop':
            background_sync.stop_background_sync()
            print("⏹️ Background sync stopped")
            
        elif command == 'status':
            status = background_sync.get_sync_status()
            print("📊 Sync Status:")
            for key, value in status.items():
                print(f"  {key}: {value}")
                
        elif command == 'force':
            result = background_sync.force_sync()
            if result.get('success'):
                print("✅ Force sync completed")
            else:
                print(f"❌ Force sync failed: {result.get('error', 'Unknown error')}")
                
        elif command == 'stats':
            stats = background_sync.get_sync_statistics()
            print("📈 Sync Statistics:")
            for key, value in stats.items():
                print(f"  {key}: {value}")
                
        else:
            print(f"❌ Unknown command: {command}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
