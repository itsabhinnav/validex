from flask import Flask, render_template, request, redirect, url_for, jsonify
import pandas as pd
import os
from datetime import datetime
import json
from config import config
from jfrog_client import jfrog_client

app = Flask(__name__)

# Global variable to store current role (temporary solution)
current_role = None

@app.context_processor
def inject_current_role():
    """Inject current_role into all templates"""
    return dict(current_role=current_role, jfrog_config=config.get_jfrog_config())

# Configuration
app.config['UPLOAD_FOLDER'] = config.get('app.excel_files_dir', 'excel_files')
app.config['REPORTS_FOLDER'] = config.get('app.reports_dir', 'reports')
app.config['SECRET_KEY'] = 'validex-secret-key-2024'

# Create directories if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['REPORTS_FOLDER'], exist_ok=True)
os.makedirs('templates', exist_ok=True)
os.makedirs('static', exist_ok=True)

# Global variable to store test cases data
test_cases_data = {}

def load_excel_files():
    """Load all Excel files from the excel_files directory"""
    global test_cases_data
    test_cases_data = {}
    
    # Try to sync files from JFrog if enabled
    if config.is_jfrog_enabled():
        try:
            print("JFrog integration enabled, attempting to sync files...")
            jfrog_client.sync_excel_files()
        except Exception as e:
            print(f"JFrog sync failed: {e}")
    
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        return
    
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        if filename.endswith(('.xlsx', '.xls')):
            try:
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                df = pd.read_excel(file_path)
                
                # Store the data with filename as key
                test_cases_data[filename] = df.to_dict('records')
                print(f"Loaded {len(df)} test cases from {filename}")
            except Exception as e:
                print(f"Error loading {filename}: {str(e)}")

@app.route('/')
def index():
    """Landing page for Validex"""
    # Load files to display stats on the landing page
    load_excel_files()
    file_count = len(test_cases_data)
    total_cases = sum(len(cases) for cases in test_cases_data.values()) if test_cases_data else 0
    return render_template('landing.html', file_count=file_count, total_cases=total_cases)

@app.route('/role-selection')
def role_selection():
    """Role selection page"""
    # Load files to display stats on the role selection page
    load_excel_files()
    file_count = len(test_cases_data)
    total_cases = sum(len(cases) for cases in test_cases_data.values()) if test_cases_data else 0
    sample_files = list(test_cases_data.keys())[:3]
    return render_template('role_selection.html', file_count=file_count, total_cases=total_cases, sample_files=sample_files)

@app.route('/select_role', methods=['POST'])
def select_role():
    """Handle role selection"""
    global current_role
    role = request.form.get('role')
    if role in ['admin', 'tester']:
        current_role = role
        return redirect(url_for('dashboard'))
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    """Main dashboard based on user role"""
    global current_role
    if not current_role:
        return redirect(url_for('index'))
    
    # Load Excel files
    load_excel_files()
    
    # Calculate total test cases
    total_cases = sum(len(cases) for cases in test_cases_data.values()) if test_cases_data else 0
    
    return render_template('dashboard.html', role=current_role, test_cases_data=test_cases_data, total_cases=total_cases)

@app.route('/test_cases')
def test_cases():
    """Display test cases with filtering options"""
    global current_role
    if not current_role:
        return redirect(url_for('index'))
    # Admin should not browse/execute tests
    if current_role == 'admin':
        return redirect(url_for('admin_panel'))
    
    # Get filter parameters
    file_filter = request.args.get('file', '')
    status_filter = request.args.get('status', '')
    feature_filter = request.args.get('feature', '')
    
    # Filter test cases
    filtered_cases = []
    for filename, cases in test_cases_data.items():
        if file_filter and file_filter not in filename:
            continue
        
        for case in cases:
            # Apply additional filters if needed
            if status_filter and case.get('Status', '').lower() != status_filter.lower():
                continue
            if feature_filter and feature_filter.lower() not in str(case.get('Feature', '')).lower():
                continue
            
            case['source_file'] = filename
            filtered_cases.append(case)
    
    return render_template('test_cases.html', 
                         test_cases=filtered_cases, 
                         available_files=list(test_cases_data.keys()),
                         role=current_role)

@app.route('/execute_test/<test_id>')
def execute_test(test_id):
    """Execute a specific test case"""
    global current_role
    if not current_role:
        return redirect(url_for('index'))
    # Admin should not execute tests
    if current_role == 'admin':
        return redirect(url_for('admin_panel'))
    
    # Find the test case
    test_case = None
    source_file = None
    for filename, cases in test_cases_data.items():
        for case in cases:
            if str(case.get('Test Case ID', '')) == test_id:
                test_case = case
                source_file = filename
                break
        if test_case:
            break
    
    if not test_case:
        return "Test case not found", 404
    
    return render_template('execute_test.html', 
                         test_case=test_case, 
                         source_file=source_file,
                         role=current_role)

