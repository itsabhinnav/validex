"""
Create sample requirements Excel file for Sakura
"""

import pandas as pd
import os
from pathlib import Path

def create_sample_requirements():
    """Create sample requirements Excel file with predefined columns"""
    
    requirements_data = {
        'Requirement ID': ['REQ-001', 'REQ-002', 'REQ-003', 'REQ-004', 'REQ-005', 'REQ-006'],
        'Screen ID': ['SCR-001', 'SCR-002', 'SCR-003', 'SCR-004', 'SCR-005', 'SCR-006'],
        'Description': [
            'User Authentication System',
            'Payment Gateway Integration', 
            'API Documentation Standards',
            'Database Schema Design',
            'Security Requirements',
            'User Interface Guidelines'
        ],
        'Given': [
            'User wants to access the system',
            'User needs to process payments',
            'Developers need API documentation',
            'System needs data storage',
            'System needs security measures',
            'Users need intuitive interface'
        ],
        'When': [
            'User enters credentials',
            'User initiates payment',
            'Developer accesses API',
            'Data is stored/retrieved',
            'System is accessed',
            'User interacts with system'
        ],
        'Then': [
            'System should authenticate user',
            'Payment should be processed securely',
            'Clear documentation should be provided',
            'Data should be stored efficiently',
            'System should be secure',
            'Interface should be user-friendly'
        ],
        'Priority': ['High', 'Medium', 'Low', 'High', 'High', 'Medium'],
        'Status': ['Active', 'Active', 'Completed', 'Active', 'Active', 'Pending'],
        'Category': ['Security', 'Integration', 'Documentation', 'Database', 'Security', 'UI/UX'],
        'Assignee': ['John Doe', 'Jane Smith', 'Mike Johnson', 'Sarah Wilson', 'David Brown', 'Lisa Davis'],
        'Created Date': ['2024-01-15', '2024-01-14', '2024-01-10', '2024-01-12', '2024-01-08', '2024-01-16'],
        'Due Date': ['2024-02-15', '2024-02-14', '2024-01-20', '2024-02-12', '2024-02-08', '2024-02-16'],
        'Tags': ['auth,security', 'payment,integration', 'docs,api', 'database,schema', 'security,access', 'ui,ux,design']
    }
    
    df = pd.DataFrame(requirements_data)
    
    output_dir = Path('data/excel_files/requirements')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / 'sample_requirements.xlsx'
    df.to_excel(output_file, index=False)
    
    print(f"Sample requirements Excel file created: {output_file}")
    print(f"Total requirements: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    
    return output_file

if __name__ == "__main__":
    create_sample_requirements()
