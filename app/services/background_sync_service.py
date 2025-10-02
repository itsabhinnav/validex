"""
Enhanced Background Sync Service for Test Case Management System
"""

import threading
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from app.services.database_service import DatabaseService
from app.services.file_service import FileService
from app.services.sync_service import SyncService
from app.models.sync_status import SyncStatus, SyncStatusType, SyncStrategy

class BackgroundSyncService:
    """Enhanced background sync service with change detection"""
    
    def __init__(self, db_service: DatabaseService, file_service: FileService, sync_service: SyncService):
        self.db_service = db_service
        self.file_service = file_service
        self.sync_service = sync_service
        self.sync_thread = None
        self.running = False
        self.sync_interval = 300  # 5 minutes default
        self.last_sync_time = None
        self.sync_status = None
        self.logger = logging.getLogger(__name__)
        
        # Change detection settings
        self.enable_change_detection = True
        self.file_hash_cache = {}
        self.remote_file_metadata = {}
        
    def configure_sync(self, sync_interval: int = 300, enable_change_detection: bool = True):
        """Configure background sync settings"""
        self.sync_interval = sync_interval
        self.enable_change_detection = enable_change_detection
        self.logger.info(f"Background sync configured: interval={sync_interval}s, change_detection={enable_change_detection}")
    
    def start_background_sync(self):
        """Start background sync thread"""
        if self.running:
            self.logger.warning("Background sync is already running")
            return
        
        self.running = True
        self.sync_thread = threading.Thread(target=self._background_sync_loop, daemon=True)
        self.sync_thread.start()
        self.logger.info("🔄 Background sync started")
        
        # Create initial sync status
        self.sync_status = SyncStatus(
            sync_id=f"bg_sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            strategy=SyncStrategy.INCREMENTAL,
            status=SyncStatusType.RUNNING
        )
    
    def stop_background_sync(self):
        """Stop background sync thread"""
        if not self.running:
            return
            
        self.running = False
        if self.sync_thread:
            self.sync_thread.join(timeout=10)
        
        if self.sync_status:
            self.sync_status.complete_sync(success=True)
        
        self.logger.info("⏹️ Background sync stopped")
    
    def _background_sync_loop(self):
        """Main background sync loop"""
        self.logger.info("🔄 Background sync loop started")
        
        while self.running:
            try:
                # Perform sync cycle
                self._perform_sync_cycle()
                
            except Exception as e:
                self.logger.error(f"❌ Background sync error: {e}")
                # Continue running even if one cycle fails
                
            # Wait for next sync interval
            time.sleep(self.sync_interval)
        
        self.logger.info("🔄 Background sync loop ended")
    
    def _perform_sync_cycle(self):
        """Perform a single sync cycle"""
        cycle_start = datetime.now()
        self.logger.info(f"🔄 Starting sync cycle at {cycle_start}")
        
        try:
            # Step 1: Check for file changes
            if self.enable_change_detection:
                changes_detected = self._detect_file_changes()
                if not changes_detected:
                    self.logger.info("📊 No changes detected, skipping sync")
                    return
            
            # Step 2: Perform incremental sync
            sync_result = self.sync_service.incremental_sync()
            
            # Step 3: Update sync status
            if self.sync_status:
                self.sync_status.update_progress(
                    processed_files=sync_result.get('changes_processed', 0),
                    processed_test_cases=sync_result.get('test_cases_updated', 0)
                )
            
            # Step 4: Update last sync time
            self.last_sync_time = datetime.now()
            
            # Step 5: Log results
            changes_processed = sync_result.get('changes_processed', 0)
            test_cases_updated = sync_result.get('test_cases_updated', 0)
            
            if changes_processed > 0:
                self.logger.info(f"✅ Sync cycle completed: {changes_processed} changes, {test_cases_updated} test cases updated")
            else:
                self.logger.info("✅ Sync cycle completed: No changes found")
                
        except Exception as e:
            self.logger.error(f"❌ Sync cycle failed: {e}")
            if self.sync_status:
                self.sync_status.complete_sync(success=False, error_message=str(e))
    
    def _detect_file_changes(self) -> bool:
        """Detect if any files have changed since last sync"""
        try:
            # Get current file hashes
            current_hashes = {}
            files = self.file_service.scan_directory(self.file_service.upload_folder)
            
            for file_path in files:
                file_hash = self.file_service.get_file_hash(file_path)
                if file_hash:
                    current_hashes[file_path] = file_hash
            
            # Compare with cached hashes
            changes_detected = False
            for file_path, current_hash in current_hashes.items():
                cached_hash = self.file_hash_cache.get(file_path)
                if cached_hash != current_hash:
                    self.logger.info(f"📝 File changed detected: {file_path}")
                    changes_detected = True
                
                # Update cache
                self.file_hash_cache[file_path] = current_hash
            
            # Check for new files
            new_files = set(current_hashes.keys()) - set(self.file_hash_cache.keys())
            if new_files:
                self.logger.info(f"📁 New files detected: {len(new_files)} files")
                changes_detected = True
            
            # Check for deleted files
            deleted_files = set(self.file_hash_cache.keys()) - set(current_hashes.keys())
            if deleted_files:
                self.logger.info(f"🗑️ Deleted files detected: {len(deleted_files)} files")
                changes_detected = True
                # Remove from cache
                for file_path in deleted_files:
                    self.file_hash_cache.pop(file_path, None)
            
            return changes_detected
            
        except Exception as e:
            self.logger.error(f"❌ Error detecting file changes: {e}")
            return True  # Assume changes if detection fails
    
    def force_sync(self) -> Dict[str, Any]:
        """Force immediate sync"""
        self.logger.info("🔄 Forcing immediate sync")
        
        try:
            # Perform full sync
            result = self.sync_service.start_sync(
                SyncStatus(
                    sync_id=f"force_sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    strategy=SyncStrategy.COMPLETE,
                    status=SyncStatusType.RUNNING
                )
            )
            
            # Update cache
            self._update_file_hash_cache()
            
            self.logger.info(f"✅ Force sync completed: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Force sync failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _update_file_hash_cache(self):
        """Update file hash cache"""
        try:
            files = self.file_service.scan_directory(self.file_service.upload_folder)
            for file_path in files:
                file_hash = self.file_service.get_file_hash(file_path)
                if file_hash:
                    self.file_hash_cache[file_path] = file_hash
        except Exception as e:
            self.logger.error(f"❌ Error updating file hash cache: {e}")
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get current sync status"""
        status = {
            'running': self.running,
            'last_sync_time': self.last_sync_time.isoformat() if self.last_sync_time else None,
            'sync_interval': self.sync_interval,
            'change_detection_enabled': self.enable_change_detection,
            'cached_files': len(self.file_hash_cache),
            'current_sync': self.sync_status.to_dict() if self.sync_status else None
        }
        return status
    
    def get_sync_statistics(self) -> Dict[str, Any]:
        """Get sync statistics"""
        try:
            # Get database statistics
            db_stats = self.db_service.get_statistics()
            
            # Get file statistics
            files = self.file_service.scan_directory(self.file_service.upload_folder)
            file_count = len(files)
            
            # Calculate sync efficiency
            total_files = len(self.file_hash_cache)
            changed_files = 0
            for file_path, current_hash in self.file_hash_cache.items():
                if self.file_service.is_file_changed(file_path, current_hash):
                    changed_files += 1
            
            efficiency = (1 - (changed_files / total_files)) * 100 if total_files > 0 else 100
            
            stats = {
                'total_test_cases': db_stats.get('total_cases', 0),
                'total_files': file_count,
                'cached_files': total_files,
                'changed_files': changed_files,
                'sync_efficiency': round(efficiency, 2),
                'last_sync': self.last_sync_time.isoformat() if self.last_sync_time else None,
                'next_sync': (self.last_sync_time + timedelta(seconds=self.sync_interval)).isoformat() if self.last_sync_time else None
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"❌ Error getting sync statistics: {e}")
            return {'error': str(e)}

# Global background sync service instance
background_sync_service = None

def initialize_background_sync(db_service: DatabaseService, file_service: FileService, sync_service: SyncService):
    """Initialize global background sync service"""
    global background_sync_service
    background_sync_service = BackgroundSyncService(db_service, file_service, sync_service)
    return background_sync_service

def get_background_sync_service():
    """Get global background sync service instance"""
    return background_sync_service

