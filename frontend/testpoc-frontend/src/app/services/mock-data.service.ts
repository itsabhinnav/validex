import { Injectable } from '@angular/core';
import { Observable, of, delay } from 'rxjs';
import { TestCase, FilterOptions, FilterState, PaginationState, DatabaseStats, BulkImportResult } from '../models/high-performance-test-case.model';

@Injectable({
  providedIn: 'root'
})
export class MockDataService {
  private mockTestCases: TestCase[] = [];
  private mockFilterOptions: FilterOptions = {
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
  };

  constructor() {
    this.initializeMockData();
  }

  private initializeMockData(): void {
    // Generate comprehensive mock test cases
    this.mockTestCases = this.generateMockTestCases(150);
    this.mockFilterOptions = this.generateMockFilterOptions();
  }

  private generateMockTestCases(count: number): TestCase[] {
    const testCases: TestCase[] = [];
    const apps = ['Mobile App', 'Web Portal', 'Admin Panel', 'API Service', 'Desktop App'];
    const testTypes = ['Functional', 'Integration', 'Performance', 'Security', 'Usability', 'Regression'];
    const priorities = ['High', 'Medium', 'Low', 'Critical'];
    const features = ['Authentication', 'User Management', 'Payment Processing', 'Search', 'Notifications', 'Reports', 'Dashboard', 'Settings'];
    const screenIds = ['LOGIN', 'DASHBOARD', 'PROFILE', 'SETTINGS', 'REPORTS', 'SEARCH', 'PAYMENT', 'NOTIFICATIONS'];
    const testSuiteTypes = ['Smoke', 'Regression', 'Integration', 'Performance', 'Security'];
    const requirementTypes = ['Functional', 'Non-Functional', 'Performance', 'Security', 'Usability'];
    const regions = ['North America', 'Europe', 'Asia Pacific', 'Latin America', 'Middle East'];
    const brands = ['Brand A', 'Brand B', 'Brand C', 'Brand D', 'Brand E'];
    const statuses = ['Passed', 'Failed', 'Blocked', 'Not Executed', 'In Progress', 'Pending Review'];
    const automationStatuses = ['Automated', 'Manual', 'Semi-Automated', 'Not Applicable'];

    for (let i = 1; i <= count; i++) {
      const testCase: TestCase = {
        id: i,
        tc_id: `TC-${String(i).padStart(4, '0')}`,
        summary: `Test case ${i} - ${this.getRandomItem(features)} functionality`,
        test_objective: `Verify ${this.getRandomItem(features).toLowerCase()} functionality works correctly`,
        feature: this.getRandomItem(features),
        priority: this.getRandomItem(priorities),
        status: this.getRandomItem(statuses),
        screen_id: this.getRandomItem(screenIds),
        test_type: this.getRandomItem(testTypes),
        expected_behavior: `Expected behavior for test case ${i}`,
        procedure: `Step 1: Navigate to ${this.getRandomItem(screenIds)} screen\nStep 2: Perform action\nStep 3: Verify result`,
        preconditions: `User must be logged in and have appropriate permissions`,
        app_name: this.getRandomItem(apps),
        test_category: this.getRandomItem(testTypes),
        test_suite_type: this.getRandomItem(testSuiteTypes),
        requirement_type: this.getRandomItem(requirementTypes),
        region: this.getRandomItem(regions),
        brand: this.getRandomItem(brands),
        test_data: `Test data for scenario ${i}`,
        test_environment: 'Test Environment',
        automation_status: this.getRandomItem(automationStatuses),
        execution_time: Math.floor(Math.random() * 300) + 30, // 30-330 seconds
        last_executed: this.getRandomDate(),
        execution_count: Math.floor(Math.random() * 20) + 1,
        pass_rate: Math.floor(Math.random() * 100),
        file_path: `/test-cases/test-suite-${Math.floor(i / 10) + 1}.xlsx`,
        file_name: `test-suite-${Math.floor(i / 10) + 1}.xlsx`,
        file_hash: this.generateRandomHash(),
        row_number: i,
        is_active: true,
        created_at: this.getRandomDate(),
        updated_at: this.getRandomDate(),
        file_last_modified: this.getRandomDate(),
        reference_document: `REF-${i}`,
        associated_requirements: `REQ-${i}`,
        dr_applicable_screens: this.getRandomItem(screenIds),
        file_id: `file-${Math.floor(i / 10) + 1}`,
        local_version: '1.0',
        directory_structure: `/test-cases/suite-${Math.floor(i / 10) + 1}/`
      };
      testCases.push(testCase);
    }

    return testCases;
  }