@app.route('/submit_test_result', methods=['POST'])
def submit_test_result():
    """Submit test execution result"""
    global current_role
    if not current_role:
        return redirect(url_for('index'))
    
    test_id = request.form.get('test_id')
    result = request.form.get('result')
    comments = request.form.get('comments', '')
    execution_time = request.form.get('execution_time', '')
    
    # Save test result to a report file
    report_data = {
        'test_id': test_id,
        'result': result,
        'comments': comments,
        'execution_time': execution_time,
        'timestamp': datetime.now().isoformat(),
        'executed_by': current_role
    }
    
    # Append to report file
    report_file = os.path.join(app.config['REPORTS_FOLDER'], 'test_execution_report.jsonl')
    with open(report_file, 'a') as f:
        f.write(json.dumps(report_data) + '\n')
    
    return redirect(url_for('test_cases'))

@app.route('/admin')
def admin_panel():
    """Admin panel for managing test cases"""
    global current_role
    if current_role != 'admin':
        return redirect(url_for('dashboard'))
    
    # Load Excel files
    load_excel_files()
    
    return render_template('admin.html', test_cases_data=test_cases_data)

# ---------------------- Admin: Upload/Add/Edit ---------------------- #
ALLOWED_EXTENSIONS = {'.xlsx', '.xls'}

def allowed_file(filename: str) -> bool:
    _, ext = os.path.splitext(filename)
    return ext.lower() in ALLOWED_EXTENSIONS

def ensure_columns(df: pd.DataFrame) -> pd.DataFrame:
    expected_columns = [
        'Test Case ID', 'Test Case Title', 'Feature', 'Priority', 'Status',
        'Preconditions', 'Given', 'When', 'Then', 'Expected Behavior', 'Remarks'
    ]
    for col in expected_columns:
        if col not in df.columns:
            df[col] = ''
    return df[expected_columns]

@app.route('/admin/upload', methods=['POST'])
def admin_upload():
    global current_role
    if current_role != 'admin':
        return redirect(url_for('dashboard'))
    file = request.files.get('file')
    if not file or file.filename == '':
        return redirect(url_for('admin_panel'))
    if not allowed_file(file.filename):
        return redirect(url_for('admin_panel'))
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(save_path)
    return redirect(url_for('admin_panel'))

@app.route('/admin/add', methods=['GET', 'POST'])
def admin_add():
    global current_role
    if current_role != 'admin':
        return redirect(url_for('dashboard'))
    filename = request.args.get('file') or request.form.get('file')
    if request.method == 'GET':
        return render_template('admin_edit.html', mode='add', filename=filename, test_case={})
    # POST create new test case row
    if not filename:
        return redirect(url_for('admin_panel'))
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        df = pd.read_excel(file_path)
    else:
        df = pd.DataFrame()
    df = ensure_columns(df)
    new_case = {
        'Test Case ID': request.form.get('test_id', '').strip(),
        'Test Case Title': request.form.get('title', '').strip(),
        'Feature': request.form.get('feature', '').strip(),
        'Priority': request.form.get('priority', '').strip(),
        'Status': request.form.get('status', '').strip() or 'Pending',
        'Preconditions': request.form.get('preconditions', '').strip(),
        'Given': request.form.get('given', '').strip(),
        'When': request.form.get('when', '').strip(),
        'Then': request.form.get('then', '').strip(),
        'Expected Behavior': request.form.get('expected', '').strip(),
        'Remarks': request.form.get('remarks', '').strip(),
    }
    df = pd.concat([df, pd.DataFrame([new_case])], ignore_index=True)
    df = ensure_columns(df)
    df.to_excel(file_path, index=False)
    return redirect(url_for('admin_panel'))

