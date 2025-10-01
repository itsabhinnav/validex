"""
File Metadata model for Test Case Management System
"""

from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class FileMetadata:
    """File metadata for tracking and sync operations"""
    
    # Primary fields
    file_id: str
    file_path: str
    file_hash: str
    file_size: int
    
    # Sync information
    last_modified: datetime
    last_synced: Optional[datetime] = None
    sync_status: str = 'pending'
    
    # Remote information
    remote_url: Optional[str] = None
    remote_hash: Optional[str] = None
    remote_version: Optional[str] = None
    
    # Local information
    local_path: Optional[str] = None
    local_hash: Optional[str] = None
    local_version: Optional[str] = None
    
    # Processing information
    record_count: Optional[int] = None
    processing_time: Optional[float] = None
    error_message: Optional[str] = None
    
    # Metadata
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'file_id': self.file_id,
            'file_path': self.file_path,
            'file_hash': self.file_hash,
            'file_size': self.file_size,
            'last_modified': self.last_modified.isoformat(),
            'last_synced': self.last_synced.isoformat() if self.last_synced else None,
            'sync_status': self.sync_status,
            'remote_url': self.remote_url,
            'remote_hash': self.remote_hash,
            'remote_version': self.remote_version,
            'local_path': self.local_path,
            'local_hash': self.local_hash,
            'local_version': self.local_version,
            'record_count': self.record_count,
            'processing_time': self.processing_time,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FileMetadata':
        """Create from dictionary"""
        return cls(
            file_id=data.get('file_id', ''),
            file_path=data.get('file_path', ''),
            file_hash=data.get('file_hash', ''),
            file_size=data.get('file_size', 0),
            last_modified=datetime.fromisoformat(data['last_modified']) if data.get('last_modified') else datetime.now(),
            last_synced=datetime.fromisoformat(data['last_synced']) if data.get('last_synced') else None,
            sync_status=data.get('sync_status', 'pending'),
            remote_url=data.get('remote_url'),
            remote_hash=data.get('remote_hash'),
            remote_version=data.get('remote_version'),
            local_path=data.get('local_path'),
            local_hash=data.get('local_hash'),
            local_version=data.get('local_version'),
            record_count=data.get('record_count'),
            processing_time=data.get('processing_time'),
            error_message=data.get('error_message'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None
        )
    
    def is_changed(self, other_hash: str) -> bool:
        """Check if file has changed"""
        return self.file_hash != other_hash
    
    def needs_sync(self) -> bool:
        """Check if file needs to be synced"""
        return (
            self.sync_status in ['pending', 'failed'] or
            self.remote_hash != self.local_hash or
            not self.last_synced
        )
    
    def mark_synced(self, sync_time: Optional[datetime] = None):
        """Mark file as synced"""
        self.sync_status = 'synced'
        self.last_synced = sync_time or datetime.now()
        self.updated_at = datetime.now()
    
    def mark_failed(self, error_message: str):
        """Mark file sync as failed"""
        self.sync_status = 'failed'
        self.error_message = error_message
        self.updated_at = datetime.now()
    
    def get_sync_age(self) -> Optional[float]:
        """Get age of last sync in seconds"""
        if not self.last_synced:
            return None
        return (datetime.now() - self.last_synced).total_seconds()
    
    def get_file_size_mb(self) -> float:
        """Get file size in MB"""
        return self.file_size / (1024 * 1024)

