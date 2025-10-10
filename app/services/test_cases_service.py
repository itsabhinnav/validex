"""
Test Cases Service for business logic
"""

from typing import Dict, Any, List, Optional, Union
import pandas as pd
from datetime import datetime
import re
from app.models.test_case import TestCase

class TestCasesService:
    """Service for test cases business logic with dynamic filtering"""
    
    def __init__(self):
        pass
    
    def _get_filter_types(self):
        """Get filter types mapping - defined as method to avoid initialization issues"""
        return {
            'exact': self._filter_exact,
            'contains': self._filter_contains,
            'starts_with': self._filter_starts_with,
            'ends_with': self._filter_ends_with,
            'regex': self._filter_regex,
            'in_list': self._filter_in_list,
            'not_in_list': self._filter_not_in_list,
            'greater_than': self._filter_greater_than,
            'less_than': self._filter_less_than,
            'between': self._filter_between,
            'is_empty': self._filter_is_empty,
            'is_not_empty': self._filter_is_not_empty
        }
    
    def filter_test_cases(self, test_cases_data: Dict[str, List[Dict[str, Any]]], 
                         filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter test cases based on dynamic criteria"""
        filtered_cases = []
        
        for file_name, file_data in test_cases_data.items():
            for case in file_data:
                case['source_file'] = file_name
                
                if self._should_include_case_dynamic(case, filters):
                    filtered_cases.append(case)
        
        return filtered_cases
    
    def _should_include_case_dynamic(self, case: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if case should be included based on dynamic filters"""
        
        # Handle legacy filters for backward compatibility
        if filters.get('app_filter') and case.get('App', '') not in filters['app_filter']:
            return False
        
        if filters.get('test_type_filter') and case.get('Test Type', '') not in filters['test_type_filter']:
            return False
        
        if filters.get('priority_filter'):
            case_priority = case.get('Priority', '').lower()
            filter_priorities = [p.lower() for p in filters['priority_filter']]
            if case_priority not in filter_priorities:
                return False
        
        if filters.get('selected_id_list') and filters['selected_id_list'][0]:
            case_id = str(case.get('Test Case ID', case.get('TC ID', '')))
            if case_id not in filters['selected_id_list']:
                return False
        
        # Handle dynamic filters
        dynamic_filters = filters.get('dynamic_filters', {})
        for filter_config in dynamic_filters:
            if not self._apply_dynamic_filter(case, filter_config):
                return False
        
        # Handle global search
        if filters.get('search_query'):
            search_text = ' '.join(str(v) for v in case.values() if v).lower()
            if filters['search_query'].lower() not in search_text:
                return False
        
        return True
    
    def _apply_dynamic_filter(self, case: Dict[str, Any], filter_config: Dict[str, Any]) -> bool:
        """Apply a single dynamic filter to a test case"""
        column = filter_config.get('column')
        filter_type = filter_config.get('type', 'exact')
        value = filter_config.get('value')
        case_value = case.get(column, '')
        
        if column not in case:
            return filter_type == 'is_empty'
        
        filter_types = self._get_filter_types()
        filter_func = filter_types.get(filter_type, self._filter_exact)
        return filter_func(case_value, value)
    
    # Filter type implementations
    def _filter_exact(self, case_value: Any, filter_value: Any) -> bool:
        """Exact match filter"""
        return str(case_value).lower() == str(filter_value).lower()
    
    def _filter_contains(self, case_value: Any, filter_value: Any) -> bool:
        """Contains filter"""
        return str(filter_value).lower() in str(case_value).lower()
    
    def _filter_starts_with(self, case_value: Any, filter_value: Any) -> bool:
        """Starts with filter"""
        return str(case_value).lower().startswith(str(filter_value).lower())
    
    def _filter_ends_with(self, case_value: Any, filter_value: Any) -> bool:
        """Ends with filter"""
        return str(case_value).lower().endswith(str(filter_value).lower())
    
    def _filter_regex(self, case_value: Any, filter_value: Any) -> bool:
        """Regex filter"""
        try:
            return bool(re.search(str(filter_value), str(case_value), re.IGNORECASE))
        except re.error:
            return False
    
    def _filter_in_list(self, case_value: Any, filter_value: Union[List, str]) -> bool:
        """In list filter"""
        if isinstance(filter_value, str):
            filter_value = [v.strip() for v in filter_value.split(',')]
        return str(case_value).lower() in [str(v).lower() for v in filter_value]
    
    def _filter_not_in_list(self, case_value: Any, filter_value: Union[List, str]) -> bool:
        """Not in list filter"""
        if isinstance(filter_value, str):
            filter_value = [v.strip() for v in filter_value.split(',')]
        return str(case_value).lower() not in [str(v).lower() for v in filter_value]
    
    def _filter_greater_than(self, case_value: Any, filter_value: Any) -> bool:
        """Greater than filter"""
        try:
            return float(case_value) > float(filter_value)
        except (ValueError, TypeError):
            return str(case_value).lower() > str(filter_value).lower()
    
    def _filter_less_than(self, case_value: Any, filter_value: Any) -> bool:
        """Less than filter"""
        try:
            return float(case_value) < float(filter_value)
        except (ValueError, TypeError):
            return str(case_value).lower() < str(filter_value).lower()
    
    def _filter_between(self, case_value: Any, filter_value: Union[List, str]) -> bool:
        """Between filter (inclusive)"""
        if isinstance(filter_value, str):
            filter_value = [v.strip() for v in filter_value.split(',')]
        if len(filter_value) != 2:
            return False
        try:
            val = float(case_value)
            return float(filter_value[0]) <= val <= float(filter_value[1])
        except (ValueError, TypeError):
            return str(filter_value[0]).lower() <= str(case_value).lower() <= str(filter_value[1]).lower()
    
    def _filter_is_empty(self, case_value: Any, filter_value: Any) -> bool:
        """Is empty filter"""
        return not case_value or str(case_value).strip() == ''
    
    def _filter_is_not_empty(self, case_value: Any, filter_value: Any) -> bool:
        """Is not empty filter"""
        return bool(case_value) and str(case_value).strip() != ''
    
    def sort_test_cases(self, test_cases: List[Dict[str, Any]], 
                       sort_by: str, sort_order: str) -> List[Dict[str, Any]]:
        """Sort test cases"""
        if sort_by in ['Test Case ID', 'Summary', 'App', 'Test Type', 'Feature', 'Status', 'Priority']:
            try:
                reverse = sort_order.lower() == 'desc'
                test_cases.sort(key=lambda x: str(x.get(sort_by, '')).lower(), reverse=reverse)
            except:
                pass
        return test_cases
    
    def get_filter_options(self, test_cases_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[str]]:
        """Get unique values for filter dropdowns - dynamically generated from all columns"""
        filter_options = {}
        column_values = {}
        
        # Collect all unique values for each column
        for file_data in test_cases_data.values():
            for case in file_data:
                for column, value in case.items():
                    if value and str(value).strip():  # Skip empty values
                        if column not in column_values:
                            column_values[column] = set()
                        column_values[column].add(str(value).strip())
        
        # Convert to sorted lists
        for column, values in column_values.items():
            filter_options[column] = sorted(list(values))
        
        # Add legacy filter options for backward compatibility
        filter_options.update({
            'apps': filter_options.get('App', []),
            'test_types': filter_options.get('Test Type', []),
            'priorities': filter_options.get('Priority', [])
        })
        
        return filter_options
    
    def get_available_columns(self, test_cases_data: Dict[str, List[Dict[str, Any]]]) -> List[str]:
        """Get all available columns from test cases data"""
        columns = set()
        for file_data in test_cases_data.values():
            for case in file_data:
                columns.update(case.keys())
        return sorted(list(columns))
    
    def get_column_statistics(self, test_cases_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Dict[str, Any]]:
        """Get statistics for each column"""
        stats = {}
        total_cases = 0
        
        # Count total cases
        for file_data in test_cases_data.values():
            total_cases += len(file_data)
        
        # Analyze each column
        for file_data in test_cases_data.values():
            for case in file_data:
                for column, value in case.items():
                    if column not in stats:
                        stats[column] = {
                            'total_values': 0,
                            'unique_values': set(),
                            'empty_count': 0,
                            'data_types': set()
                        }
                    
                    stats[column]['total_values'] += 1
                    
                    if value and str(value).strip():
                        stats[column]['unique_values'].add(str(value).strip())
                        stats[column]['data_types'].add(type(value).__name__)
                    else:
                        stats[column]['empty_count'] += 1
        
        # Convert sets to counts and percentages
        for column, stat in stats.items():
            stat['unique_count'] = len(stat['unique_values'])
            stat['completeness'] = round((stat['total_values'] - stat['empty_count']) / stat['total_values'] * 100, 2) if stat['total_values'] > 0 else 0
            stat['data_types'] = list(stat['data_types'])
            del stat['unique_values']  # Remove the set to make it JSON serializable
        
        return stats
    
    def export_to_excel(self, test_cases: List[Dict[str, Any]]) -> bytes:
        """Export test cases to Excel format"""
        if not test_cases:
            return b''
        
        df = pd.DataFrame(test_cases)
        
        column_order = ['Test Case ID', 'Summary', 'App', 'Test Type', 'Feature', 'Priority', 'Status', 'Expected Behavior', 'source_file']
        existing_columns = [col for col in column_order if col in df.columns]
        other_columns = [col for col in df.columns if col not in existing_columns]
        df = df[existing_columns + other_columns]
        
        from io import BytesIO
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Test Cases', index=False)
            
            workbook = writer.book
            worksheet = writer.sheets['Test Cases']
            
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        output.seek(0)
        return output.getvalue()
    
    def export_to_csv(self, test_cases: List[Dict[str, Any]]) -> str:
        """Export test cases to CSV format"""
        if not test_cases:
            return ''
        
        df = pd.DataFrame(test_cases)
        
        column_order = ['Test Case ID', 'Summary', 'App', 'Test Type', 'Feature', 'Priority', 'Status', 'Expected Behavior', 'source_file']
        existing_columns = [col for col in column_order if col in df.columns]
        other_columns = [col for col in df.columns if col not in existing_columns]
        df = df[existing_columns + other_columns]
        
        from io import StringIO
        output = StringIO()
        df.to_csv(output, index=False)
        output.seek(0)
        
        return output.getvalue()
    
    def find_test_case(self, test_cases_data: Dict[str, List[Dict[str, Any]]], 
                      test_id: str, source_file: str) -> Optional[Dict[str, Any]]:
        """Find a specific test case by ID and source file"""
        if not test_id or not source_file:
            return None
        
        for file_name, file_data in test_cases_data.items():
            if file_name == source_file:
                for case in file_data:
                    case_id = case.get('Test Case ID', case.get('TC ID', ''))
                    if str(case_id) == str(test_id):
                        case['source_file'] = file_name
                        return case
        return None
    
    def create_sample_test_case(self) -> Dict[str, Any]:
        """Create a sample test case for demonstration"""
        return {
            'Test Case ID': 'TC-SAMPLE-001',
            'Summary': 'Sample Test Case',
            'App': 'Sample App',
            'Test Type': 'Functional',
            'Feature': 'Sample Feature',
            'Priority': 'Medium',
            'Status': 'Pending',
            'Expected Behavior': 'This is a sample test case for demonstration purposes.',
            'source_file': 'sample.xlsx'
        }

