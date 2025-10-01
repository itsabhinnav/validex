from flask import Blueprint, render_template, request, redirect, url_for, jsonify, current_app, session
import os
import pandas as pd
from datetime import datetime

# Create blueprint
main_bp = Blueprint('main', __name__)

# Global variable to store current role (temporary solution)
current_role = None

@main_bp.context_processor
def inject_current_role():
    """Inject current_role into all templates"""
    role = session.get('current_role', current_role)
    return dict(current_role=role, min=min, max=max)

# Global variable to store test cases data
test_cases_data = {}

def load_excel_files():
    """Load test cases from local files"""
    global test_cases_data
    
    print("Loading local Excel files...")
    excel_dir = current_app.config.get('UPLOAD_FOLDER', 'excel_files')
    
    if not os.path.exists(excel_dir):
        print(f"Excel directory {excel_dir} not found")
        return
    
    test_cases_data = {}
    
    # Simple file loading for now
    for root, dirs, files in os.walk(excel_dir):
        for file in files:
            if file.endswith(('.xlsx', '.xls')):
                file_path = os.path.join(root, file)
                try:
                    df = pd.read_excel(file_path)
                    if not df.empty:
                        # Print column names for debugging
                        print(f"Columns in {file}: {list(df.columns)}")
                        
                        # Add a Test Case ID if it doesn't exist
                        if 'Test Case ID' not in df.columns:
                            # Try to find similar column names
                            id_columns = [col for col in df.columns if 'id' in col.lower() or 'case' in col.lower()]
                            if id_columns:
                                # Use the first ID-like column
                                df['Test Case ID'] = df[id_columns[0]]
                            else:
                                # Generate sequential IDs
                                df['Test Case ID'] = [f"TC-{i+1:03d}" for i in range(len(df))]
                        
                        # Map actual columns to expected column names
                        if 'App' not in df.columns:
                            # Try to find app-related columns or use file name
                            app_columns = [col for col in df.columns if 'app' in col.lower()]
                            if app_columns:
                                df['App'] = df[app_columns[0]]
                            else:
                                # Extract app name from file name
                                app_name = file.replace('.xlsx', '').replace('.xls', '').split('_')[0].title()
                                df['App'] = app_name
                        
                        if 'Test Type' not in df.columns:
                            # Try to find test type columns
                            type_columns = [col for col in df.columns if 'type' in col.lower()]
                            if type_columns:
                                df['Test Type'] = df[type_columns[0]]
                            else:
                                # Extract test type from file name
                                test_type = file.replace('.xlsx', '').replace('.xls', '').split('_')[1] if '_' in file else 'Functional'
                                df['Test Type'] = test_type.title()
                        
                        test_cases_data[file] = df.to_dict('records')
                        print(f"Loaded {len(df)} test cases from {file}")
                except Exception as e:
                    print(f"Error loading {file}: {e}")
    
    print(f"Total files loaded: {len(test_cases_data)}")

@main_bp.route('/')
def index():
    """Landing page for Validex"""
    # Load files to display stats on the landing page
    load_excel_files()
    file_count = len(test_cases_data)
    total_cases = sum(len(cases) for cases in test_cases_data.values()) if test_cases_data else 0
    return render_template('landing.html', file_count=file_count, total_cases=total_cases)

@main_bp.route('/role-selection')
def role_selection():
    """Role selection page"""
    # Load files to display stats on the role selection page
    load_excel_files()
    file_count = len(test_cases_data)
    total_cases = sum(len(cases) for cases in test_cases_data.values()) if test_cases_data else 0
    return render_template('role_selection.html', file_count=file_count, total_cases=total_cases)

