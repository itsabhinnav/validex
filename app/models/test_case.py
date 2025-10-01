"""
Test Case model for Test Case Management System
"""

from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class TestCase:
    """Test Case data model"""
    
    # Primary fields
    tc_id: str
    summary: str
    feature: str
    priority: str
    status: str
    
    # Optional fields
    screen_id: Optional[str] = None
    test_type: Optional[str] = None
    expected_behavior: Optional[str] = None
    procedure: Optional[str] = None
    preconditions: Optional[str] = None
    
    # File information
    file_path: Optional[str] = None
    directory_structure: Optional[str] = None
    app_name: Optional[str] = None
    test_category: Optional[str] = None
    
    # Metadata
    file_id: Optional[str] = None
    local_version: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'tc_id': self.tc_id,
            'summary': self.summary,
            'feature': self.feature,
            'priority': self.priority,
            'status': self.status,
            'screen_id': self.screen_id,
            'test_type': self.test_type,
            'expected_behavior': self.expected_behavior,
            'procedure': self.procedure,
            'preconditions': self.preconditions,
            'file_path': self.file_path,
            'directory_structure': self.directory_structure,
            'app_name': self.app_name,
            'test_category': self.test_category,
            'file_id': self.file_id,
            'local_version': self.local_version,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestCase':
        """Create from dictionary"""
        return cls(
            tc_id=data.get('tc_id', ''),
            summary=data.get('summary', ''),
            feature=data.get('feature', ''),
            priority=data.get('priority', ''),
            status=data.get('status', ''),
            screen_id=data.get('screen_id'),
            test_type=data.get('test_type'),
            expected_behavior=data.get('expected_behavior'),
            procedure=data.get('procedure'),
            preconditions=data.get('preconditions'),
            file_path=data.get('file_path'),
            directory_structure=data.get('directory_structure'),
            app_name=data.get('app_name'),
            test_category=data.get('test_category'),
            file_id=data.get('file_id'),
            local_version=data.get('local_version'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None
        )
    
    def validate(self) -> bool:
        """Validate test case data"""
        required_fields = ['tc_id', 'summary', 'feature', 'priority', 'status']
        return all(getattr(self, field) for field in required_fields)
    
    def get_display_name(self) -> str:
        """Get display name for the test case"""
        return f"{self.tc_id}: {self.summary[:50]}{'...' if len(self.summary) > 50 else ''}"
    
    def get_hierarchy_path(self) -> str:
        """Get hierarchical path for the test case"""
        if self.directory_structure:
            return f"{self.directory_structure}/{self.tc_id}"
        return self.tc_id

