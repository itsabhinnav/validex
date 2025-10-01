import requests
import sqlite3
import hashlib
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import threading
import time

class RemoteAPI:
    """Handles communication with remote JFrog Artifactory"""
    
    def __init__(self, base_url: str, api_token: str):
        self.base_url = base_url.rstrip('/')
        self.api_token = api_token
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        })
    
    def get_files_metadata(self) -> List[Dict]:
        """Get metadata for all files without downloading content"""
        try:
            response = self.session.get(f"{self.base_url}/api/files/metadata")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching metadata: {e}")
            return []
    
    def get_file_content(self, file_id: str) -> bytes:
        """Download specific file content"""
        try:
            response = self.session.get(f"{self.base_url}/api/files/{file_id}/content")
            response.raise_for_status()
            return response.content
        except Exception as e:
            print(f"Error downloading file {file_id}: {e}")
            return b''
    
    def get_changes_since(self, timestamp: str) -> List[Dict]:
        """Get files changed since timestamp"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/files/changes",
                params={'since': timestamp}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching changes: {e}")
            return []
    
    def get_file_delta(self, file_id: str, local_version: str) -> bytes:
        """Get delta changes for a file"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/files/{file_id}/delta",
                params={'version': local_version}
            )
            response.raise_for_status()
            return response.content
        except Exception as e:
            print(f"Error fetching delta for {file_id}: {e}")
            return b''

class SyncStrategy:
    """Defines different sync strategies"""
    
    @staticmethod
    def minimal_sync(metadata: List[Dict]) -> List[Dict]:
        """Sync only metadata, no file content"""
        return [{
            'id': f['id'],
            'path': f['path'],
            'size': f['size'],
            'hash': f['hash'],
            'metadata_only': True
        } for f in metadata]
    
    @staticmethod
    def selective_sync(metadata: List[Dict], apps: List[str] = None, 
                      test_types: List[str] = None) -> List[Dict]:
        """Sync only selected apps or test types"""
        filtered = metadata
        
        if apps:
            filtered = [f for f in filtered if f.get('app') in apps]
        
        if test_types:
            filtered = [f for f in filtered if f.get('test_type') in test_types]
        
        return filtered
    
    @staticmethod
    def progressive_sync(metadata: List[Dict], priority_files: List[str] = None) -> List[Dict]:
        """Sync files in priority order"""
        if priority_files:
            # Sort by priority
            priority_set = set(priority_files)
            return sorted(metadata, key=lambda x: x['id'] in priority_set, reverse=True)
        
        # Default: sort by access frequency or size
        return sorted(metadata, key=lambda x: x.get('access_count', 0), reverse=True)