@main_bp.route('/dashboard')
def dashboard():
    """Dashboard page"""
    global current_role
    
    # Load files to display stats on the dashboard
    load_excel_files()
    
    # Calculate statistics
    file_count = len(test_cases_data)
    total_cases = sum(len(cases) for cases in test_cases_data.values()) if test_cases_data else 0
    
    # Get unique apps and test types
    apps = set()
    test_types = set()
    
    for file_data in test_cases_data.values():
        for case in file_data:
            if 'App' in case:
                apps.add(case['App'])
            if 'Test Type' in case:
                test_types.add(case['Test Type'])
    
    # Create app_stats object for template
    from collections import Counter
    
    # Count by app
    app_counts = Counter()
    test_type_counts = Counter()
    directory_counts = Counter()
    
    for file_data in test_cases_data.values():
        for case in file_data:
            if 'App' in case:
                app_counts[case['App']] += 1
            if 'Test Type' in case:
                test_type_counts[case['Test Type']] += 1
            # Extract directory from file path
            if 'File' in case:
                directory = case['File'].split('/')[0] if '/' in case['File'] else 'root'
                directory_counts[directory] += 1
    
    app_stats = {
        'by_app': dict(app_counts),
        'by_test_type': dict(test_type_counts),
        'by_directory': dict(directory_counts)
    }
    
    stats = {
        'total_files': file_count,
        'total_cases': total_cases,
        'apps': list(apps),
        'test_types': list(test_types)
    }
    
    return render_template('dashboard.html', stats=stats, current_role=current_role, test_cases_data=test_cases_data, app_stats=app_stats)

@main_bp.route('/test-cases')
def test_cases():
    """Test cases page with filtering and search"""
    global current_role
    
    # Load files
    load_excel_files()
    
    # Get filter parameters
    app_filter = request.args.get('app', '')
    test_type_filter = request.args.get('test_type', '')
    status_filter = request.args.get('status', '')
    priority_filter = request.args.get('priority', '')
    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort', 'Test Case ID')
    sort_order = request.args.get('order', 'asc')
    
    # Get dynamic filter parameters
    dynamic_filters = {}
    for key, value in request.args.items():
        if key.startswith('dynamic_') and value:
            filter_column = key.replace('dynamic_', '').replace('_', ' ').title()
            dynamic_filters[filter_column] = value
    
    # Get selected test case IDs (for selective export)
    selected_ids = request.args.get('selected_ids', '')
    selected_id_list = selected_ids.split(',') if selected_ids else []
    
    # Filter test cases
    filtered_cases = []
    for file_name, file_data in test_cases_data.items():
        for case in file_data:
            # Add source file information
            case['source_file'] = file_name
            
            # Apply filters
            if app_filter and case.get('App', '') != app_filter:
                continue
            if test_type_filter and case.get('Test Type', '') != test_type_filter:
                continue
            if status_filter and case.get('Status', '').lower() != status_filter.lower():
                continue
            if priority_filter and case.get('Priority', '').lower() != priority_filter.lower():
                continue
            if search_query:
                search_text = ' '.join(str(v) for v in case.values() if v).lower()
                if search_query.lower() not in search_text:
                    continue
            
            # Apply dynamic filters
            for filter_column, filter_value in dynamic_filters.items():
                if case.get(filter_column, '') != filter_value:
                    continue
            
            # Apply selected IDs filter (if specified)
            if selected_id_list and selected_id_list[0]:  # Only if specific IDs are selected
                case_id = str(case.get('Test Case ID', case.get('TC ID', '')))
                if case_id not in selected_id_list:
                    continue
            
            filtered_cases.append(case)
    
    # Sort test cases
    if sort_by in ['Test Case ID', 'Summary', 'App', 'Test Type', 'Feature', 'Status', 'Priority']:
        try:
            reverse = sort_order.lower() == 'desc'
            filtered_cases.sort(key=lambda x: str(x.get(sort_by, '')).lower(), reverse=reverse)
        except:
            pass  # Keep original order if sorting fails
    
    # Pagination
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 25))
    
    total_cases = len(filtered_cases)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    paginated_cases = filtered_cases[start_idx:end_idx]
    
    # Calculate pagination info
    total_pages = (total_cases + per_page - 1) // per_page
    has_prev = page > 1
    has_next = page < total_pages
    
    # Get unique values for filters
    apps = set()
    test_types = set()
    statuses = set()
    priorities = set()
    
    for file_data in test_cases_data.values():
        for case in file_data:
            if 'App' in case:
                apps.add(case['App'])
            if 'Test Type' in case:
                test_types.add(case['Test Type'])
            if 'Status' in case:
                statuses.add(case['Status'])
            if 'Priority' in case:
                priorities.add(case['Priority'])
    
    return render_template('test_cases.html', 
                         test_cases=paginated_cases,
                         apps=sorted(apps),
                         test_types=sorted(test_types),
                         statuses=sorted(statuses),
                         priorities=sorted(priorities),
                         current_app_filter=app_filter,
                         current_test_type_filter=test_type_filter,
                         current_status_filter=status_filter,
                         current_priority_filter=priority_filter,
                         current_search=search_query,
                         current_sort=sort_by,
                         current_order=sort_order,
                         current_role=current_role,
                         dynamic_filters=dynamic_filters,
                         # Pagination info
                         page=page,
                         per_page=per_page,
                         total_cases=total_cases,
                         total_pages=total_pages,
                         has_prev=has_prev,
                         has_next=has_next)

