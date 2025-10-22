"""
High-Performance Database Initialization Script
Initializes the high-performance database system for 1M+ test cases
"""

#!/usr/bin/env python3
"""
Database Initialization Script for High-Performance Test Case Management
Run this script to initialize the database for handling 1M+ test cases
"""

import os
import sys
import time
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.high_performance_db_service import HighPerformanceDatabaseService
from app.services.excel_processing_service import ExcelProcessingService
from app.services.database_migration_service import DatabaseMigrationService
from app.utils.path_resolver import path_resolver

def main():
    """Main initialization function"""
    print("=" * 80)
    print("HIGH-PERFORMANCE DATABASE INITIALIZATION")
    print("=" * 80)
    print("Initializing database for 1M+ test cases with advanced indexing...")
    print()
    
    start_time = time.time()
    
    try:
        # Step 1: Initialize database service
        print("Step 1: Initializing high-performance database service...")
        db_service = HighPerformanceDatabaseService()
        
        # Step 2: Run database migrations
        print("Step 2: Running database migrations...")
        migration_service = DatabaseMigrationService(db_service.db_path)
        migration_results = migration_service.run_all_migrations()
        
        if migration_results['success']:
            print(f"✓ Migrations completed successfully")
            print(f"  Applied: {len(migration_results['migrations_applied'])} migrations")
            if migration_results['migrations_failed']:
                print(f"  Failed: {len(migration_results['migrations_failed'])} migrations")
        else:
            print("✗ Some migrations failed")
            return False
        
        # Step 3: Initialize database with optimized schema
        print("Step 3: Initializing optimized database schema...")
        if db_service.initialize():
            print("✓ Database schema initialized successfully")
        else:
            print("✗ Database schema initialization failed")
            return False
        
        # Step 4: Discover Excel files
        print("Step 4: Discovering Excel files...")
        excel_service = ExcelProcessingService()
        excel_directory = str(project_root / 'data' / 'excel_files' / 'validex')
        
        excel_files = excel_service.discover_excel_files(excel_directory)
        print(f"✓ Found {len(excel_files)} Excel files")
        
        if excel_files:
            # Step 5: Analyze Excel files structure
            print("Step 5: Analyzing Excel files structure...")
            file_stats = excel_service.get_file_statistics(excel_directory)
            print(f"✓ Total file size: {file_stats['total_size'] / (1024*1024):.2f} MB")
            print(f"✓ File types: {file_stats['file_types']}")
            
            # Step 6: Bulk import Excel files
            print("Step 6: Bulk importing Excel files...")
            print("This may take several minutes for large datasets...")
            
            import_result = db_service.bulk_import_excel_files(excel_directory)
            
            if import_result['success']:
                print(f"✓ Bulk import completed successfully")
                print(f"  Files processed: {import_result['files_processed']}")
                print(f"  Total records: {import_result['total_records']:,}")
                print(f"  Processing time: {import_result['processing_time']:.2f} seconds")
                print(f"  Files/second: {import_result.get('files_per_second', 0):.2f}")
                print(f"  Records/second: {import_result.get('records_per_second', 0):.2f}")
                
                if import_result.get('errors'):
                    print(f"  Errors: {len(import_result['errors'])}")
                    for error in import_result['errors'][:5]:  # Show first 5 errors
                        print(f"    - {error}")
            else:
                print(f"✗ Bulk import failed: {import_result['message']}")
                return False
        
        # Step 7: Get final statistics
        print("Step 7: Generating database statistics...")
        stats = db_service.get_statistics()
        
        print(f"✓ Database statistics:")
        print(f"  Total test cases: {stats['total_test_cases']:,}")
        print(f"  Total files: {stats['total_files']}")
        print(f"  Status distribution: {stats['status_distribution']}")
        print(f"  Priority distribution: {stats['priority_distribution']}")
        
        # Step 8: Optimize database
        print("Step 8: Optimizing database...")
        db_service.optimize_database()
        print("✓ Database optimization completed")
        
        total_time = time.time() - start_time
        
        print()
        print("=" * 80)
        print("INITIALIZATION COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print(f"Total initialization time: {total_time:.2f} seconds")
        print(f"Database ready for high-performance operations")
        print(f"Database path: {db_service.db_path}")
        print()
        print("Next steps:")
        print("1. Start the Flask application: python run.py")
        print("2. Access the high-performance API endpoints:")
        print("   - POST /api/hp/test-cases/search")
        print("   - GET /api/hp/test-cases/filter-options")
        print("   - GET /api/hp/test-cases/statistics")
        print("3. Use the bulk import endpoint for additional files:")
        print("   - POST /api/hp/test-cases/bulk-import")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"✗ Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_performance():
    """Test database performance with sample queries"""
    print("\n" + "=" * 80)
    print("PERFORMANCE TESTING")
    print("=" * 80)
    
    try:
        db_service = HighPerformanceDatabaseService()
        
        # Test 1: Basic search
        print("Test 1: Basic search performance...")
        start_time = time.time()
        results = db_service.fast_search("", {}, limit=1000)
        search_time = time.time() - start_time
        
        print(f"✓ Search completed in {search_time:.4f} seconds")
        print(f"  Results: {len(results['results'])}")
        print(f"  Total available: {results['total_count']:,}")
        
        # Test 2: Filtered search
        print("Test 2: Filtered search performance...")
        start_time = time.time()
        results = db_service.fast_search("", {"status": "Pending"}, limit=1000)
        search_time = time.time() - start_time
        
        print(f"✓ Filtered search completed in {search_time:.4f} seconds")
        print(f"  Results: {len(results['results'])}")
        
        # Test 3: Get filter options
        print("Test 3: Filter options performance...")
        start_time = time.time()
        options = db_service.get_filter_options()
        options_time = time.time() - start_time
        
        print(f"✓ Filter options retrieved in {options_time:.4f} seconds")
        for field, values in options.items():
            print(f"  {field}: {len(values)} options")
        
        print("✓ Performance testing completed successfully")
        
    except Exception as e:
        print(f"✗ Performance testing failed: {e}")

if __name__ == '__main__':
    success = main()
    
    if success:
        # Run performance tests
        test_performance()
    
    sys.exit(0 if success else 1)
