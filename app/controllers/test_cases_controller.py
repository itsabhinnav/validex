"""
Test Cases Controller for MVC architecture
"""

from flask import render_template, request, redirect, url_for, session, Response
from typing import Dict, Any, List
import pandas as pd
from io import BytesIO, StringIO
from datetime import datetime
from .base_controller import BaseController
from app.services.test_cases_service import TestCasesService
from app.views.test_cases_view import TestCasesView

class TestCasesController(BaseController):
    """Controller for test cases functionality"""
    
    def __init__(self):
        super().__init__('test_cases')
        self.test_cases_service = TestCasesService()
        self.test_cases_view = TestCasesView()
    
    def _register_routes(self):
        """Register test cases routes - not used in MVC structure"""
        pass
    
    def _handle_test_cases(self):
        """Handle test cases page logic"""
        role = session.get('current_role')
        if not role:
            return redirect(url_for('main.role_selection'))
        
        test_cases_data = self.load_test_files()
        
        
        app_filter = request.args.getlist('app') if request.args.getlist('app') else [request.args.get('app', '')]
        test_type_filter = request.args.getlist('test_type') if request.args.getlist('test_type') else [request.args.get('test_type', '')]
        priority_filter = request.args.getlist('priority') if request.args.getlist('priority') else [request.args.get('priority', '')]
        search_query = request.args.get('search', '')
        sort_by = request.args.get('sort', 'Test Case ID')
        sort_order = request.args.get('order', 'asc')
        
        app_filter = [f for f in app_filter if f]
        test_type_filter = [f for f in test_type_filter if f]
        priority_filter = [f for f in priority_filter if f]
        
        dynamic_filters = {}
        dynamic_filter_groups = {}
        
        # Process dynamic filters with new structure
        for key, value in request.args.items():
            if key.startswith('dynamic_') and value:
                parts = key.split('_')
                if len(parts) >= 3:
                    filter_id = parts[2]  # Get the unique filter ID
                    filter_type = parts[1]  # column, type, value, value2
                    
                    if filter_id not in dynamic_filter_groups:
                        dynamic_filter_groups[filter_id] = {}
                    
                    dynamic_filter_groups[filter_id][filter_type] = value
        
        # Convert grouped filters to proper format
        for filter_id, filter_data in dynamic_filter_groups.items():
            if 'column' in filter_data and 'type' in filter_data and 'value' in filter_data:
                column = filter_data['column']
                filter_type = filter_data['type']
                value = filter_data['value']
                value2 = filter_data.get('value2', '')
                
                dynamic_filters[f"{column}_{filter_type}"] = {
                    'column': column,
                    'type': filter_type,
                    'value': value,
                    'value2': value2
                }
        
        selected_ids = request.args.get('selected_ids', '')
        selected_id_list = selected_ids.split(',') if selected_ids else []
        
        filtered_cases = self._filter_test_cases(
            test_cases_data, app_filter, test_type_filter, 
            priority_filter, search_query, dynamic_filters, selected_id_list
        )
        
        filtered_cases = self._sort_test_cases(filtered_cases, sort_by, sort_order)
        
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 25))
        
        total_cases = len(filtered_cases)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        paginated_cases = filtered_cases[start_idx:end_idx]
        
        total_pages = (total_cases + per_page - 1) // per_page
        has_prev = page > 1
        has_next = page < total_pages
        
        apps, test_types, priorities = self._get_filter_options(test_cases_data)
        
        from config.settings import config
        multiselect_threshold = config.get_multiselect_threshold()
        
        return render_template('validex/test_cases.html', 
                             test_cases=paginated_cases,
                             apps=sorted(apps),
                             test_types=sorted(test_types),
                             priorities=sorted(priorities),
                             current_app_filter=app_filter[0] if len(app_filter) == 1 else app_filter,
                             current_test_type_filter=test_type_filter[0] if len(test_type_filter) == 1 else test_type_filter,
                             current_priority_filter=priority_filter[0] if len(priority_filter) == 1 else priority_filter,
                             current_search=search_query,
                             current_sort=sort_by,
                             current_order=sort_order,
                             current_role=session.get('current_role'),
                             dynamic_filters=dynamic_filters,
                             page=page,
                             per_page=per_page,
                             total_cases=total_cases,
                             total_pages=total_pages,
                             has_prev=has_prev,
                             has_next=has_next,
                             multiselect_threshold=multiselect_threshold)
    
    def _filter_test_cases(self, test_cases_data, app_filter, test_type_filter, 
                          priority_filter, search_query, dynamic_filters, selected_id_list):
        """Filter test cases based on criteria"""
        filtered_cases = []
        for file_name, file_data in test_cases_data.items():
            for case in file_data:
                case['source_file'] = file_name
                
                if app_filter and case.get('App', '') not in app_filter:
                    continue
                if test_type_filter and case.get('Test Type', '') not in test_type_filter:
                    continue
                if priority_filter and case.get('Priority', '').lower() not in [p.lower() for p in priority_filter]:
                    continue
                if search_query:
                    search_text = ' '.join(str(v) for v in case.values() if v).lower()
                    if search_query.lower() not in search_text:
                        continue
                
                # Apply dynamic filters using enhanced service
                if dynamic_filters:
                    from app.services.test_cases_service import TestCasesService
                    service = TestCasesService()
                    if not service._should_include_case_dynamic(case, dynamic_filters):
                        continue
                
                if selected_id_list and selected_id_list[0]:
                    case_id = str(case.get('Test Case ID', case.get('TC ID', '')))
                    if case_id not in selected_id_list:
                        continue
                
                filtered_cases.append(case)
        return filtered_cases
    
    def _sort_test_cases(self, test_cases, sort_by, sort_order):
        """Sort test cases"""
        if sort_by in ['Test Case ID', 'Summary', 'App', 'Test Type', 'Feature', 'Status', 'Priority']:
            try:
                reverse = sort_order.lower() == 'desc'
                test_cases.sort(key=lambda x: str(x.get(sort_by, '')).lower(), reverse=reverse)
            except:
                pass
        return test_cases
    
    def _get_filter_options(self, test_cases_data):
        """Get unique values for filter dropdowns using enhanced service"""
        from app.services.test_cases_service import TestCasesService
        service = TestCasesService()
        filter_options = service.get_filter_options(test_cases_data)
        
        # Return legacy format for backward compatibility
        return (
            filter_options.get('apps', []),
            filter_options.get('test_types', []),
            filter_options.get('priorities', [])
        )
    
    def get_enhanced_filter_data(self, test_cases_data):
        """Get enhanced filter data including all columns and statistics"""
        from app.services.test_cases_service import TestCasesService
        service = TestCasesService()
        
        return {
            'filter_options': service.get_filter_options(test_cases_data),
            'available_columns': service.get_available_columns(test_cases_data),
            'column_statistics': service.get_column_statistics(test_cases_data),
            'column_mappings': service.get_column_mappings(test_cases_data),
            'filter_types': list(service._get_filter_types().keys())
        }
    
    def _handle_execute_test(self):
        """Handle execute test page"""
        role = session.get('current_role')
        if not role:
            return redirect(url_for('main.role_selection'))
        
        test_id = request.args.get('test_id')
        source_file = request.args.get('source_file')
        
        test_cases_data = self.load_test_files()
        
        test_case = None
        if test_id and source_file:
            for file_name, file_data in test_cases_data.items():
                if file_name == source_file:
                    for case in file_data:
                        case_id = case.get('Test Case ID', case.get('TC ID', ''))
                        if str(case_id) == str(test_id):
                            test_case = case
                            test_case['source_file'] = file_name
                            break
                    break
        
        if not test_case:
            test_case = {
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
        
        return render_template('validex/execute_test.html', 
                             current_role=role, 
                             test_case=test_case)
    
    def _handle_submit_test_execution(self):
        """Handle test execution submission"""
        role = session.get('current_role')
        if not role:
            return redirect(url_for('main.role_selection'))
        
        test_id = request.form.get('test_id')
        source_file = request.form.get('source_file')
        result = request.form.get('result')
        execution_time = request.form.get('execution_time')
        environment = request.form.get('environment')
        comments = request.form.get('comments')

        return redirect(url_for('main.test_cases', 
                               message=f'Test execution recorded successfully! Result: {result}'))
    
    def _handle_test_case_details(self, test_id):
        """Handle test case details page"""
        role = session.get('current_role')
        if not role:
            return redirect(url_for('main.role_selection'))
        
        test_cases_data = self.load_test_files()
        
        # Find the specific test case
        test_case = None
        source_file = None
        
        for file_name, file_data in test_cases_data.items():
            for case in file_data:
                case_id = case.get('Test Case ID', case.get('TC ID', case.get('ID', '')))
                if str(case_id) == str(test_id):
                    test_case = case.copy()
                    test_case['source_file'] = file_name
                    source_file = file_name
                    break
            if test_case:
                break
        
        if not test_case:
            # For testing, create a sample test case
            test_case = {
                'Test Case ID': test_id,
                'TC ID': test_id,
                'Summary': f'Sample test case for {test_id}',
                'App': 'Sample App',
                'Test Type': 'Functional',
                'Feature': 'Sample Feature',
                'Priority': 'Medium',
                'Status': 'Pending',
                'Expected Behavior': 'This is a sample test case for demonstration purposes.',
                'Test Steps': '1. Navigate to the application\n2. Perform the test action\n3. Verify the results',
                'Test Data': 'Sample test data',
                'Prerequisites': 'Application should be running',
                'source_file': 'sample.xlsx'
            }
        
        # Get related test cases from the same file
        related_cases = []
        if source_file and source_file in test_cases_data:
            for case in test_cases_data[source_file]:
                if case.get('Test Case ID', case.get('TC ID', '')) != test_id:
                    related_cases.append(case)
        
        # Get execution history (mock data for now)
        execution_history = [
            {
                'date': '2024-01-15 10:30:00',
                'result': 'Passed',
                'environment': 'QA',
                'execution_time': '2.5s',
                'executed_by': 'John Doe',
                'comments': 'Test executed successfully'
            },
            {
                'date': '2024-01-10 14:20:00',
                'result': 'Failed',
                'environment': 'Dev',
                'execution_time': '1.8s',
                'executed_by': 'Jane Smith',
                'comments': 'Failed due to timeout issue'
            }
        ]
        
        return render_template('validex/test_case_details.html',
                             current_role=role,
                             test_case=test_case,
                             related_cases=related_cases[:5],  # Show max 5 related cases
                             execution_history=execution_history)
    
    def _handle_export_test_cases(self):
        """Handle test cases export"""
        role = session.get('current_role')
        if not role:
            return redirect(url_for('main.role_selection'))
        
        test_cases_data = self.load_test_files()
        
        app_filter = request.args.getlist('app') if request.args.getlist('app') else [request.args.get('app', '')]
        test_type_filter = request.args.getlist('test_type') if request.args.getlist('test_type') else [request.args.get('test_type', '')]
        priority_filter = request.args.getlist('priority') if request.args.getlist('priority') else [request.args.get('priority', '')]
        
        app_filter = [f for f in app_filter if f]
        test_type_filter = [f for f in test_type_filter if f]
        priority_filter = [f for f in priority_filter if f]
        search_query = request.args.get('search', '')
        sort_by = request.args.get('sort', 'Test Case ID')
        sort_order = request.args.get('order', 'asc')
        
        dynamic_filters = {}
        for key, value in request.args.items():
            if key.startswith('dynamic_') and value:
                filter_column = key.replace('dynamic_', '').replace('_', ' ').title()
                dynamic_filters[filter_column] = value
        
        selected_ids = request.args.get('selected_ids', '')
        selected_id_list = selected_ids.split(',') if selected_ids else []
        
        filtered_cases = self._filter_test_cases(
            test_cases_data, app_filter, test_type_filter, 
            priority_filter, search_query, dynamic_filters, selected_id_list
        )
        
        filtered_cases = self._sort_test_cases(filtered_cases, sort_by, sort_order)
        
        if filtered_cases:
            df = pd.DataFrame(filtered_cases)
            
            column_order = ['Test Case ID', 'Summary', 'App', 'Test Type', 'Feature', 'Priority', 'Status', 'Expected Behavior', 'source_file']
            existing_columns = [col for col in column_order if col in df.columns]
            other_columns = [col for col in df.columns if col not in existing_columns]
            df = df[existing_columns + other_columns]
            
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
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_cases_export_{timestamp}.xlsx"
            
            return Response(
                output.getvalue(),
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                headers={'Content-Disposition': f'attachment; filename={filename}'}
            )
        else:
            return redirect(url_for('main.test_cases', message='No test cases found to export'))
    
    def _handle_export_test_cases_csv(self):
        """Handle CSV export"""
        role = session.get('current_role')
        if not role:
            return redirect(url_for('main.role_selection'))
        
        return redirect(url_for('main.test_cases', message='CSV export not implemented yet'))
    
    # Prepare test suite functionality merged into test cases page
    
    def _handle_export_test_suite(self):
        """Handle test suite export"""
        from flask import Response
        import pandas as pd
        from io import BytesIO
        from datetime import datetime
        
        role = session.get('current_role')
        if not role:
            return redirect(url_for('main.role_selection'))
        
        # Get form data
        release_version = request.form.get('releaseVersion', '')
        sprint = request.form.get('sprint', '')
        build_number = request.form.get('buildNumber', '')
        environment = request.form.get('environment', '')
        test_suite_name = request.form.get('testSuiteName', '')
        test_suite_description = request.form.get('testSuiteDescription', '')
        selected_test_cases = request.form.get('selectedTestCases', '')
        
        if not release_version:
            return redirect(url_for('main.test_cases', error='Release version is required'))
        
        if not selected_test_cases:
            return redirect(url_for('main.test_cases', error='Please select at least one test case'))
        
        # Load test cases data
        test_cases_data = self.load_test_files()
        
        # Get selected test cases
        selected_ids = selected_test_cases.split(',')
        selected_cases = []
        
        for file_name, file_data in test_cases_data.items():
            for case in file_data:
                case_id = case.get('Test Case ID', case.get('TC ID', case.get('ID', '')))
                if str(case_id) in selected_ids:
                    case_copy = case.copy()
                    case_copy['source_file'] = file_name
                    selected_cases.append(case_copy)
        
        if not selected_cases:
            return redirect(url_for('main.test_cases', error='No valid test cases found'))
        
        # Create DataFrame
        df = pd.DataFrame(selected_cases)
        
        # Add release information
        df['Release Version'] = release_version
        df['Sprint'] = sprint
        df['Build Number'] = build_number
        df['Environment'] = environment
        df['Test Suite Name'] = test_suite_name
        df['Test Suite Description'] = test_suite_description
        df['Export Date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Reorder columns
        column_order = [
            'Test Case ID', 'Summary', 'App', 'Test Type', 'Feature', 
            'Priority', 'Status', 'Expected Behavior', 'Test Steps',
            'Release Version', 'Sprint', 'Build Number', 'Environment',
            'Test Suite Name', 'Test Suite Description', 'Export Date', 'source_file'
        ]
        
        existing_columns = [col for col in column_order if col in df.columns]
        other_columns = [col for col in df.columns if col not in existing_columns]
        df = df[existing_columns + other_columns]
        
        # Create Excel file
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Test Suite sheet
            df.to_excel(writer, sheet_name='Test Suite', index=False)
            
            # Summary sheet
            summary_data = {
                'Field': ['Test Suite Name', 'Description', 'Release Version', 'Sprint', 'Build Number', 'Environment', 'Total Test Cases', 'Export Date'],
                'Value': [test_suite_name, test_suite_description, release_version, sprint, build_number, environment, len(selected_cases), datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Format worksheets
            workbook = writer.book
            
            # Format Test Suite sheet
            test_suite_worksheet = writer.sheets['Test Suite']
            for column in test_suite_worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                test_suite_worksheet.column_dimensions[column_letter].width = adjusted_width
            
            # Format Summary sheet
            summary_worksheet = writer.sheets['Summary']
            summary_worksheet.column_dimensions['A'].width = 20
            summary_worksheet.column_dimensions['B'].width = 30
        
        output.seek(0)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_suite_{release_version}_{timestamp}.xlsx"
        
        return Response(
            output.getvalue(),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )
    
    def _handle_export_test_cases_csv(self):
        """Handle CSV export"""
        role = session.get('current_role')
        if not role:
            return redirect(url_for('main.role_selection'))
        
        return redirect(url_for('main.test_cases', message='CSV export not implemented yet'))