@main_bp.route('/admin')
def admin():
    """Admin page"""
    global current_role
    role = session.get('current_role', current_role)
    
    if role != 'admin':
        return redirect(url_for('main.role_selection'))
    
    # Load files for admin stats
    load_excel_files()
    
    file_count = len(test_cases_data)
    total_cases = sum(len(cases) for cases in test_cases_data.values()) if test_cases_data else 0
    
    return render_template('admin.html', 
                         file_count=file_count, 
                         total_cases=total_cases,
                         current_role=current_role,
                         test_cases_data=test_cases_data)

@main_bp.route('/reports')
def reports():
    """Reports page"""
    global current_role
    role = session.get('current_role', current_role)
    
    if not role:
        return redirect(url_for('main.role_selection'))
    
    # Load files for reports
    load_excel_files()
    
    file_count = len(test_cases_data)
    total_cases = sum(len(cases) for cases in test_cases_data.values()) if test_cases_data else 0
    
    return render_template('reports.html', 
                         file_count=file_count, 
                         total_cases=total_cases,
                         current_role=role,
                         test_cases_data=test_cases_data)

@main_bp.route('/execute-test')
def execute_test():
    """Execute test page"""
    global current_role
    role = session.get('current_role', current_role)
    
    if not role:
        return redirect(url_for('main.role_selection'))
    
    # Get test case ID from query parameters
    test_id = request.args.get('test_id')
    source_file = request.args.get('source_file')
    
    # Load files to find the test case
    load_excel_files()
    
    test_case = None
    if test_id and source_file:
        # Find the specific test case
        for file_name, file_data in test_cases_data.items():
            if file_name == source_file:
                for case in file_data:
                    case_id = case.get('Test Case ID', case.get('TC ID', ''))
                    if str(case_id) == str(test_id):
                        test_case = case
                        test_case['source_file'] = file_name
                        break
                break
    
    # If no specific test case, create a sample one
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
    
    return render_template('execute_test.html', 
                         current_role=role, 
                         test_case=test_case)

@main_bp.route('/execute-test', methods=['POST'])
def submit_test_execution():
    """Handle test execution submission"""
    global current_role
    role = session.get('current_role', current_role)
    
    if not role:
        return redirect(url_for('main.role_selection'))
    
    # Get form data
    test_id = request.form.get('test_id')
    source_file = request.form.get('source_file')
    result = request.form.get('result')
    execution_time = request.form.get('execution_time')
    environment = request.form.get('environment')
    comments = request.form.get('comments')
    
    # Here you would typically save the execution result to a database
    # For now, we'll just redirect back to test cases with a success message
    
    return redirect(url_for('main.test_cases', 
                           message=f'Test execution recorded successfully! Result: {result}'))

