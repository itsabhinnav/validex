"""
Sync Status model for Test Case Management System
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum

class SyncStatusType(Enum):
    """Sync status types"""
    PENDING = 'pending'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'

class SyncStrategy(Enum):
    """Sync strategies"""
    MINIMAL = 'minimal'
    SELECTIVE = 'selective'
    PROGRESSIVE = 'progressive'
    COMPLETE = 'complete'

@dataclass
class SyncStatus:
    """Sync status for tracking sync operations"""
    
    # Primary fields
    sync_id: str
    strategy: SyncStrategy
    status: SyncStatusType
    
    # Progress information
    total_files: int = 0
    processed_files: int = 0
    failed_files: int = 0
    total_test_cases: int = 0
    processed_test_cases: int = 0
    
    # Timing information
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration: Optional[float] = None
    
    # Configuration
    apps: Optional[List[str]] = None
    test_types: Optional[List[str]] = None
    priority_files: Optional[List[str]] = None
    
    # Results
    success: bool = False
    error_message: Optional[str] = None
    warnings: Optional[List[str]] = None
    
    # Metadata
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'sync_id': self.sync_id,
            'strategy': self.strategy.value,
            'status': self.status.value,
            'total_files': self.total_files,
            'processed_files': self.processed_files,
            'failed_files': self.failed_files,
            'total_test_cases': self.total_test_cases,
            'processed_test_cases': self.processed_test_cases,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration': self.duration,
            'apps': self.apps,
            'test_types': self.test_types,
            'priority_files': self.priority_files,
            'success': self.success,
            'error_message': self.error_message,
            'warnings': self.warnings,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SyncStatus':
        """Create from dictionary"""
        return cls(
            sync_id=data.get('sync_id', ''),
            strategy=SyncStrategy(data.get('strategy', 'minimal')),
            status=SyncStatusType(data.get('status', 'pending')),
            total_files=data.get('total_files', 0),
            processed_files=data.get('processed_files', 0),
            failed_files=data.get('failed_files', 0),
            total_test_cases=data.get('total_test_cases', 0),
            processed_test_cases=data.get('processed_test_cases', 0),
            started_at=datetime.fromisoformat(data['started_at']) if data.get('started_at') else None,
            completed_at=datetime.fromisoformat(data['completed_at']) if data.get('completed_at') else None,
            duration=data.get('duration'),
            apps=data.get('apps'),
            test_types=data.get('test_types'),
            priority_files=data.get('priority_files'),
            success=data.get('success', False),
            error_message=data.get('error_message'),
            warnings=data.get('warnings'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None
        )
    
    def start_sync(self):
        """Start sync operation"""
        self.status = SyncStatusType.IN_PROGRESS
        self.started_at = datetime.now()
        self.updated_at = datetime.now()
    
    def complete_sync(self, success: bool = True, error_message: Optional[str] = None):
        """Complete sync operation"""
        self.status = SyncStatusType.COMPLETED if success else SyncStatusType.FAILED
        self.completed_at = datetime.now()
        self.success = success
        self.error_message = error_message
        
        if self.started_at:
            self.duration = (self.completed_at - self.started_at).total_seconds()
        
        self.updated_at = datetime.now()
    
    def cancel_sync(self):
        """Cancel sync operation"""
        self.status = SyncStatusType.CANCELLED
        self.completed_at = datetime.now()
        self.updated_at = datetime.now()
    
    def update_progress(self, processed_files: int, processed_test_cases: int):
        """Update sync progress"""
        self.processed_files = processed_files
        self.processed_test_cases = processed_test_cases
        self.updated_at = datetime.now()
    
    def get_progress_percentage(self) -> float:
        """Get progress percentage"""
        if self.total_files == 0:
            return 0.0
        return (self.processed_files / self.total_files) * 100
    
    def get_processing_rate(self) -> Optional[float]:
        """Get processing rate (files per second)"""
        if not self.started_at or not self.duration:
            return None
        return self.processed_files / self.duration
    
    def is_completed(self) -> bool:
        """Check if sync is completed"""
        return self.status in [SyncStatusType.COMPLETED, SyncStatusType.FAILED, SyncStatusType.CANCELLED]
    
    def is_successful(self) -> bool:
        """Check if sync was successful"""
        return self.status == SyncStatusType.COMPLETED and self.success
    
    def get_summary(self) -> str:
        """Get sync summary"""
        if self.is_completed():
            if self.is_successful():
                return f"✅ Sync completed: {self.processed_files}/{self.total_files} files, {self.processed_test_cases} test cases"
            else:
                return f"❌ Sync failed: {self.error_message}"
        else:
            progress = self.get_progress_percentage()
            return f"🔄 Sync in progress: {progress:.1f}% ({self.processed_files}/{self.total_files} files)"

