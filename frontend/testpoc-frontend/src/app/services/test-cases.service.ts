import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { TestCase, FilterOptions, FilterState, PaginationState, SearchResponse, DatabaseStats, BulkImportResult } from '../models/high-performance-test-case.model';

@Injectable({
  providedIn: 'root'
})
export class TestCasesService {
  private apiUrl = 'http://localhost:8000/api/legacy/api';

  constructor(private http: HttpClient) { }

  // Get test cases with filtering and pagination - using working endpoints
  getTestCases(filterState: FilterState, paginationState: PaginationState): Observable<{
    test_cases: TestCase[];
    filter_options: FilterOptions;
    pagination: PaginationState;
  }> {
    const params = new HttpParams()
      .set('page', paginationState.current_page.toString())
      .set('per_page', paginationState.per_page.toString())
      .set('search', filterState.search_query || '')
      .set('sort', filterState.sort_by || 'tc_id')
      .set('order', filterState.sort_order || 'asc');

    // Add filter parameters
    if (filterState.app_filter && filterState.app_filter.length > 0) {
      filterState.app_filter.forEach(app => params.append('app', app));
    }
    if (filterState.test_type_filter && filterState.test_type_filter.length > 0) {
      filterState.test_type_filter.forEach(type => params.append('test_type', type));
    }
    if (filterState.priority_filter && filterState.priority_filter.length > 0) {
      filterState.priority_filter.forEach(priority => params.append('priority', priority));
    }
    if (filterState.feature_filter && filterState.feature_filter.length > 0) {
      filterState.feature_filter.forEach(feature => params.append('feature', feature));
    }
    if (filterState.screen_id_filter && filterState.screen_id_filter.length > 0) {
      filterState.screen_id_filter.forEach(screenId => params.append('screen_id', screenId));
    }
    if (filterState.test_suite_type_filter && filterState.test_suite_type_filter.length > 0) {
      filterState.test_suite_type_filter.forEach(type => params.append('test_suite_type', type));
    }
    if (filterState.requirement_type_filter && filterState.requirement_type_filter.length > 0) {
      filterState.requirement_type_filter.forEach(type => params.append('requirement_type', type));
    }
    if (filterState.region_filter && filterState.region_filter.length > 0) {
      filterState.region_filter.forEach(region => params.append('region', region));
    }
    if (filterState.brand_filter && filterState.brand_filter.length > 0) {
      filterState.brand_filter.forEach(brand => params.append('brand', brand));
    }
    if (filterState.status_filter && filterState.status_filter.length > 0) {
      filterState.status_filter.forEach(status => params.append('status', status));
    }

    return this.http.get<any>(`${this.apiUrl}/test-cases`, { params })
      .pipe(
        map(response => ({
          test_cases: (response.test_cases || []).map((tc: any) => this.transformTestCase(tc)),
          filter_options: response.filter_options || {
            apps: [],
            test_types: [],
            priorities: [],
            features: [],
            screen_ids: [],
            test_suite_types: [],
            requirement_types: [],
            regions: [],
            brands: [],
            statuses: []
          },
          pagination: response.pagination || {
            current_page: paginationState.current_page,
            per_page: paginationState.per_page,
            total_cases: 0,
            total_pages: 0,
            has_prev: false,
            has_next: false
          }
        }))
      );
  }

  // Get filter options - using working endpoint
  getFilterOptions(): Observable<FilterOptions> {
    return this.http.get<any>(`${this.apiUrl}/test-cases`)
      .pipe(
        map(response => response.filter_options || {
          apps: [],
          test_types: [],
          priorities: [],
          features: [],
          screen_ids: [],
          test_suite_types: [],
          requirement_types: [],
          regions: [],
          brands: [],
          statuses: []
        })
      );
  }

  // Get test case details - using search approach
  getTestCaseDetails(testCaseId: string): Observable<TestCase | null> {
    const params = new HttpParams()
      .set('search', testCaseId)
      .set('per_page', '1');

    return this.http.get<any>(`${this.apiUrl}/test-cases`, { params })
      .pipe(
        map(response => {
          const testCases = response.test_cases || [];
          return testCases.length > 0 ? this.transformTestCase(testCases[0]) : null;
        })
      );
  }