class HybridStorageManager:
    """Manages hybrid remote-local storage"""
    
    def __init__(self, remote_api: RemoteAPI, local_db_path: str):
        self.remote_api = remote_api
        self.local_db_path = local_db_path
        self.sync_cache = {}
        self.last_sync = None
        self.init_local_database()
    
    def init_local_database(self):
        """Initialize local SQLite database"""
        conn = sqlite3.connect(self.local_db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS local_test_cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tc_id TEXT NOT NULL,
                summary TEXT,
                feature TEXT,
                priority TEXT,
                status TEXT,
                screen_id TEXT,
                test_type TEXT,
                expected_behavior TEXT,
                file_path TEXT,
                directory_structure TEXT,
                app_name TEXT,
                test_category TEXT,
                file_id TEXT,
                local_version TEXT,
                last_synced TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id TEXT UNIQUE,
                remote_hash TEXT,
                local_hash TEXT,
                file_size INTEGER,
                last_modified TIMESTAMP,
                sync_status TEXT,
                last_synced TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_file_id ON local_test_cases(file_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tc_id ON local_test_cases(tc_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_app_name ON local_test_cases(app_name)')
        
        conn.commit()
        conn.close()
    
    def get_sync_strategy(self) -> str:
        """Get current sync strategy"""
        conn = sqlite3.connect(self.local_db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM sync_settings WHERE key = ?', ('sync_strategy',))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 'minimal'
    
    def set_sync_strategy(self, strategy: str):
        """Set sync strategy"""
        conn = sqlite3.connect(self.local_db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO sync_settings (key, value) 
            VALUES (?, ?)
        ''', ('sync_strategy', strategy))
        conn.commit()
        conn.close()
    
    def initial_sync(self, strategy: str = 'minimal', **kwargs) -> Dict:
        """Perform initial sync based on strategy"""
        print(f"🚀 Starting initial sync with strategy: {strategy}")
        
        # Get remote metadata
        metadata = self.remote_api.get_files_metadata()
        print(f"📊 Found {len(metadata)} files on remote server")
        
        # Apply strategy
        if strategy == 'minimal':
            files_to_sync = SyncStrategy.minimal_sync(metadata)
        elif strategy == 'selective':
            files_to_sync = SyncStrategy.selective_sync(
                metadata, 
                apps=kwargs.get('apps'),
                test_types=kwargs.get('test_types')
            )
        elif strategy == 'progressive':
            files_to_sync = SyncStrategy.progressive_sync(
                metadata,
                priority_files=kwargs.get('priority_files')
            )
        else:
            files_to_sync = metadata
        
        print(f"📥 Syncing {len(files_to_sync)} files...")
        
        # Sync files
        synced_count = 0
        total_size = 0
        
        for file_info in files_to_sync:
            try:
                if file_info.get('metadata_only'):
                    # Store metadata only
                    self.store_file_metadata(file_info)
                else:
                    # Download and process file
                    content = self.remote_api.get_file_content(file_info['id'])
                    if content:
                        processed_count = self.process_file_content(file_info, content)
                        synced_count += processed_count
                        total_size += len(content)
                
                print(f"✅ Synced {file_info['path']}")
                
            except Exception as e:
                print(f"❌ Error syncing {file_info['path']}: {e}")
        
        # Update sync timestamp
        self.update_last_sync()
        
        return {
            'strategy': strategy,
            'files_synced': len(files_to_sync),
            'test_cases_synced': synced_count,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'sync_time': datetime.now().isoformat()
        }
    
    def incremental_sync(self) -> Dict:
        """Sync only changed files"""
        print("🔄 Starting incremental sync...")
        
        # Get last sync timestamp
        last_sync = self.get_last_sync_timestamp()
        if not last_sync:
            print("⚠️ No previous sync found, performing initial sync")
            return self.initial_sync('minimal')
        
        # Get changes since last sync
        changes = self.remote_api.get_changes_since(last_sync)
        print(f"📊 Found {len(changes)} changes since last sync")
        
        synced_count = 0
        for change in changes:
            try:
                if change['action'] == 'modified':
                    # Download and process changed file
                    content = self.remote_api.get_file_content(change['file_id'])
                    if content:
                        processed_count = self.process_file_content(change, content)
                        synced_count += processed_count
                        print(f"✅ Updated {change['path']}")
                
                elif change['action'] == 'deleted':
                    # Remove from local database
                    self.remove_local_file(change['file_id'])
                    print(f"🗑️ Removed {change['path']}")
                
            except Exception as e:
                print(f"❌ Error processing change for {change['path']}: {e}")
        
        # Update sync timestamp
        self.update_last_sync()
        
        return {
            'changes_processed': len(changes),
            'test_cases_updated': synced_count,
            'sync_time': datetime.now().isoformat()
        }
    
    def process_file_content(self, file_info: Dict, content: bytes) -> int:
        """Process downloaded file content"""
        import pandas as pd
        from io import BytesIO
        
        try:
            # Read Excel content
            df = pd.read_excel(BytesIO(content))
            
            # Extract hierarchical information
            path_parts = file_info['path'].split('/')
            app_name = path_parts[0] if len(path_parts) > 0 else 'Unknown'
            test_category = path_parts[1] if len(path_parts) > 1 else 'Unknown'
            directory_structure = '/'.join(path_parts[:-1]) if len(path_parts) > 1 else ''
            
            # Store in local database
            conn = sqlite3.connect(self.local_db_path)
            cursor = conn.cursor()
            
            # Remove existing records for this file
            cursor.execute('DELETE FROM local_test_cases WHERE file_id = ?', (file_info['id'],))
            
            # Insert new records
            for _, row in df.iterrows():
                cursor.execute('''
                    INSERT INTO local_test_cases 
                    (tc_id, summary, feature, priority, status, screen_id, test_type,
                     expected_behavior, file_path, directory_structure, app_name, 
                     test_category, file_id, local_version)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row.get('TC ID', ''),
                    row.get('Summary', ''),
                    row.get('Feature', ''),
                    row.get('Priority', ''),
                    row.get('Status', ''),
                    row.get('Screen ID', ''),
                    row.get('type', ''),
                    row.get('Expected Behavior', ''),
                    file_info['path'],
                    directory_structure,
                    app_name,
                    test_category,
                    file_info['id'],
                    file_info.get('version', '1')
                ))
            
            # Update sync metadata
            cursor.execute('''
                INSERT OR REPLACE INTO sync_metadata 
                (file_id, remote_hash, local_hash, file_size, last_modified, sync_status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                file_info['id'],
                file_info.get('hash', ''),
                hashlib.md5(content).hexdigest(),
                len(content),
                file_info.get('last_modified', datetime.now().isoformat()),
                'synced'
            ))
            
            conn.commit()
            conn.close()
            
            return len(df)
            
        except Exception as e:
            print(f"Error processing file content: {e}")
            return 0
    
    def store_file_metadata(self, file_info: Dict):
        """Store file metadata without content"""
        conn = sqlite3.connect(self.local_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO sync_metadata 
            (file_id, remote_hash, file_size, last_modified, sync_status)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            file_info['id'],
            file_info.get('hash', ''),
            file_info.get('size', 0),
            file_info.get('last_modified', datetime.now().isoformat()),
            'metadata_only'
        ))
        
        conn.commit()
        conn.close()
    
    def remove_local_file(self, file_id: str):
        """Remove file from local database"""
        conn = sqlite3.connect(self.local_db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM local_test_cases WHERE file_id = ?', (file_id,))
        cursor.execute('DELETE FROM sync_metadata WHERE file_id = ?', (file_id,))
        
        conn.commit()
        conn.close()
    
    def get_last_sync_timestamp(self) -> Optional[str]:
        """Get last sync timestamp"""
        conn = sqlite3.connect(self.local_db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM sync_settings WHERE key = ?', ('last_sync',))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    
    def update_last_sync(self):
        """Update last sync timestamp"""
        conn = sqlite3.connect(self.local_db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO sync_settings (key, value) 
            VALUES (?, ?)
        ''', ('last_sync', datetime.now().isoformat()))
        conn.commit()
        conn.close()
    
    def search_test_cases(self, filters: Dict = None, limit: int = 50, offset: int = 0) -> Dict:
        """Search test cases with local fallback to remote"""
        conn = sqlite3.connect(self.local_db_path)
        cursor = conn.cursor()
        
        # Build WHERE clause
        where_conditions = []
        params = []
        
        if filters:
            for key, value in filters.items():
                if value and key in ['tc_id', 'feature', 'status', 'priority', 'app_name', 'test_type']:
                    where_conditions.append(f"{key} LIKE ?")
                    params.append(f"%{value}%")
        
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        # Get total count
        cursor.execute(f"SELECT COUNT(*) FROM local_test_cases WHERE {where_clause}", params)
        total_count = cursor.fetchone()[0]
        
        # Get paginated results
        query = f"""
            SELECT tc_id, summary, feature, priority, status, screen_id, test_type,
                   expected_behavior, file_path, directory_structure, app_name, test_category
            FROM local_test_cases 
            WHERE {where_clause}
            ORDER BY tc_id
            LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        conn.close()
        
        return {
            'results': results,
            'total_count': total_count,
            'limit': limit,
            'offset': offset,
            'has_more': (offset + limit) < total_count,
            'source': 'local'
        }
    
    def get_statistics(self) -> Dict:
        """Get statistics from local database"""
        conn = sqlite3.connect(self.local_db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Total count
        cursor.execute("SELECT COUNT(*) FROM local_test_cases")
        stats['total_cases'] = cursor.fetchone()[0]
        
        # By status
        cursor.execute("SELECT status, COUNT(*) FROM local_test_cases GROUP BY status")
        stats['by_status'] = dict(cursor.fetchall())
        
        # By priority
        cursor.execute("SELECT priority, COUNT(*) FROM local_test_cases GROUP BY priority")
        stats['by_priority'] = dict(cursor.fetchall())
        
        # By feature
        cursor.execute("SELECT feature, COUNT(*) FROM local_test_cases GROUP BY feature")
        stats['by_feature'] = dict(cursor.fetchall())
        
        # By app
        cursor.execute("SELECT app_name, COUNT(*) FROM local_test_cases GROUP BY app_name")
        stats['by_app'] = dict(cursor.fetchall())
        
        # By test type
        cursor.execute("SELECT test_type, COUNT(*) FROM local_test_cases GROUP BY test_type")
        stats['by_test_type'] = dict(cursor.fetchall())
        
        # By directory
        cursor.execute("SELECT directory_structure, COUNT(*) FROM local_test_cases GROUP BY directory_structure")
        stats['by_directory'] = dict(cursor.fetchall())
        
        conn.close()
        return stats

class BackgroundSyncManager:
    """Manages background sync operations"""
    
    def __init__(self, storage_manager: HybridStorageManager, sync_interval: int = 300):
        self.storage_manager = storage_manager
        self.sync_interval = sync_interval  # 5 minutes default
        self.sync_thread = None
        self.running = False
    
    def start_background_sync(self):
        """Start background sync thread"""
        if self.running:
            return
        
        self.running = True
        self.sync_thread = threading.Thread(target=self._background_sync_loop)
        self.sync_thread.daemon = True
        self.sync_thread.start()
        print("🔄 Background sync started")
    
    def stop_background_sync(self):
        """Stop background sync thread"""
        self.running = False
        if self.sync_thread:
            self.sync_thread.join()
        print("⏹️ Background sync stopped")
    
    def _background_sync_loop(self):
        """Background sync loop"""
        while self.running:
            try:
                # Perform incremental sync
                result = self.storage_manager.incremental_sync()
                if result['changes_processed'] > 0:
                    print(f"🔄 Background sync: {result['changes_processed']} changes processed")
                
            except Exception as e:
                print(f"❌ Background sync error: {e}")
            
            # Wait for next sync
            time.sleep(self.sync_interval)
    
    def force_sync(self):
        """Force immediate sync"""
        try:
            result = self.storage_manager.incremental_sync()
            print(f"🔄 Forced sync: {result['changes_processed']} changes processed")
            return result
        except Exception as e:
            print(f"❌ Forced sync error: {e}")
            return None

# Global instances
remote_api = None
storage_manager = None
background_sync = None

def initialize_remote_sync(remote_url: str, api_token: str, local_db_path: str = "data/hybrid_test_cases.db"):
    """Initialize remote sync system"""
    global remote_api, storage_manager, background_sync
    
    remote_api = RemoteAPI(remote_url, api_token)
    storage_manager = HybridStorageManager(remote_api, local_db_path)
    background_sync = BackgroundSyncManager(storage_manager)
    
    print("🚀 Remote sync system initialized")
    return storage_manager

def setup_wizard():
    """Interactive setup wizard"""
    print("🚀 Welcome to Test Case Management System")
    print("\nChoose your sync strategy:")
    print("1. 🏃‍♂️ Quick Start (Metadata only) - 5 minutes, 50MB")
    print("2. 🎯 Focused (Select apps/types) - 15-30 minutes, 1GB")
    print("3. 📦 Complete (All files) - 2-4 hours, 5GB")
    
    choice = input("Enter your choice (1-3): ")
    
    if choice == "1":
        return storage_manager.initial_sync('minimal')
    elif choice == "2":
        apps = input("Enter apps to sync (comma-separated, e.g., App1,App2): ").split(',')
        test_types = input("Enter test types (comma-separated, e.g., FMEA,Sanity): ").split(',')
        return storage_manager.initial_sync('selective', apps=apps, test_types=test_types)
    elif choice == "3":
        return storage_manager.initial_sync('complete')
    else:
        print("Invalid choice, using minimal sync")
        return storage_manager.initial_sync('minimal')
