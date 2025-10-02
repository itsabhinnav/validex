#!/usr/bin/env python3
"""
Enable Background Sync and Change Detection for Validex
"""

import os
import sys
import json
import logging
from pathlib import Path

def setup_logging():
    """Setup logging for sync operations"""
    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/sync.log'),
            logging.StreamHandler()
        ]
    )
    
    print("✅ Logging configured")

def update_configuration():
    """Update configuration to enable background sync"""
    config_path = Path("config/validex_config.json")
    
    if not config_path.exists():
        print("❌ Configuration file not found. Please run the application first.")
        return False
    
    try:
        # Load existing configuration
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Update sync configuration
        config.setdefault('sync', {})
        config['sync'].update({
            'background_sync_enabled': True,
            'sync_interval_seconds': 300,  # 5 minutes
            'change_detection_enabled': True,
            'file_hash_cache_enabled': True,
            'incremental_sync_enabled': True,
            'force_sync_on_startup': False,
            'sync_strategy': 'incremental',
            'max_retry_attempts': 3,
            'retry_delay_seconds': 60
        })
        
        # Update logging configuration
        config.setdefault('logging', {})
        config['logging'].update({
            'sync_log_level': 'INFO',
            'sync_log_file': 'logs/sync.log',
            'enable_console_logging': True
        })
        
        # Save updated configuration
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print("✅ Configuration updated with background sync settings")
        return True
        
    except Exception as e:
        print(f"❌ Error updating configuration: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    directories = [
        "logs",
        "data/cache",
        "data/excel_files",
        "data/reports"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def test_sync_service():
    """Test if sync service can be imported and initialized"""
    try:
        # Add project root to path
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root))
        
        # Test imports
        from app.services.background_sync_service import BackgroundSyncService
        from app.services.database_service import DatabaseService
        from app.services.file_service import FileService
        from app.services.sync_service import SyncService
        
        print("✅ All sync services imported successfully")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing sync service: {e}")
        return False

def create_sync_management_script():
    """Create a script to manage sync operations"""
    script_content = '''#!/usr/bin/env python3
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
'''
    
    script_path = Path("scripts/manage_sync.py")
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    # Make script executable
    try:
        os.chmod(script_path, 0o755)
    except:
        pass  # Windows doesn't support chmod
    
    print(f"✅ Created sync management script: {script_path}")

def main():
    """Main setup function"""
    print("🚀 Enabling Background Sync and Change Detection for Validex")
    print("=" * 60)
    
    # Step 1: Create directories
    print("\n📁 Creating directories...")
    create_directories()
    
    # Step 2: Setup logging
    print("\n📝 Setting up logging...")
    setup_logging()
    
    # Step 3: Update configuration
    print("\n⚙️ Updating configuration...")
    if not update_configuration():
        print("❌ Failed to update configuration")
        return False
    
    # Step 4: Test sync service
    print("\n🧪 Testing sync service...")
    if not test_sync_service():
        print("❌ Sync service test failed")
        return False
    
    # Step 5: Create management script
    print("\n📜 Creating management script...")
    create_sync_management_script()
    
    print("\n🎉 Background sync and change detection enabled successfully!")
    print("\nNext steps:")
    print("1. Start the application: python run.py")
    print("2. Access sync dashboard: http://localhost:8000/sync-dashboard")
    print("3. Use management script: python scripts/manage_sync.py <command>")
    print("\nAvailable commands:")
    print("  python scripts/manage_sync.py start    - Start background sync")
    print("  python scripts/manage_sync.py stop     - Stop background sync")
    print("  python scripts/manage_sync.py status  - Show sync status")
    print("  python scripts/manage_sync.py force    - Force immediate sync")
    print("  python scripts/manage_sync.py stats    - Show sync statistics")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
