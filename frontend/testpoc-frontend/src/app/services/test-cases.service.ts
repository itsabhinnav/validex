import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { TestCase, FilterOptions, FilterState, PaginationState } from '../models/test-case.model';

@Injectable({
  providedIn: 'root'
})
export class TestCasesService {
  private apiUrl = 'http://localhost:8000/api';

  constructor(private http: HttpClient) { }

  // Get test cases with filtering and pagination
  getTestCases(filterState: FilterState, paginationState: PaginationState): Observable<{
    test_cases: TestCase[];
    filter_options: FilterOptions;
    pagination: PaginationState;
  }> {
    let params = new HttpParams();
    
    // Add filter parameters
    if (filterState.app_filter && filterState.app_filter.length > 0) {
      filterState.app_filter.forEach(app => {
        params = params.append('app', app);
      });
    }
    if (filterState.test_type_filter && filterState.test_type_filter.length > 0) {
      filterState.test_type_filter.forEach(type => {
        params = params.append('test_type', type);
      });
    }
    if (filterState.priority_filter && filterState.priority_filter.length > 0) {
      filterState.priority_filter.forEach(priority => {
        params = params.append('priority', priority);
      });
    }
    if (filterState.feature_filter && filterState.feature_filter.length > 0) {
      filterState.feature_filter.forEach(feature => {
        params = params.append('feature', feature);
      });
    }
    if (filterState.screen_id_filter && filterState.screen_id_filter.length > 0) {
      filterState.screen_id_filter.forEach(screenId => {
        params = params.append('screen_id', screenId);
      });
    }
    if (filterState.test_suite_type_filter.length > 0) {
      filterState.test_suite_type_filter.forEach(type => {
        params = params.append('test_suite_type', type);
      });
    }
    if (filterState.requirement_type_filter.length > 0) {
      filterState.requirement_type_filter.forEach(type => {
        params = params.append('requirement_type', type);
      });
    }
    if (filterState.search_query) {
      params = params.set('search', filterState.search_query);
    }
    if (filterState.sort_by) {
      params = params.set('sort', filterState.sort_by);
    }
    if (filterState.sort_order) {
      params = params.set('order', filterState.sort_order);
    }
    
    // Add pagination parameters
    params = params.set('page', paginationState.current_page.toString());
    params = params.set('per_page', paginationState.per_page.toString());

    return this.http.get<{
      test_cases: TestCase[];
      filter_options: FilterOptions;
      pagination: PaginationState;
    }>(`${this.apiUrl}/test-cases`, { params });
  }

  // Get filter options
  getFilterOptions(): Observable<FilterOptions> {
    return this.http.get<FilterOptions>(`${this.apiUrl}/filter-options`);
  }

  // Get test case details
  getTestCaseDetails(testCaseId: string): Observable<TestCase> {
    return this.http.get<TestCase>(`${this.apiUrl}/test-case-details`, {
      params: { test_case_id: testCaseId }
    });
  }

  // Export test cases
  exportTestCases(format: 'excel' | 'csv' | 'pdf', filterState: FilterState): Observable<Blob> {
    let params = new HttpParams();
    
    // Add filter parameters (same as getTestCases)
    if (filterState.app_filter && filterState.app_filter.length > 0) {
      filterState.app_filter.forEach(app => {
        params = params.append('app', app);
      });
    }
    if (filterState.test_type_filter && filterState.test_type_filter.length > 0) {
      filterState.test_type_filter.forEach(type => {
        params = params.append('test_type', type);
      });
    }
    if (filterState.priority_filter && filterState.priority_filter.length > 0) {
      filterState.priority_filter.forEach(priority => {
        params = params.append('priority', priority);
      });
    }
    if (filterState.feature_filter && filterState.feature_filter.length > 0) {
      filterState.feature_filter.forEach(feature => {
        params = params.append('feature', feature);
      });
    }
    if (filterState.screen_id_filter && filterState.screen_id_filter.length > 0) {
      filterState.screen_id_filter.forEach(screenId => {
        params = params.append('screen_id', screenId);
      });
    }
    
    params = params.set('format', format);

    return this.http.get(`${this.apiUrl}/export-test-cases`, {
      params,
      responseType: 'blob'
    });
  }
}