@app.route('/admin/edit', methods=['GET', 'POST'])
def admin_edit():
    global current_role
    if current_role != 'admin':
        return redirect(url_for('dashboard'))
    filename = request.args.get('file') or request.form.get('file')
    test_id = request.args.get('id') or request.form.get('test_id')
    if not filename:
        return redirect(url_for('admin_panel'))
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(file_path):
        return redirect(url_for('admin_panel'))
    df = pd.read_excel(file_path)
    df = ensure_columns(df)
    if request.method == 'GET':
        case = {}
        if test_id:
            match = df[df['Test Case ID'].astype(str) == str(test_id)]
            if not match.empty:
                case = match.iloc[0].to_dict()
        return render_template('admin_edit.html', mode='edit', filename=filename, test_case=case)
    # POST update
    if not test_id:
        return redirect(url_for('admin_panel'))
    idx = df.index[df['Test Case ID'].astype(str) == str(test_id)]
    if len(idx) == 0:
        return redirect(url_for('admin_panel'))
    row = idx[0]
    df.at[row, 'Test Case Title'] = request.form.get('title', '').strip()
    df.at[row, 'Feature'] = request.form.get('feature', '').strip()
    df.at[row, 'Priority'] = request.form.get('priority', '').strip()
    df.at[row, 'Status'] = request.form.get('status', '').strip() or 'Pending'
    df.at[row, 'Preconditions'] = request.form.get('preconditions', '').strip()
    df.at[row, 'Given'] = request.form.get('given', '').strip()
    df.at[row, 'When'] = request.form.get('when', '').strip()
    df.at[row, 'Then'] = request.form.get('then', '').strip()
    df.at[row, 'Expected Behavior'] = request.form.get('expected', '').strip()
    df.at[row, 'Remarks'] = request.form.get('remarks', '').strip()
    df.to_excel(file_path, index=False)
    return redirect(url_for('admin_panel'))

@app.route('/reports')
def reports():
    """View test execution reports"""
    global current_role
    if not current_role:
        return redirect(url_for('index'))
    # Admin should not view tester reports
    if current_role == 'admin':
        return redirect(url_for('admin_panel'))
    
    # Read execution reports
    report_file = os.path.join(app.config['REPORTS_FOLDER'], 'test_execution_report.jsonl')
    reports = []
    
    if os.path.exists(report_file):
        with open(report_file, 'r') as f:
            for line in f:
                try:
                    reports.append(json.loads(line.strip()))
                except:
                    continue
    
    return render_template('reports.html', reports=reports, role=current_role)

@app.route('/logout')
def logout():
    """Logout and clear session"""
    global current_role
    current_role = None
    return redirect(url_for('index'))

# JFrog Configuration Routes
@app.route('/jfrog-config')
def jfrog_config():
    """JFrog configuration page"""
    if current_role != 'admin':
        return redirect(url_for('dashboard'))
    
    jfrog_config_data = config.get_jfrog_config()
    return render_template('jfrog_config.html', jfrog_config=jfrog_config_data)

@app.route('/save-jfrog-config', methods=['POST'])
def save_jfrog_config():
    """Save JFrog configuration"""
    if current_role != 'admin':
        return redirect(url_for('dashboard'))
    
    try:
        base_url = request.form.get('base_url', '').strip()
        repository = request.form.get('repository', '').strip()
        root_path = request.form.get('root_path', '').strip()
        access_token = request.form.get('access_token', '').strip()
        enabled = request.form.get('enabled') == 'on'
        
        config.update_jfrog_config(
            base_url=base_url,
            repository=repository,
            root_path=root_path,
            access_token=access_token,
            enabled=enabled
        )
        
        return redirect(url_for('jfrog_config'))
    except Exception as e:
        print(f"Error saving JFrog config: {e}")
        return redirect(url_for('jfrog_config'))

# API Routes for JFrog
@app.route('/api/check-cli-status')
def check_cli_status():
    """Check if JFrog CLI is available"""
    return jsonify({'available': jfrog_client.is_cli_available()})

@app.route('/api/test-jfrog-connection', methods=['POST'])
def test_jfrog_connection():
    """Test JFrog connection"""
    try:
        data = request.get_json()
        
        # Temporarily update config for testing
        original_config = config.get_jfrog_config()
        config.update_jfrog_config(
            base_url=data.get('base_url'),
            repository=data.get('repository'),
            root_path=data.get('root_path'),
            access_token=data.get('access_token')
        )
        
        # Test connection by trying to list files
        files = jfrog_client.list_excel_files()
        
        # Restore original config
        config.update_jfrog_config(**original_config)
        
        return jsonify({'success': True, 'files_found': len(files)})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/sync-jfrog-files', methods=['POST'])
def sync_jfrog_files():
    """Sync files from JFrog"""
    try:
        files = jfrog_client.sync_excel_files()
        
        # Reload Excel files after sync
        load_excel_files()
        
        return jsonify({'success': True, 'files': files})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    # Load Excel files on startup
    load_excel_files()
    print("Test Case Management System starting...")
    print("Open your browser and navigate to: http://localhost:8000")
    print("Press Ctrl+C to stop the application")
    app.run(debug=True, host='0.0.0.0', port=8000)
