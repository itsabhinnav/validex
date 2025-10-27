import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent, HttpResponse } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { delay } from 'rxjs/operators';
import { MockDataService } from './mock-data.service';
import { FilterState, PaginationState } from '../models/high-performance-test-case.model';

@Injectable()
export class MockHttpInterceptor implements HttpInterceptor {
  constructor(private mockDataService: MockDataService) {}

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    // Check if mock mode is enabled
    const mockMode = localStorage.getItem('mockMode') === 'true' || 
                     sessionStorage.getItem('mockMode') === 'true';
    
    if (!mockMode) {
      return next.handle(req);
    }

    // Intercept API calls and return mock responses
    const url = req.url;
    const method = req.method;

    console.log(`[Mock Interceptor] Intercepting ${method} ${url}`);

    // Handle different API endpoints
    if (url.includes('/api/legacy/api/test-cases')) {
      if (method === 'GET') {
        return this.handleGetTestCases(req);
      } else if (method === 'POST' && url.includes('/export')) {
        return this.handleExportTestCases(req);
      } else if (method === 'POST' && url.includes('/statistics')) {
        return this.handleGetStatistics(req);
      } else if (method === 'POST' && url.includes('/bulk-operations')) {
        return this.handleBulkOperations(req);
      } else if (method === 'POST' && url.includes('/bulk-import')) {
        return this.handleBulkImport(req);
      } else if (method === 'POST' && url.includes('/optimize-database')) {
        return this.handleOptimizeDatabase(req);
      }
    }

    // If no mock handler found, pass through to real API
    return next.handle(req);
  }

  private handleGetTestCases(req: HttpRequest<any>): Observable<HttpEvent<any>> {
    const params = req.params;
    
    // Extract parameters
    const filterState: FilterState = {
      app_filter: params.getAll('app') || [],
      test_type_filter: params.getAll('test_type') || [],
      priority_filter: params.getAll('priority') || [],
      feature_filter: params.getAll('feature') || [],
      screen_id_filter: params.getAll('screen_id') || [],
      test_suite_type_filter: params.getAll('test_suite_type') || [],
      requirement_type_filter: params.getAll('requirement_type') || [],
      region_filter: params.getAll('region') || [],
      brand_filter: params.getAll('brand') || [],
      status_filter: params.getAll('status') || [],
      search_query: params.get('search') || '',
      sort_by: params.get('sort') || 'tc_id',
      sort_order: (params.get('order') as 'asc' | 'desc') || 'asc'
    };

    const paginationState: PaginationState = {
      current_page: parseInt(params.get('page') || '1'),
      per_page: parseInt(params.get('per_page') || '20'),
      total_cases: 0,
      total_pages: 0,
      has_prev: false,
      has_next: false
    };

    // Get mock response
    const response = this.mockDataService.filterAndPaginateTestCases(filterState, paginationState);
    
    return of(new HttpResponse({
      status: 200,
      body: response
    })).pipe(delay(200 + Math.random() * 300));
  }

  private handleExportTestCases(req: HttpRequest<any>): Observable<HttpEvent<any>> {
    const body = req.body;
    const format = body.format || 'csv';
    
    const filterState: FilterState = {
      app_filter: [],
      test_type_filter: [],
      priority_filter: [],
      feature_filter: [],
      screen_id_filter: [],
      test_suite_type_filter: [],
      requirement_type_filter: [],
      region_filter: [],
      brand_filter: [],
      status_filter: [],
      search_query: body.query || '',
      sort_by: 'tc_id',
      sort_order: 'asc'
    };

    // Generate mock CSV content
    const mockTestCases = this.mockDataService.getAllMockTestCases();
    const csvContent = this.generateCSVContent(mockTestCases);
    const blob = new Blob([csvContent], { type: 'text/csv' });

    return of(new HttpResponse({
      status: 200,
      body: {
        success: true,
        data: btoa(csvContent) // Base64 encode for Excel format
      }
    })).pipe(delay(1000));
  }

  private handleGetStatistics(req: HttpRequest<any>): Observable<HttpEvent<any>> {
    const stats = this.mockDataService.getDatabaseStatistics();
    
    return of(new HttpResponse({
      status: 200,
      body: {
        success: true,
        data: {
          total_test_cases: 150,
          total_files: 15,
          status_distribution: {
            'Passed': 45,
            'Failed': 12,
            'Blocked': 8,
            'Not Executed': 60,
            'In Progress': 15,
            'Pending Review': 10
          },
          priority_distribution: {
            'High': 30,
            'Medium': 80,
            'Low': 35,
            'Critical': 5
          },
          app_distribution: {
            'Mobile App': 50,
            'Web Portal': 40,
            'Admin Panel': 30,
            'API Service': 20,
            'Desktop App': 10
          },
          feature_distribution: {
            'Authentication': 25,
            'User Management': 20,
            'Payment Processing': 15,
            'Search': 18,
            'Notifications': 12,
            'Reports': 22,
            'Dashboard': 20,
            'Settings': 18
          }
        }
      }
    })).pipe(delay(200));
  }

  private handleBulkOperations(req: HttpRequest<any>): Observable<HttpEvent<any>> {
    const body = req.body;
    
    return of(new HttpResponse({
      status: 200,
      body: {
        success: true,
        data: {
          processed_count: body.test_case_ids?.length || 0,
          operation: body.operation,
          success: true,
          message: `Successfully processed ${body.test_case_ids?.length || 0} test cases`
        }
      }
    })).pipe(delay(800));
  }

  private handleBulkImport(req: HttpRequest<any>): Observable<HttpEvent<any>> {
    return of(new HttpResponse({
      status: 200,
      body: {
        success: true,
        data: {
          success: true,
          message: 'Mock import completed successfully',
          files_processed: 5,
          total_records: 150,
          processing_time: 2.5,
          files_per_second: 2.0,
          records_per_second: 60.0,
          errors: []
        }
      }
    })).pipe(delay(2000));
  }

  private handleOptimizeDatabase(req: HttpRequest<any>): Observable<HttpEvent<any>> {
    return of(new HttpResponse({
      status: 200,
      body: {
        success: true,
        data: {
          success: true,
          message: 'Mock database optimization completed successfully'
        }
      }
    })).pipe(delay(1500));
  }

  private generateCSVContent(testCases: any[]): string {
    if (testCases.length === 0) return '';
    
    const headers = [
      'TC ID', 'Summary', 'Feature', 'Priority', 'Status', 'Screen ID', 
      'Test Type', 'Expected Behavior', 'Procedure', 'Preconditions',
      'App Name', 'Test Category', 'Test Suite Type', 'Requirement Type',
      'Region', 'Brand', 'Test Data', 'Test Environment', 'Automation Status'
    ];
    
    const csvRows = [headers.join(',')];
    
    testCases.forEach(testCase => {
      const values = [
        testCase.tc_id || '',
        `"${testCase.summary || ''}"`,
        testCase.feature || '',
        testCase.priority || '',
        testCase.status || '',
        testCase.screen_id || '',
        testCase.test_type || '',
        `"${testCase.expected_behavior || ''}"`,
        `"${testCase.procedure || ''}"`,
        `"${testCase.preconditions || ''}"`,
        testCase.app_name || '',
        testCase.test_category || '',
        testCase.test_suite_type || '',
        testCase.requirement_type || '',
        testCase.region || '',
        testCase.brand || '',
        `"${testCase.test_data || ''}"`,
        testCase.test_environment || '',
        testCase.automation_status || ''
      ];
      csvRows.push(values.join(','));
    });
    
    return csvRows.join('\n');
  }
}