@main_bp.route('/export-test-cases')
def export_test_cases():
    """Export test cases to Excel"""
    global current_role
    role = session.get('current_role', current_role)
    
    if not role:
        return redirect(url_for('main.role_selection'))
    
    # Load files
    load_excel_files()
    
    # Get filter parameters (same as test_cases route)
    app_filter = request.args.get('app', '')
    test_type_filter = request.args.get('test_type', '')
    status_filter = request.args.get('status', '')
    priority_filter = request.args.get('priority', '')
    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort', 'Test Case ID')
    sort_order = request.args.get('order', 'asc')
    
    # Get dynamic filter parameters
    dynamic_filters = {}
    for key, value in request.args.items():
        if key.startswith('dynamic_') and value:
            filter_column = key.replace('dynamic_', '').replace('_', ' ').title()
            dynamic_filters[filter_column] = value
    
    # Get selected test case IDs (for selective export)
    selected_ids = request.args.get('selected_ids', '')
    selected_id_list = selected_ids.split(',') if selected_ids else []
    
    # Filter test cases (same logic as test_cases route)
    filtered_cases = []
    for file_name, file_data in test_cases_data.items():
        for case in file_data:
            # Add source file information
            case['source_file'] = file_name
            
            # Apply filters
            if app_filter and case.get('App', '') != app_filter:
                continue
            if test_type_filter and case.get('Test Type', '') != test_type_filter:
                continue
            if status_filter and case.get('Status', '').lower() != status_filter.lower():
                continue
            if priority_filter and case.get('Priority', '').lower() != priority_filter.lower():
                continue
            if search_query:
                search_text = ' '.join(str(v) for v in case.values() if v).lower()
                if search_query.lower() not in search_text:
                    continue
            
            # Apply dynamic filters
            for filter_column, filter_value in dynamic_filters.items():
                if case.get(filter_column, '') != filter_value:
                    continue
            
            # Apply selected IDs filter (if specified)
            if selected_id_list and selected_id_list[0]:  # Only if specific IDs are selected
                case_id = str(case.get('Test Case ID', case.get('TC ID', '')))
                if case_id not in selected_id_list:
                    continue
            
            filtered_cases.append(case)
    
    # Sort test cases
    if sort_by in ['Test Case ID', 'Summary', 'App', 'Test Type', 'Feature', 'Status', 'Priority']:
        try:
            reverse = sort_order.lower() == 'desc'
            filtered_cases.sort(key=lambda x: str(x.get(sort_by, '')).lower(), reverse=reverse)
        except:
            pass  # Keep original order if sorting fails
    
    # Create DataFrame
    if filtered_cases:
        df = pd.DataFrame(filtered_cases)
        
        # Reorder columns for better readability
        column_order = ['Test Case ID', 'Summary', 'App', 'Test Type', 'Feature', 'Priority', 'Status', 'Expected Behavior', 'source_file']
        existing_columns = [col for col in column_order if col in df.columns]
        other_columns = [col for col in df.columns if col not in existing_columns]
        df = df[existing_columns + other_columns]
        
        # Create Excel file in memory
        from io import BytesIO
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Test Cases', index=False)
            
            # Get the workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['Test Cases']
            
            # Auto-adjust column widths
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
        
        # Create filename with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_cases_export_{timestamp}.xlsx"
        
        # Return Excel file
        from flask import Response
        return Response(
            output.getvalue(),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )
    else:
        return redirect(url_for('main.test_cases', message='No test cases found to export'))

