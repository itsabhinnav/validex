"""
Requirement Model for Sakura Requirements Management System
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

class RequirementStatus(Enum):
    DRAFT = "Draft"
    REVIEW = "Review"
    APPROVED = "Approved"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    REJECTED = "Rejected"
    ON_HOLD = "On Hold"

class RequirementPriority(Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class RequirementCategory(Enum):
    AUTHENTICATION = "Authentication"
    AUTHORIZATION = "Authorization"
    DATA_MANAGEMENT = "Data Management"
    UI_UX = "UI/UX"
    PERFORMANCE = "Performance"
    SECURITY = "Security"
    INTEGRATION = "Integration"
    REPORTING = "Reporting"
    ANALYTICS = "Analytics"
    API = "API"
    DATABASE = "Database"
    INFRASTRUCTURE = "Infrastructure"
    DOCUMENTATION = "Documentation"
    FUNCTIONAL = "Functional"
    NON_FUNCTIONAL = "Non-Functional"
    BUSINESS = "Business"
    TECHNICAL = "Technical"

@dataclass
class Requirement:
    """Requirement data model"""
    
    # Core fields
    requirement_id: str
    description: str
    given: Optional[str] = None
    when: Optional[str] = None
    then: Optional[str] = None
    
    # Metadata
    status: str = "Draft"
    priority: str = "Medium"
    category: str = "Functional"
    assignee: Optional[str] = None
    created_date: Optional[str] = None
    due_date: Optional[str] = None
    updated_date: Optional[str] = None
    
    # Additional fields
    screen_id: Optional[str] = None
    tags: Optional[str] = None
    source_file: Optional[str] = None
    version: str = "1.0"
    author: Optional[str] = None
    reviewer: Optional[str] = None
    approval_date: Optional[str] = None
    
    # Relationships
    parent_requirement_id: Optional[str] = None
    related_requirements: List[str] = None
    test_cases: List[str] = None
    user_stories: List[str] = None
    
    # Custom fields
    custom_fields: Dict[str, Any] = None
    
    def __post_init__(self):
        """Initialize default values after dataclass creation"""
        if self.created_date is None:
            self.created_date = datetime.now().isoformat()
        
        if self.updated_date is None:
            self.updated_date = datetime.now().isoformat()
        
        if self.related_requirements is None:
            self.related_requirements = []
        
        if self.test_cases is None:
            self.test_cases = []
        
        if self.user_stories is None:
            self.user_stories = []
        
        if self.custom_fields is None:
            self.custom_fields = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert requirement to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Requirement':
        """Create requirement from dictionary"""
        return cls(**data)
    
    def update(self, updates: Dict[str, Any]) -> None:
        """Update requirement with new data"""
        for key, value in updates.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        self.updated_date = datetime.now().isoformat()
    
    def is_overdue(self) -> bool:
        """Check if requirement is overdue"""
        if not self.due_date:
            return False
        
        try:
            due_date = datetime.fromisoformat(self.due_date.replace('Z', '+00:00'))
            return due_date.date() < datetime.now().date()
        except:
            return False
    
    def is_due_soon(self, days: int = 7) -> bool:
        """Check if requirement is due soon"""
        if not self.due_date:
            return False
        
        try:
            due_date = datetime.fromisoformat(self.due_date.replace('Z', '+00:00'))
            days_until_due = (due_date.date() - datetime.now().date()).days
            return 0 <= days_until_due <= days
        except:
            return False
    
    def get_gherkin_scenario(self) -> str:
        """Generate Gherkin scenario from Given/When/Then"""
        scenario = []
        
        if self.given:
            scenario.append(f"Given {self.given}")
        
        if self.when:
            scenario.append(f"When {self.when}")
        
        if self.then:
            scenario.append(f"Then {self.then}")
        
        return "\n".join(scenario)
    
    def validate(self) -> Dict[str, List[str]]:
        """Validate requirement data"""
        errors = []
        
        # Required fields
        if not self.requirement_id:
            errors.append("Requirement ID is required")
        
        if not self.description:
            errors.append("Description is required")
        
        # Validate status
        valid_statuses = [status.value for status in RequirementStatus]
        if self.status not in valid_statuses:
            errors.append(f"Status must be one of: {', '.join(valid_statuses)}")
        
        # Validate priority
        valid_priorities = [priority.value for priority in RequirementPriority]
        if self.priority not in valid_priorities:
            errors.append(f"Priority must be one of: {', '.join(valid_priorities)}")
        
        # Validate category
        valid_categories = [category.value for category in RequirementCategory]
        if self.category not in valid_categories:
            errors.append(f"Category must be one of: {', '.join(valid_categories)}")
        
        # Validate dates
        if self.due_date:
            try:
                datetime.fromisoformat(self.due_date.replace('Z', '+00:00'))
            except:
                errors.append("Invalid due date format")
        
        return {'valid': len(errors) == 0, 'errors': errors}
    
    def get_summary(self) -> str:
        """Get a summary of the requirement"""
        return f"{self.requirement_id}: {self.description[:100]}{'...' if len(self.description) > 100 else ''}"
    
    def get_tags_list(self) -> List[str]:
        """Get tags as a list"""
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the requirement"""
        current_tags = self.get_tags_list()
        if tag not in current_tags:
            current_tags.append(tag)
            self.tags = ', '.join(current_tags)
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the requirement"""
        current_tags = self.get_tags_list()
        if tag in current_tags:
            current_tags.remove(tag)
            self.tags = ', '.join(current_tags)
    
    def add_related_requirement(self, requirement_id: str) -> None:
        """Add a related requirement"""
        if requirement_id not in self.related_requirements:
            self.related_requirements.append(requirement_id)
    
    def remove_related_requirement(self, requirement_id: str) -> None:
        """Remove a related requirement"""
        if requirement_id in self.related_requirements:
            self.related_requirements.remove(requirement_id)
    
    def add_test_case(self, test_case_id: str) -> None:
        """Add a test case"""
        if test_case_id not in self.test_cases:
            self.test_cases.append(test_case_id)
    
    def remove_test_case(self, test_case_id: str) -> None:
        """Remove a test case"""
        if test_case_id in self.test_cases:
            self.test_cases.remove(test_case_id)
    
    def get_progress_percentage(self) -> int:
        """Get progress percentage based on status"""
        status_progress = {
            "Draft": 10,
            "Review": 25,
            "Approved": 40,
            "In Progress": 60,
            "Completed": 100,
            "Rejected": 0,
            "On Hold": 30
        }
        return status_progress.get(self.status, 0)
    
    def get_priority_weight(self) -> int:
        """Get priority weight for sorting"""
        priority_weights = {
            "Critical": 4,
            "High": 3,
            "Medium": 2,
            "Low": 1
        }
        return priority_weights.get(self.priority, 2)
    
    def get_status_color(self) -> str:
        """Get Bootstrap color class for status"""
        status_colors = {
            "Draft": "secondary",
            "Review": "warning",
            "Approved": "info",
            "In Progress": "primary",
            "Completed": "success",
            "Rejected": "danger",
            "On Hold": "dark"
        }
        return status_colors.get(self.status, "secondary")
    
    def get_priority_color(self) -> str:
        """Get Bootstrap color class for priority"""
        priority_colors = {
            "Critical": "danger",
            "High": "warning",
            "Medium": "info",
            "Low": "success"
        }
        return priority_colors.get(self.priority, "info")
