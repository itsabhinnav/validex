export interface TestCase {
  'Test Case ID'?: string;
  'TC ID'?: string;
  'Test Objective'?: string;
  'Summary'?: string;
  'App'?: string;
  'Test Type'?: string;
  'Priority'?: string;
  'Feature'?: string;
  'Screen ID'?: string;
  'Preconditions'?: string;
  'Procedure'?: string;
  'Expected Behavior'?: string;
  'Requirement Type'?: string;
  'TestSuite Type'?: string;
  'Region'?: string;
  'Brand'?: string;
  'Vehicle Variant'?: string;
  'Vehicle Specification'?: string;
  'Env Dependancy'?: string;
  'Regulation'?: string;
  'Associated Requirements'?: string;
  'DR Applicable Screens'?: string;
  'DR ID'?: string;
  'Reference_Document'?: string;
  source_file?: string;
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
