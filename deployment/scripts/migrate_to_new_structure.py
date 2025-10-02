"""
Migration script to move existing files to new project structure
"""

import os
import shutil
from pathlib import Path

def migrate_project():
    """Migrate existing project to new structure"""
    print("Starting project migration...")
    
    # Create new directories
    new_dirs = [
        'app/models',
        'app/services', 
        'app/api',
        'app/utils',
        'core/database',
        'core/sync',
        'core/storage',
        'tests',
        'scripts',
        'docs',
        'data/excel_files',
        'data/reports',
        'data/cache'
    ]
    
    for dir_path in new_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {dir_path}")
    
    # Move existing files
    file_moves = [
        ('app.py', 'app/api/routes.py'),
        ('database_manager.py', 'core/database/manager.py'),
        ('remote_sync_manager.py', 'core/sync/remote_sync.py'),
        ('column_manager.py', 'app/services/column_service.py'),
        ('config.py', 'config/settings.py'),
        ('validex_config.json', 'config/database.py'),
        ('column_config.json', 'config/column_config.json'),
        ('requirements.txt', 'requirements.txt'),
        ('README.md', 'README.md')
    ]
    
    for src, dst in file_moves:
        if os.path.exists(src):
            # Create destination directory if needed
            Path(dst).parent.mkdir(parents=True, exist_ok=True)
            
            # Skip if source and destination are the same
            if src != dst:
                # Copy file
                shutil.copy2(src, dst)
                print(f"Moved {src} -> {dst}")
            else:
                print(f"Skipped {src} (same file)")
        else:
            print(f"Source file not found: {src}")
    
    # Move templates
    if os.path.exists('templates'):
        # Create app/templates directory
        Path('app/templates').mkdir(parents=True, exist_ok=True)
        
        for template_file in os.listdir('templates'):
            src = f'templates/{template_file}'
            dst = f'app/templates/{template_file}'
            shutil.copy2(src, dst)
            print(f"Moved template: {template_file}")
    
    # Move static files
    if os.path.exists('static'):
        # Create app/static directory
        Path('app/static').mkdir(parents=True, exist_ok=True)
        
        for static_file in os.listdir('static'):
            src = f'static/{static_file}'
            dst = f'app/static/{static_file}'
            shutil.copy2(src, dst)
            print(f"Moved static: {static_file}")
    
    # Move Excel files
    if os.path.exists('excel_files'):
        for excel_file in os.listdir('excel_files'):
            src = f'excel_files/{excel_file}'
            dst = f'data/excel_files/{excel_file}'
            if os.path.isfile(src):
                shutil.copy2(src, dst)
                print(f"Moved Excel file: {excel_file}")
            elif os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
                print(f"Moved Excel directory: {excel_file}")
    
    # Create __init__.py files
    init_files = [
        'app/__init__.py',
        'app/models/__init__.py',
        'app/services/__init__.py',
        'app/api/__init__.py',
        'app/utils/__init__.py',
        'core/__init__.py',
        'core/database/__init__.py',
        'core/sync/__init__.py',
        'core/storage/__init__.py',
        'tests/__init__.py',
        'scripts/__init__.py',
        'config/__init__.py'
    ]
    
    for init_file in init_files:
        Path(init_file).touch()
        print(f"Created: {init_file}")
    
    print("\nMigration completed successfully!")
    print("\nNew project structure:")
    print("app/")
    print("  models/")
    print("  services/")
    print("  api/")
    print("  utils/")
    print("  templates/")
    print("core/")
    print("  database/")
    print("  sync/")
    print("  storage/")
    print("config/")
    print("tests/")
    print("scripts/")
    print("docs/")
    print("data/")
    print("  excel_files/")
    print("  reports/")
    print("  cache/")
    print("run.py")
    
    print("\nTo run the application:")
    print("python run.py")

if __name__ == '__main__':
    migrate_project()