@main_bp.route('/export-test-cases-csv')
def export_test_cases_csv():
    """Export test cases to CSV"""
    global current_role
    role = session.get('current_role', current_role)
    
    if not role:
        return redirect(url_for('main.role_selection'))
    
    # Load files
    load_excel_files()
    
    # Get filter parameters (same as test_cases route)
    app_filter = request.args.get('app', '')
    test_type_filter = request.args.get('test_type', '')
    status_filter = request.args.get('status', '')
    priority_filter = request.args.get('priority', '')
    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort', 'Test Case ID')
    sort_order = request.args.get('order', 'asc')
    
    # Get dynamic filter parameters
    dynamic_filters = {}
    for key, value in request.args.items():
        if key.startswith('dynamic_') and value:
            filter_column = key.replace('dynamic_', '').replace('_', ' ').title()
            dynamic_filters[filter_column] = value
    
    # Get selected test case IDs (for selective export)
    selected_ids = request.args.get('selected_ids', '')
    selected_id_list = selected_ids.split(',') if selected_ids else []
    
    # Filter test cases (same logic as test_cases route)
    filtered_cases = []
    for file_name, file_data in test_cases_data.items():
        for case in file_data:
            # Add source file information
            case['source_file'] = file_name
            
            # Apply filters
            if app_filter and case.get('App', '') != app_filter:
                continue
            if test_type_filter and case.get('Test Type', '') != test_type_filter:
                continue
            if status_filter and case.get('Status', '').lower() != status_filter.lower():
                continue
            if priority_filter and case.get('Priority', '').lower() != priority_filter.lower():
                continue
            if search_query:
                search_text = ' '.join(str(v) for v in case.values() if v).lower()
                if search_query.lower() not in search_text:
                    continue
            
            # Apply dynamic filters
            for filter_column, filter_value in dynamic_filters.items():
                if case.get(filter_column, '') != filter_value:
                    continue
            
            # Apply selected IDs filter (if specified)
            if selected_id_list and selected_id_list[0]:  # Only if specific IDs are selected
                case_id = str(case.get('Test Case ID', case.get('TC ID', '')))
                if case_id not in selected_id_list:
                    continue
            
            filtered_cases.append(case)
    
    # Sort test cases
    if sort_by in ['Test Case ID', 'Summary', 'App', 'Test Type', 'Feature', 'Status', 'Priority']:
        try:
            reverse = sort_order.lower() == 'desc'
            filtered_cases.sort(key=lambda x: str(x.get(sort_by, '')).lower(), reverse=reverse)
        except:
            pass  # Keep original order if sorting fails
    
    # Create DataFrame
    if filtered_cases:
        df = pd.DataFrame(filtered_cases)
        
        # Reorder columns for better readability
        column_order = ['Test Case ID', 'Summary', 'App', 'Test Type', 'Feature', 'Priority', 'Status', 'Expected Behavior', 'source_file']
        existing_columns = [col for col in column_order if col in df.columns]
        other_columns = [col for col in df.columns if col not in existing_columns]
        df = df[existing_columns + other_columns]
        
        # Create CSV file in memory
        from io import StringIO
        output = StringIO()
        df.to_csv(output, index=False)
        output.seek(0)
        
        # Create filename with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_cases_export_{timestamp}.csv"
        
        # Return CSV file
        from flask import Response
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )
    else:
        return redirect(url_for('main.test_cases', message='No test cases found to export'))

@main_bp.route('/setup')
def setup():
    """Setup page"""
    return render_template('setup.html')

@main_bp.route('/jfrog-config')
def jfrog_config():
    """JFrog configuration page"""
    global current_role
    role = session.get('current_role', current_role)
    
    if role != 'admin':
        return redirect(url_for('main.role_selection'))
    
    # Create a default JFrog config object
    jfrog_config = {
        'base_url': '',
        'username': '',
        'password': '',
        'repository': '',
        'enabled': False
    }
    
    return render_template('jfrog_config.html', current_role=role, jfrog_config=jfrog_config)

@main_bp.route('/set-role', methods=['POST'])
def set_role():
    """Set user role"""
    global current_role
    role = request.form.get('role')
    current_role = role
    session['current_role'] = role
    
    if role == 'admin':
        return redirect(url_for('main.admin'))
    else:
        return redirect(url_for('main.dashboard'))

@main_bp.route('/logout')
def logout():
    """Logout and return to role selection"""
    global current_role
    current_role = None
    session.pop('current_role', None)
    return redirect(url_for('main.role_selection'))

@main_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@main_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return render_template('500.html'), 500