  private generateMockFilterOptions(): FilterOptions {
    const testCases = this.mockTestCases;
    
    return {
      apps: [...new Set(testCases.map(tc => tc.app_name).filter(Boolean))].sort() as string[],
      test_types: [...new Set(testCases.map(tc => tc.test_type).filter(Boolean))].sort() as string[],
      priorities: [...new Set(testCases.map(tc => tc.priority).filter(Boolean))].sort() as string[],
      features: [...new Set(testCases.map(tc => tc.feature).filter(Boolean))].sort() as string[],
      screen_ids: [...new Set(testCases.map(tc => tc.screen_id).filter(Boolean))].sort() as string[],
      test_suite_types: [...new Set(testCases.map(tc => tc.test_suite_type).filter(Boolean))].sort() as string[],
      requirement_types: [...new Set(testCases.map(tc => tc.requirement_type).filter(Boolean))].sort() as string[],
      regions: [...new Set(testCases.map(tc => tc.region).filter(Boolean))].sort() as string[],
      brands: [...new Set(testCases.map(tc => tc.brand).filter(Boolean))].sort() as string[],
      statuses: [...new Set(testCases.map(tc => tc.status).filter(Boolean))].sort() as string[]
    };
  }

  private getRandomItem<T>(array: T[]): T {
    return array[Math.floor(Math.random() * array.length)];
  }

  private getRandomDate(): string {
    const start = new Date(2023, 0, 1);
    const end = new Date();
    const randomTime = start.getTime() + Math.random() * (end.getTime() - start.getTime());
    return new Date(randomTime).toISOString();
  }

  private generateRandomHash(): string {
    return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
  }

  // Mock API methods
  getTestCases(filterState: FilterState, paginationState: PaginationState): Observable<{
    test_cases: TestCase[];
    filter_options: FilterOptions;
    pagination: PaginationState;
  }> {
    // Simulate network delay
    return of(this.filterAndPaginateTestCases(filterState, paginationState)).pipe(
      delay(Math.random() * 500 + 200) // 200-700ms delay
    );
  }

  getFilterOptions(): Observable<FilterOptions> {
    return of(this.mockFilterOptions).pipe(
      delay(100)
    );
  }

  getTestCaseDetails(testCaseId: string): Observable<TestCase | null> {
    const testCase = this.mockTestCases.find(tc => tc.tc_id === testCaseId);
    return of(testCase || null).pipe(
      delay(150)
    );
  }

  exportTestCases(format: 'excel' | 'csv' | 'pdf', filterState: FilterState): Observable<Blob> {
    const filteredCases = this.applyFilters(this.mockTestCases, filterState);
    const csvContent = this.generateCSVContent(filteredCases);
    const blob = new Blob([csvContent], { type: 'text/csv' });
    
    return of(blob).pipe(
      delay(1000) // Simulate longer processing time for export
    );
  }

  getDatabaseStatistics(): Observable<DatabaseStats> {
    const stats: DatabaseStats = {
      total_test_cases: this.mockTestCases.length,
      total_files: Math.floor(this.mockTestCases.length / 10),
      status_distribution: this.getDistribution('status'),
      priority_distribution: this.getDistribution('priority'),
      app_distribution: this.getDistribution('app_name'),
      feature_distribution: this.getDistribution('feature')
    };

    return of(stats).pipe(
      delay(200)
    );
  }

  bulkOperations(operation: string, testCaseIds: string[], updateData: any = {}): Observable<any> {
    const result = {
      processed_count: testCaseIds.length,
      operation,
      success: true,
      message: `Successfully processed ${testCaseIds.length} test cases`
    };

    return of(result).pipe(
      delay(800)
    );
  }

  bulkImportExcelFiles(excelDirectory: string = 'data/excel_files/validex'): Observable<BulkImportResult> {
    const result: BulkImportResult = {
      success: true,
      message: 'Mock import completed successfully',
      files_processed: 5,
      total_records: 150,
      processing_time: 2.5,
      files_per_second: 2.0,
      records_per_second: 60.0,
      errors: []
    };

    return of(result).pipe(
      delay(2000)
    );
  }

  optimizeDatabase(): Observable<{ success: boolean; message: string }> {
    return of({
      success: true,
      message: 'Mock database optimization completed successfully'
    }).pipe(
      delay(1500)
    );
  }

