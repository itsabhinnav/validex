// High-Performance Test Case Models
export interface TestCase {
  id?: number;
  tc_id: string;
  summary?: string;
  feature?: string;
  priority?: string;
  status?: string;
  screen_id?: string;
  test_type?: string;
  expected_behavior?: string;
  procedure?: string;
  preconditions?: string;
  file_path?: string;
  directory_structure?: string;
  app_name?: string;
  test_category?: string;
  file_id?: string;
  local_version?: string;
  created_at?: string;
  updated_at?: string;
  
  // Additional comprehensive fields
  reference_document?: string;
  associated_requirements?: string;
  dr_applicable_screens?: string;
  test_objective?: string;
  test_suite_type?: string;
  requirement_type?: string;
  region?: string;
  brand?: string;
  test_data?: string;
  test_environment?: string;
  automation_status?: string;
  execution_time?: number;
  last_executed?: string;
  execution_count?: number;
  pass_rate?: number;
  
  // Metadata
  file_hash?: string;
  row_number?: number;
  is_active?: boolean;
  file_name?: string;
  file_last_modified?: string;
}

export interface FilterOptions {
  apps: string[];
  test_types: string[];
  priorities: string[];
  features: string[];
  screen_ids: string[];
  test_suite_types: string[];
  requirement_types: string[];
  regions: string[];
  brands: string[];
  statuses: string[];
}

export interface FilterState {
  app_filter: string[];
  test_type_filter: string[];
  priority_filter: string[];
  feature_filter: string[];
  screen_id_filter: string[];
  test_suite_type_filter: string[];
  requirement_type_filter: string[];
  region_filter: string[];
  brand_filter: string[];
  status_filter: string[];
  search_query: string;
  sort_by: string;
  sort_order: 'asc' | 'desc';
}

export interface PaginationState {
  current_page: number;
  per_page: number;
  total_cases: number;
  total_pages: number;
  has_prev: boolean;
  has_next: boolean;
}

export interface SearchResponse {
  results: TestCase[];
  total_count: number;
  limit: number;
  offset: number;
  has_more: boolean;
  search_time: number;
  query: string;
  filters: any;
  timestamp?: number;
}

export interface DatabaseStats {
  total_test_cases: number;
  total_files: number;
  status_distribution: { [key: string]: number };
  priority_distribution: { [key: string]: number };
  app_distribution: { [key: string]: number };
  feature_distribution: { [key: string]: number };
}

export interface BulkImportResult {
  success: boolean;
  message: string;
  files_processed: number;
  total_records: number;
  processing_time: number;
  files_per_second: number;
  records_per_second: number;
  errors: string[];
}

export interface PerformanceMetrics {
  searchTime: number;
  filterTime: number;
  totalRecords: number;
  lastUpdated: Date;
}

export interface ExportResult {
  data: string; // Base64 encoded file or CSV string
  format: 'excel' | 'csv';
  record_count: number;
}

export interface ExcelAnalysisResult {
  file_analyses: ExcelFileAnalysis[];
  overall_statistics: FileStatistics;
  total_files_discovered: number;
}

export interface ExcelFileAnalysis {
  file_path: string;
  file_name: string;
  file_size: number;
  file_hash: string;
  total_rows: number;
  total_columns: number;
  columns: string[];
  data_types: { [key: string]: string };
  null_counts: { [key: string]: number };
  sample_data: any[];
  processing_time: number;
  last_modified: string;
  column_analysis: { [key: string]: ColumnAnalysis };
}

export interface ColumnAnalysis {
  total_values: number;
  non_null_values: number;
  null_count: number;
  unique_count: number;
  data_type: string;
  sample_values: any[];
  is_primary_key?: boolean;
  pattern?: any;
  allowed_values?: any[];
}

export interface FileStatistics {
  total_files: number;
  total_size: number;
  file_types: { [key: string]: number };
  directory_structure: any;
  largest_files: FileInfo[];
  oldest_files: FileInfo[];
  newest_files: FileInfo[];
}

export interface FileInfo {
  file: string;
  size?: number;
  modified?: string;
}

export interface FileValidationResult {
  is_valid: boolean;
  errors: string[];
  warnings: string[];
  recommendations: string[];
}

export interface BulkOperationResult {
  processed_count: number;
  operation: string;
  success: boolean;
  message: string;
}

// View modes for the UI
export type ViewMode = 'list' | 'detail' | 'more';

// Dynamic filter interface for advanced filtering
export interface DynamicFilter {
  columnName: string;
  displayName: string;
  values: string[];
  selectedValues: string[];
  dropdownOpen?: boolean;
  searchQuery?: string;
  filteredValues?: string[];
}

// Search and filter state management
export interface SearchState {
  query: string;
  filters: FilterState;
  pagination: PaginationState;
  sortBy: string;
  sortOrder: 'asc' | 'desc';
  isLoading: boolean;
  error: string | null;
}

// Bulk operations types
export type BulkOperationType = 'update_status' | 'update_priority' | 'update_feature' | 'delete' | 'export';

export interface BulkOperation {
  type: BulkOperationType;
  label: string;
  icon: string;
  description: string;
  requiresConfirmation: boolean;
  data?: any;
}

// Performance monitoring
export interface PerformanceStats {
  averageSearchTime: number;
  averageFilterTime: number;
  totalSearches: number;
  cacheHitRate: number;
  lastOptimization: Date;
  databaseSize: number;
}