  // Export test cases - now using high-performance endpoint
  exportTestCases(format: 'excel' | 'csv' | 'pdf', filterState: FilterState): Observable<Blob> {
    const exportRequest = {
      query: filterState.search_query || '',
      filters: this.sanitizeFilters(filterState),
      format: format === 'pdf' ? 'excel' : format, // Convert PDF to Excel for now
      limit: 50000
    };

    return this.http.post<{
      success: boolean;
      data: string; // Base64 encoded file
    }>(`${this.apiUrl}/test-cases/export`, exportRequest)
      .pipe(
        map(response => {
          const blob = format === 'excel' 
            ? this.base64ToBlob(response.data, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            : new Blob([response.data], { type: 'text/csv' });
          return blob;
        })
      );
  }

  // Get database statistics - now using high-performance endpoint
  getDatabaseStatistics(): Observable<DatabaseStats> {
    return this.http.get<{
      success: boolean;
      data: DatabaseStats;
    }>(`${this.apiUrl}/test-cases/statistics`)
      .pipe(
        map(response => response.data)
      );
  }

  // Bulk operations - now using high-performance endpoint
  bulkOperations(
    operation: string,
    testCaseIds: string[],
    updateData: any = {}
  ): Observable<any> {
    return this.http.post<{
      success: boolean;
      data: any;
    }>(`${this.apiUrl}/test-cases/bulk-operations`, {
      operation,
      test_case_ids: testCaseIds,
      update_data: updateData
    })
      .pipe(
        map(response => response.data)
      );
  }

  // Bulk import Excel files - now using high-performance endpoint
  bulkImportExcelFiles(excelDirectory: string = 'data/excel_files/validex'): Observable<BulkImportResult> {
    return this.http.post<{
      success: boolean;
      data: BulkImportResult;
    }>(`${this.apiUrl}/test-cases/bulk-import`, {
      excel_directory: excelDirectory
    })
      .pipe(
        map(response => response.data)
      );
  }

  // Optimize database - now using high-performance endpoint
  optimizeDatabase(): Observable<{ success: boolean; message: string }> {
    return this.http.post<{
      success: boolean;
      data: { success: boolean; message: string };
    }>(`${this.apiUrl}/test-cases/optimize-database`, {})
      .pipe(
        map(response => response.data)
      );
  }

  // Private helper methods
  private transformTestCase(backendTestCase: any): TestCase {
    return {
      id: backendTestCase.id,
      tc_id: backendTestCase['TC ID'] || backendTestCase['Test Case ID'] || '',
      summary: backendTestCase['Test Objective'] || '',
      feature: backendTestCase['Feature'] || '',
      priority: backendTestCase['Priority'] || '',
      status: backendTestCase['Status'] || '',
      screen_id: backendTestCase['Screen ID'] || '',
      test_type: backendTestCase['Test Type'] || '',
      expected_behavior: backendTestCase['Expected Behavior'] || '',
      procedure: backendTestCase['Procedure'] || '',
      preconditions: backendTestCase['Preconditions'] || '',
      file_path: backendTestCase['file_path'] || '',
      directory_structure: backendTestCase['directory_structure'] || '',
      app_name: backendTestCase['App Name'] || '',
      test_category: backendTestCase['Test Category'] || '',
      file_id: backendTestCase['file_id'] || '',
      local_version: backendTestCase['local_version'] || '',
      created_at: backendTestCase['created_at'] || '',
      updated_at: backendTestCase['updated_at'] || '',
      
      // Additional comprehensive fields
      reference_document: backendTestCase['Reference_Document'] || '',
      associated_requirements: backendTestCase['Associated Requirements'] || '',
      dr_applicable_screens: backendTestCase['DR Applicable Screens'] || '',
      test_objective: backendTestCase['Test Objective'] || '',
      test_suite_type: backendTestCase['TestSuite Type'] || '',
      requirement_type: backendTestCase['Requirement Type'] || '',
      region: backendTestCase['Region'] || '',
      brand: backendTestCase['Brand'] || '',
      test_data: backendTestCase['Test Data'] || '',
      test_environment: backendTestCase['Test Environment'] || '',
      automation_status: backendTestCase['Automation Status'] || '',
      execution_time: backendTestCase['execution_time'] || 0,
      last_executed: backendTestCase['last_executed'] || '',
      execution_count: backendTestCase['execution_count'] || 0,
      pass_rate: backendTestCase['pass_rate'] || 0,
      
      // Metadata
      file_hash: backendTestCase['file_hash'] || '',
      row_number: backendTestCase['row_number'] || 0,
      is_active: backendTestCase['is_active'] || true,
      file_name: backendTestCase['source_file'] || '',
      file_last_modified: backendTestCase['file_last_modified'] || ''
    };
  }

  private sanitizeFilters(filters: FilterState): any {
    const sanitized: any = {};
    
    // Map frontend filter names to backend field names
    const fieldMapping: { [key: string]: string } = {
      'app_filter': 'app_name',
      'test_type_filter': 'test_type',
      'priority_filter': 'priority',
      'feature_filter': 'feature',
      'screen_id_filter': 'screen_id',
      'test_suite_type_filter': 'test_suite_type',
      'requirement_type_filter': 'requirement_type',
      'region_filter': 'region',
      'brand_filter': 'brand',
      'status_filter': 'status'
    };

    Object.keys(fieldMapping).forEach(frontendKey => {
      const backendKey = fieldMapping[frontendKey];
      const value = (filters as any)[frontendKey];
      
      if (value && Array.isArray(value) && value.length > 0) {
        sanitized[backendKey] = value[0]; // Backend expects single value for now
      }
    });

    return sanitized;
  }

  private base64ToBlob(base64: string, mimeType: string): Blob {
    const byteCharacters = atob(base64);
    const byteNumbers = new Array(byteCharacters.length);
    
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    
    const byteArray = new Uint8Array(byteNumbers);
    return new Blob([byteArray], { type: mimeType });
  }
}