  // Helper methods
  filterAndPaginateTestCases(filterState: FilterState, paginationState: PaginationState): {
    test_cases: TestCase[];
    filter_options: FilterOptions;
    pagination: PaginationState;
  } {
    let filteredCases = this.applyFilters(this.mockTestCases, filterState);
    
    // Apply sorting
    filteredCases = this.applySorting(filteredCases, filterState.sort_by, filterState.sort_order);
    
    // Apply pagination
    const totalCases = filteredCases.length;
    const totalPages = Math.ceil(totalCases / paginationState.per_page);
    const startIndex = (paginationState.current_page - 1) * paginationState.per_page;
    const endIndex = startIndex + paginationState.per_page;
    const paginatedCases = filteredCases.slice(startIndex, endIndex);

    return {
      test_cases: paginatedCases,
      filter_options: this.mockFilterOptions,
      pagination: {
        current_page: paginationState.current_page,
        per_page: paginationState.per_page,
        total_cases: totalCases,
        total_pages: totalPages,
        has_prev: paginationState.current_page > 1,
        has_next: paginationState.current_page < totalPages
      }
    };
  }

  private applyFilters(testCases: TestCase[], filterState: FilterState): TestCase[] {
    return testCases.filter(testCase => {
      // Search query filter
      if (filterState.search_query) {
        const searchLower = filterState.search_query.toLowerCase();
        const searchableFields = [
          testCase.tc_id,
          testCase.summary,
          testCase.test_objective,
          testCase.feature,
          testCase.screen_id,
          testCase.app_name
        ].filter(Boolean).join(' ').toLowerCase();
        
        if (!searchableFields.includes(searchLower)) {
          return false;
        }
      }

      // Filter by various criteria
      if (filterState.app_filter?.length > 0 && !filterState.app_filter.includes(testCase.app_name || '')) {
        return false;
      }
      if (filterState.test_type_filter?.length > 0 && !filterState.test_type_filter.includes(testCase.test_type || '')) {
        return false;
      }
      if (filterState.priority_filter?.length > 0 && !filterState.priority_filter.includes(testCase.priority || '')) {
        return false;
      }
      if (filterState.feature_filter?.length > 0 && !filterState.feature_filter.includes(testCase.feature || '')) {
        return false;
      }
      if (filterState.screen_id_filter?.length > 0 && !filterState.screen_id_filter.includes(testCase.screen_id || '')) {
        return false;
      }
      if (filterState.test_suite_type_filter?.length > 0 && !filterState.test_suite_type_filter.includes(testCase.test_suite_type || '')) {
        return false;
      }
      if (filterState.requirement_type_filter?.length > 0 && !filterState.requirement_type_filter.includes(testCase.requirement_type || '')) {
        return false;
      }
      if (filterState.region_filter?.length > 0 && !filterState.region_filter.includes(testCase.region || '')) {
        return false;
      }
      if (filterState.brand_filter?.length > 0 && !filterState.brand_filter.includes(testCase.brand || '')) {
        return false;
      }
      if (filterState.status_filter?.length > 0 && !filterState.status_filter.includes(testCase.status || '')) {
        return false;
      }

      return true;
    });
  }

  private applySorting(testCases: TestCase[], sortBy: string, sortOrder: 'asc' | 'desc'): TestCase[] {
    return [...testCases].sort((a, b) => {
      const aValue = (a as any)[sortBy] || '';
      const bValue = (b as any)[sortBy] || '';
      
      let comparison = 0;
      if (aValue < bValue) {
        comparison = -1;
      } else if (aValue > bValue) {
        comparison = 1;
      }
      
      return sortOrder === 'asc' ? comparison : -comparison;
    });
  }

  private getDistribution(field: keyof TestCase): { [key: string]: number } {
    const distribution: { [key: string]: number } = {};
    this.mockTestCases.forEach(testCase => {
      const value = testCase[field] as string;
      if (value) {
        distribution[value] = (distribution[value] || 0) + 1;
      }
    });
    return distribution;
  }

  private generateCSVContent(testCases: TestCase[]): string {
    if (testCases.length === 0) return '';
    
    const headers = Object.keys(testCases[0]);
    const csvRows = [headers.join(',')];
    
    testCases.forEach(testCase => {
      const values = headers.map(header => {
        const value = (testCase as any)[header];
        return typeof value === 'string' && value.includes(',') ? `"${value}"` : value;
      });
      csvRows.push(values.join(','));
    });
    
    return csvRows.join('\n');
  }

  // Method to refresh mock data (useful for testing)
  refreshMockData(): void {
    this.initializeMockData();
  }

  // Method to get all mock test cases (useful for debugging)
  getAllMockTestCases(): TestCase[] {
    return [...this.mockTestCases];
  }
}
