"""
Test Case model for Test Case Management System - MVC Architecture
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class TestCase:
    """Test Case data model"""
    
    tc_id: str
    summary: str
    feature: str
    priority: str
    status: str
    
    screen_id: Optional[str] = None
    test_type: Optional[str] = None
    expected_behavior: Optional[str] = None
    procedure: Optional[str] = None
    preconditions: Optional[str] = None
    
    file_path: Optional[str] = None
    directory_structure: Optional[str] = None
    app_name: Optional[str] = None
    test_category: Optional[str] = None
    
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
    
    def update_status(self, new_status: str) -> bool:
        """Update test case status"""
        if new_status in ['Pending', 'In Progress', 'Completed', 'Failed', 'Blocked']:
            self.status = new_status
            self.updated_at = datetime.now()
            return True
        return False
    
    def update_priority(self, new_priority: str) -> bool:
        """Update test case priority"""
        if new_priority in ['Low', 'Medium', 'High', 'Critical']:
            self.priority = new_priority
            self.updated_at = datetime.now()
            return True
        return False
    
    def is_executable(self) -> bool:
        """Check if test case is ready for execution"""
        return (self.status in ['Pending', 'In Progress'] and 
                self.summary and 
                self.expected_behavior)
    
    def get_execution_requirements(self) -> List[str]:
        """Get list of requirements for test execution"""
        requirements = []
        if not self.summary:
            requirements.append("Summary is required")
        if not self.expected_behavior:
            requirements.append("Expected behavior is required")
        if not self.procedure:
            requirements.append("Test procedure is recommended")
        return requirements

class TestCaseRepository(ABC):
    """Abstract repository for test case data access"""
    
    @abstractmethod
    def find_by_id(self, tc_id: str) -> Optional[TestCase]:
        """Find test case by ID"""
        pass
    
    @abstractmethod
    def find_by_status(self, status: str) -> List[TestCase]:
        """Find test cases by status"""
        pass
    
    @abstractmethod
    def find_by_priority(self, priority: str) -> List[TestCase]:
        """Find test cases by priority"""
        pass
    
    @abstractmethod
    def save(self, test_case: TestCase) -> bool:
        """Save test case"""
        pass
    
    @abstractmethod
    def delete(self, tc_id: str) -> bool:
        """Delete test case"""
        pass
    
    @abstractmethod
    def get_all(self) -> List[TestCase]:
        """Get all test cases"""
        pass

class TestCaseFactory:
    """Factory for creating test case objects"""
    
    @staticmethod
    def create_from_dict(data: Dict[str, Any]) -> TestCase:
        """Create test case from dictionary data"""
        return TestCase.from_dict(data)
    
    @staticmethod
    def create_sample() -> TestCase:
        """Create a sample test case"""
        return TestCase(
            tc_id="TC-SAMPLE-001",
            summary="Sample Test Case",
            feature="Sample Feature",
            priority="Medium",
            status="Pending",
            test_type="Functional",
            expected_behavior="This is a sample test case for demonstration purposes.",
            app_name="Sample App",
            created_at=datetime.now()
        )
    
    @staticmethod
    def create_from_excel_row(row_data: Dict[str, Any], file_path: str) -> TestCase:
        """Create test case from Excel row data"""
        return TestCase(
            tc_id=row_data.get('Test Case ID', ''),
            summary=row_data.get('Summary', ''),
            feature=row_data.get('Feature', ''),
            priority=row_data.get('Priority', 'Medium'),
            status=row_data.get('Status', 'Pending'),
            test_type=row_data.get('Test Type', ''),
            expected_behavior=row_data.get('Expected Behavior', ''),
            procedure=row_data.get('Procedure', ''),
            preconditions=row_data.get('Preconditions', ''),
            app_name=row_data.get('App', ''),
            test_category=row_data.get('Test Category', ''),
            file_path=file_path,
            created_at=datetime.now()
        )

