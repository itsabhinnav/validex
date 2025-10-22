"""
High-Performance Database Configuration
Configuration settings for optimal performance with 1M+ test cases
"""

import os
from pathlib import Path

class HighPerformanceConfig:
    """Configuration for high-performance database operations"""
    
    # Database settings
    DATABASE_PATH = "data/db/test_cases_hp.db"
    MAX_CONNECTIONS = 20
    CONNECTION_TIMEOUT = 30.0
    
    # Performance settings
    BATCH_SIZE = 10000
    INDEX_BATCH_SIZE = 5000
    MAX_WORKERS = 4
    
    # Cache settings
    CACHE_SIZE = 10000
    MMAP_SIZE = 268435456  # 256MB
    
    # Search settings
    MAX_SEARCH_RESULTS = 10000
    DEFAULT_SEARCH_LIMIT = 1000
    MAX_EXPORT_LIMIT = 100000
    
    # Excel processing settings
    EXCEL_DIRECTORY = "data/excel_files/validex"
    MAX_EXCEL_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    EXCEL_CHUNK_SIZE = 1000
    
    # Indexing settings
    ENABLE_FULL_TEXT_SEARCH = True
    ENABLE_COMPOSITE_INDEXES = True
    ENABLE_SEARCH_CACHE = True
    
    # Optimization settings
    AUTO_VACUUM = True
    AUTO_ANALYZE = True
    WAL_MODE = True
    
    @classmethod
    def get_database_path(cls):
        """Get full database path"""
        return str(Path(__file__).parent.parent.parent / cls.DATABASE_PATH)
    
    @classmethod
    def get_excel_directory(cls):
        """Get Excel files directory"""
        return str(Path(__file__).parent.parent.parent / cls.EXCEL_DIRECTORY)
    
    @classmethod
    def get_performance_settings(cls):
        """Get database performance settings"""
        return {
            'journal_mode': 'WAL' if cls.WAL_MODE else 'DELETE',
            'synchronous': 'NORMAL',
            'cache_size': cls.CACHE_SIZE,
            'temp_store': 'MEMORY',
            'mmap_size': cls.MMAP_SIZE,
            'auto_vacuum': 'INCREMENTAL' if cls.AUTO_VACUUM else 'NONE'
        }
    
    @classmethod
    def get_index_definitions(cls):
        """Get index definitions for optimal performance"""
        return [
            # Primary indexes
            "CREATE INDEX IF NOT EXISTS idx_tc_id ON test_cases(tc_id)",
            "CREATE INDEX IF NOT EXISTS idx_tc_id_active ON test_cases(tc_id, is_active)",
            
            # Single column indexes
            "CREATE INDEX IF NOT EXISTS idx_feature ON test_cases(feature)",
            "CREATE INDEX IF NOT EXISTS idx_priority ON test_cases(priority)",
            "CREATE INDEX IF NOT EXISTS idx_status ON test_cases(status)",
            "CREATE INDEX IF NOT EXISTS idx_app_name ON test_cases(app_name)",
            "CREATE INDEX IF NOT EXISTS idx_test_type ON test_cases(test_type)",
            "CREATE INDEX IF NOT EXISTS idx_screen_id ON test_cases(screen_id)",
            
            # Composite indexes for common queries
            "CREATE INDEX IF NOT EXISTS idx_feature_priority ON test_cases(feature, priority)",
            "CREATE INDEX IF NOT EXISTS idx_app_status ON test_cases(app_name, status)",
            "CREATE INDEX IF NOT EXISTS idx_feature_status ON test_cases(feature, status)",
            "CREATE INDEX IF NOT EXISTS idx_priority_status ON test_cases(priority, status)",
            "CREATE INDEX IF NOT EXISTS idx_app_feature ON test_cases(app_name, feature)",
            
            # Full-text search indexes
            "CREATE INDEX IF NOT EXISTS idx_summary_ft ON test_cases(summary)",
            "CREATE INDEX IF NOT EXISTS idx_expected_behavior_ft ON test_cases(expected_behavior)",
            "CREATE INDEX IF NOT EXISTS idx_procedure_ft ON test_cases(procedure)",
            
            # File and metadata indexes
            "CREATE INDEX IF NOT EXISTS idx_file_path ON test_cases(file_path)",
            "CREATE INDEX IF NOT EXISTS idx_file_id ON test_cases(file_id)",
            "CREATE INDEX IF NOT EXISTS idx_created_at ON test_cases(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_updated_at ON test_cases(updated_at)",
            
            # Search index table indexes
            "CREATE INDEX IF NOT EXISTS idx_index_tc_id ON test_case_index(tc_id)",
            "CREATE INDEX IF NOT EXISTS idx_searchable_text ON test_case_index(searchable_text)",
            "CREATE INDEX IF NOT EXISTS idx_feature_norm ON test_case_index(feature_normalized)",
            "CREATE INDEX IF NOT EXISTS idx_priority_norm ON test_case_index(priority_normalized)",
            "CREATE INDEX IF NOT EXISTS idx_status_norm ON test_case_index(status_normalized)",
            "CREATE INDEX IF NOT EXISTS idx_app_norm ON test_case_index(app_normalized)",
            "CREATE INDEX IF NOT EXISTS idx_test_type_norm ON test_case_index(test_type_normalized)",
        ]
    
    @classmethod
    def get_table_schema(cls):
        """Get optimized table schema"""
        return {
            'test_cases': '''
                CREATE TABLE IF NOT EXISTS test_cases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tc_id TEXT NOT NULL UNIQUE,
                    summary TEXT,
                    feature TEXT,
                    priority TEXT,
                    status TEXT,
                    screen_id TEXT,
                    test_type TEXT,
                    expected_behavior TEXT,
                    procedure TEXT,
                    preconditions TEXT,
                    file_path TEXT,
                    directory_structure TEXT,
                    app_name TEXT,
                    test_category TEXT,
                    file_id TEXT,
                    local_version TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    -- Additional columns for comprehensive test case data
                    reference_document TEXT,
                    associated_requirements TEXT,
                    dr_applicable_screens TEXT,
                    test_objective TEXT,
                    test_suite_type TEXT,
                    requirement_type TEXT,
                    region TEXT,
                    brand TEXT,
                    test_data TEXT,
                    test_environment TEXT,
                    automation_status TEXT,
                    execution_time REAL,
                    last_executed TIMESTAMP,
                    execution_count INTEGER DEFAULT 0,
                    pass_rate REAL DEFAULT 0.0,
                    
                    -- Metadata for performance
                    file_hash TEXT,
                    row_number INTEGER,
                    is_active BOOLEAN DEFAULT 1
                )
            ''',
            'file_metadata': '''
                CREATE TABLE IF NOT EXISTS file_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_id TEXT UNIQUE NOT NULL,
                    file_path TEXT NOT NULL,
                    file_name TEXT NOT NULL,
                    file_hash TEXT,
                    file_size INTEGER,
                    last_modified TIMESTAMP,
                    last_synced TIMESTAMP,
                    sync_status TEXT DEFAULT 'pending',
                    record_count INTEGER DEFAULT 0,
                    processing_time REAL,
                    error_message TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''',
            'search_cache': '''
                CREATE TABLE IF NOT EXISTS search_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cache_key TEXT UNIQUE NOT NULL,
                    cache_data TEXT NOT NULL,
                    cache_type TEXT NOT NULL,
                    expires_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''',
            'test_case_index': '''
                CREATE TABLE IF NOT EXISTS test_case_index (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tc_id TEXT NOT NULL,
                    searchable_text TEXT,
                    feature_normalized TEXT,
                    priority_normalized TEXT,
                    status_normalized TEXT,
                    app_normalized TEXT,
                    test_type_normalized TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            '''
        }
    
    @classmethod
    def validate_config(cls):
        """Validate configuration settings"""
        errors = []
        
        # Check database path
        db_path = Path(cls.get_database_path())
        if not db_path.parent.exists():
            errors.append(f"Database directory does not exist: {db_path.parent}")
        
        # Check Excel directory
        excel_dir = Path(cls.get_excel_directory())
        if not excel_dir.exists():
            errors.append(f"Excel directory does not exist: {excel_dir}")
        
        # Validate numeric settings
        if cls.BATCH_SIZE <= 0:
            errors.append("BATCH_SIZE must be positive")
        
        if cls.MAX_CONNECTIONS <= 0:
            errors.append("MAX_CONNECTIONS must be positive")
        
        if cls.MAX_SEARCH_RESULTS <= 0:
            errors.append("MAX_SEARCH_RESULTS must be positive")
        
        return errors
    
    @classmethod
    def get_environment_overrides(cls):
        """Get configuration overrides from environment variables"""
        overrides = {}
        
        # Database settings
        if os.getenv('HP_DB_PATH'):
            overrides['DATABASE_PATH'] = os.getenv('HP_DB_PATH')
        
        if os.getenv('HP_BATCH_SIZE'):
            try:
                overrides['BATCH_SIZE'] = int(os.getenv('HP_BATCH_SIZE'))
            except ValueError:
                pass
        
        if os.getenv('HP_MAX_CONNECTIONS'):
            try:
                overrides['MAX_CONNECTIONS'] = int(os.getenv('HP_MAX_CONNECTIONS'))
            except ValueError:
                pass
        
        # Excel directory
        if os.getenv('HP_EXCEL_DIRECTORY'):
            overrides['EXCEL_DIRECTORY'] = os.getenv('HP_EXCEL_DIRECTORY')
        
        return overrides
    
    @classmethod
    def apply_environment_overrides(cls):
        """Apply environment variable overrides to configuration"""
        overrides = cls.get_environment_overrides()
        
        for key, value in overrides.items():
            setattr(cls, key, value)
        
        return len(overrides) > 0

# Apply environment overrides on import
HighPerformanceConfig.apply_environment_overrides()
