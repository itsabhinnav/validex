"""
Sync service for Test Case Management System
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from app.models.sync_status import SyncStatus, SyncStatusType, SyncStrategy
from app.services.database_service import DatabaseService
from app.services.file_service import FileService
from app.services.network_security_service import network_security_service

class SyncService:
    """Service for synchronization operations"""
    
    def __init__(self, db_service: DatabaseService = None, file_service: FileService = None):
        self.db_service = db_service
        self.file_service = file_service
        self.current_sync = None
    
    def configure_remote_sync(self, remote_url: str, api_token: str, strategy: str = 'minimal') -> Dict[str, Any]:
        """Configure remote sync settings"""
        try:
            # Create sync status
            sync_status = SyncStatus(
                sync_id=f"sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                strategy=SyncStrategy(strategy),
                status=SyncStatusType.PENDING
            )
            
            self.current_sync = sync_status
            
            # Start sync process
            return self.start_sync(sync_status)
            
        except Exception as e:
            return {
                'success': False,
                'message': f"Sync configuration failed: {str(e)}"
            }
    
    def start_sync(self, sync_status: SyncStatus) -> Dict[str, Any]:
        """Start sync process"""
        try:
            sync_status.start_sync()
            
            # Get files to sync
            if self.file_service:
                files = self.file_service.scan_directory(self.file_service.upload_folder)
                sync_status.total_files = len(files)
            else:
                files = []
                sync_status.total_files = 0
            
            # Process files
            processed_files = 0
            processed_test_cases = 0
            
            for file_path in files:
                try:
                    # Process file
                    test_cases = self.file_service.process_excel_file(file_path)
                    processed_test_cases += len(test_cases)
                    
                    # Store in database
                    if self.db_service:
                        for test_case in test_cases:
                            self.db_service.insert_test_case(test_case)
                    
                    processed_files += 1
                    sync_status.update_progress(processed_files, processed_test_cases)
                    
                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")
                    sync_status.failed_files += 1
            
            # Complete sync
            sync_status.complete_sync(success=True)
            
            return {
                'success': True,
                'message': f"Sync completed: {processed_files}/{sync_status.total_files} files, {processed_test_cases} test cases",
                'files_synced': processed_files,
                'test_cases_synced': processed_test_cases,
                'failed_files': sync_status.failed_files,
                'duration': sync_status.duration
            }
            
        except Exception as e:
            if sync_status:
                sync_status.complete_sync(success=False, error_message=str(e))
            
            return {
                'success': False,
                'message': f"Sync failed: {str(e)}"
            }
    
    def incremental_sync(self) -> Dict[str, Any]:
        """Perform incremental sync"""
        try:
            # Get files that need syncing
            if not self.file_service:
                return {'changes_processed': 0, 'message': 'File service not available'}
            
            files = self.file_service.scan_directory(self.file_service.upload_folder)
            changes_processed = 0
            
            for file_path in files:
                try:
                    # Check if file needs syncing
                    file_metadata = self.file_service.get_file_metadata(file_path)
                    if not file_metadata:
                        continue
                    
                    # Process file
                    test_cases = self.file_service.process_excel_file(file_path)
                    
                    # Store in database
                    if self.db_service:
                        for test_case in test_cases:
                            self.db_service.insert_test_case(test_case)
                    
                    changes_processed += 1
                    
                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")
            
            return {
                'changes_processed': changes_processed,
                'message': f'Incremental sync completed: {changes_processed} files processed'
            }
            
        except Exception as e:
            return {
                'changes_processed': 0,
                'message': f'Incremental sync failed: {str(e)}'
            }
    
    def get_sync_status(self) -> Optional[SyncStatus]:
        """Get current sync status"""
        return self.current_sync
    
    def cancel_sync(self) -> bool:
        """Cancel current sync"""
        if self.current_sync and not self.current_sync.is_completed():
            self.current_sync.cancel_sync()
            return True
        return False

