import { Component, OnInit } from '@angular/core';
import { TestCasesService } from '../../services/test-cases.service';
import { TestCase, FilterOptions, FilterState, PaginationState } from '../../models/test-case.model';

export type ViewMode = 'list' | 'detail' | 'more';

@Component({
  selector: 'app-test-cases',
  templateUrl: './test-cases.component.html',
  styleUrls: ['./test-cases.component.css']
})
export class TestCasesComponent implements OnInit {
  testCases: TestCase[] = [];
  selectedTestCase: TestCase | null = null;
  selectedTestCaseIndex: number = -1;
  currentView: ViewMode = 'detail'; // Default to detail view
  
  filterOptions: FilterOptions = {
    apps: [],
    test_types: [],
    priorities: [],
    features: [],
    screen_ids: [],
    test_suite_types: [],
    requirement_types: [],
    regions: [],
    brands: []
  };
  
  filterState: FilterState = {
    app_filter: [],
    test_type_filter: [],
    priority_filter: [],
    feature_filter: [],
    screen_id_filter: [],
    test_suite_type_filter: [],
    requirement_type_filter: [],
    region_filter: [],
    brand_filter: [],
    search_query: '',
    sort_by: 'Test Case ID',
    sort_order: 'asc'
  };

  // Search queries for each filter dropdown
  appSearchQuery: string = '';
  testTypeSearchQuery: string = '';
  prioritySearchQuery: string = '';
  featureSearchQuery: string = '';
  screenIdSearchQuery: string = '';
  testSuiteTypeSearchQuery: string = '';
  requirementTypeSearchQuery: string = '';

  // Filtered options for each dropdown
  filteredAppOptions: string[] = [];
  filteredTestTypeOptions: string[] = [];
  filteredPriorityOptions: string[] = [];
  filteredFeatureOptions: string[] = [];
  filteredScreenIdOptions: string[] = [];
  filteredTestSuiteTypeOptions: string[] = [];
  filteredRequirementTypeOptions: string[] = [];

  // Dropdown state
  appDropdownOpen: boolean = false;
  testTypeDropdownOpen: boolean = false;
  priorityDropdownOpen: boolean = false;
  featureDropdownOpen: boolean = false;
  moreFiltersDropdownOpen: boolean = false;
  
  paginationState: PaginationState = {
    current_page: 1,
    per_page: 50,
    total_cases: 0,
    total_pages: 0,
    has_prev: false,
    has_next: false
  };

  loading = false;
  error: string | null = null;
  private searchTimeout: any;

  constructor(private testCasesService: TestCasesService) { }

  ngOnInit(): void {
    this.loadFilterOptions();
    this.loadTestCases();
    this.initializeFilteredOptions();
  }

  initializeFilteredOptions(): void {
    this.filteredAppOptions = [...this.filterOptions.apps];
    this.filteredTestTypeOptions = [...this.filterOptions.test_types];
    this.filteredPriorityOptions = [...this.filterOptions.priorities];
    this.filteredFeatureOptions = [...this.filterOptions.features];
    this.filteredScreenIdOptions = [...this.filterOptions.screen_ids];
    this.filteredTestSuiteTypeOptions = [...this.filterOptions.test_suite_types];
    this.filteredRequirementTypeOptions = [...this.filterOptions.requirement_types];
  }

  loadFilterOptions(): void {
    this.testCasesService.getFilterOptions().subscribe({
      next: (options) => {
        this.filterOptions = options;
        this.initializeFilteredOptions();
      },
      error: (error) => {
        console.error('Error loading filter options:', error);
        this.error = 'Failed to load filter options';
      }
    });
  }

  loadTestCases(): void {
    this.loading = true;
    this.error = null;
    
    this.testCasesService.getTestCases(this.filterState, this.paginationState).subscribe({
      next: (response) => {
        this.testCases = response.test_cases;
        this.filterOptions = response.filter_options;
        this.paginationState = response.pagination;
        this.loading = false;
        
        // Auto-select first test case if available and in detail view
        if (this.currentView === 'detail' && this.testCases.length > 0 && this.selectedTestCaseIndex === -1) {
          this.selectTestCase(0);
        }
      },
      error: (error) => {
        console.error('Error loading test cases:', error);
        this.error = 'Failed to load test cases';
        this.loading = false;
      }
    });
  }

  onFilterChange(): void {
    this.paginationState.current_page = 1; // Reset to first page
    this.loadTestCases();
  }

  onSearchChange(searchQuery: string): void {
    this.filterState.search_query = searchQuery;
    // Debounce search to avoid too many requests
    clearTimeout(this.searchTimeout);
    this.searchTimeout = setTimeout(() => {
      this.onFilterChange();
    }, 500);
  }

  onSortChange(sortBy: string, sortOrder: 'asc' | 'desc'): void {
    this.filterState.sort_by = sortBy;
    this.filterState.sort_order = sortOrder;
    this.loadTestCases();
  }

  onPageChange(page: number): void {
    this.paginationState.current_page = page;
    this.loadTestCases();
  }

  onPerPageChange(perPage: number): void {
    this.paginationState.per_page = perPage;
    this.paginationState.current_page = 1;
    this.loadTestCases();
  }

  clearFilters(): void {
    this.filterState = {
      app_filter: [],
      test_type_filter: [],
      priority_filter: [],
      feature_filter: [],
      screen_id_filter: [],
      test_suite_type_filter: [],
      requirement_type_filter: [],
      region_filter: [],
      brand_filter: [],
      search_query: '',
      sort_by: 'Test Case ID',
      sort_order: 'asc'
    };
    this.onFilterChange();
  }

  exportTestCases(format: 'excel' | 'csv' | 'pdf'): void {
    this.testCasesService.exportTestCases(format, this.filterState).subscribe({
      next: (blob) => {
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `test_cases.${format}`;
        link.click();
        window.URL.revokeObjectURL(url);
      },
      error: (error) => {
        console.error('Error exporting test cases:', error);
        this.error = 'Failed to export test cases';
      }
    });
  }

  viewTestCaseDetails(testCase: TestCase): void {
    const testCaseId = testCase['Test Case ID'] || testCase['TC ID'];
    if (testCaseId) {
      const detailsUrl = `/test-case-details?test_case_id=${encodeURIComponent(testCaseId)}`;
      window.open(detailsUrl, '_blank');
    }
  }

  trackByTestCaseId(index: number, testCase: TestCase): string {
    return testCase['Test Case ID'] || testCase['TC ID'] || index.toString();
  }

  getPageNumbers(): number[] {
    const pages: number[] = [];
    const totalPages = this.paginationState.total_pages;
    const currentPage = this.paginationState.current_page;
    
    // Show up to 5 pages around current page
    const start = Math.max(1, currentPage - 2);
    const end = Math.min(totalPages, currentPage + 2);
    
    for (let i = start; i <= end; i++) {
      pages.push(i);
    }
    
    return pages;
  }

  // View toggle methods
  onViewChange(view: ViewMode): void {
    this.currentView = view;
    if (view === 'detail' && this.testCases.length > 0 && this.selectedTestCaseIndex === -1) {
      this.selectTestCase(0);
    }
  }

  onExportRequest(format: string): void {
    this.exportTestCases(format as 'excel' | 'csv' | 'pdf');
  }

  onRefreshRequest(): void {
    this.loadTestCases();
  }

  onClearFiltersRequest(): void {
    this.clearFilters();
  }

  selectTestCase(index: number): void {
    if (index >= 0 && index < this.testCases.length) {
      this.selectedTestCaseIndex = index;
      this.selectedTestCase = this.testCases[index];
    }
  }

  // UI helper methods
  getPriorityBadgeClass(priority: string): string {
    switch (priority?.toLowerCase()) {
      case 'high':
      case 'p1':
        return 'badge bg-danger';
      case 'medium':
      case 'p2':
        return 'badge bg-warning';
      case 'low':
      case 'p3':
        return 'badge bg-success';
      case 'p4':
        return 'badge bg-info';
      default:
        return 'badge bg-secondary';
    }
  }

  hasAdditionalDetails(testCase: TestCase): boolean {
    return !!(testCase['Preconditions'] || testCase['Procedure'] || testCase['Expected Behavior']);
  }

  copyTestCaseId(): void {
    if (this.selectedTestCase) {
      const testCaseId = this.selectedTestCase['Test Case ID'] || this.selectedTestCase['TC ID'];
      if (testCaseId) {
        navigator.clipboard.writeText(testCaseId).then(() => {
          // You could show a toast notification here
          console.log('Test case ID copied to clipboard');
        });
      }
    }
  }

  saveCurrentFilter(): void {
    // Save filter state to localStorage
    const filterData = {
      app_filter: this.filterState.app_filter,
      test_type_filter: this.filterState.test_type_filter,
      priority_filter: this.filterState.priority_filter,
      feature_filter: this.filterState.feature_filter,
      region_filter: this.filterState.region_filter,
      search_query: this.filterState.search_query,
      timestamp: new Date().toISOString()
    };
    
    localStorage.setItem('validex_saved_filter', JSON.stringify(filterData));
    
    // Show success message (you could implement a toast notification here)
    console.log('Filter saved successfully:', filterData);
    
    // Optional: Show a brief success indicator
    const saveButton = document.querySelector('.filter-actions .btn-link');
    if (saveButton) {
      const originalText = saveButton.textContent;
      saveButton.textContent = 'Saved!';
      saveButton.classList.add('text-success');
      setTimeout(() => {
        saveButton.textContent = originalText;
        saveButton.classList.remove('text-success');
        saveButton.classList.add('text-primary');
      }, 2000);
    }
  }

  // Filter count methods
  getFilterCount(filterType: string): number {
    const filter = this.filterState[filterType as keyof FilterState];
    return Array.isArray(filter) ? filter.length : 0;
  }

  // App filter methods
  isAppSelected(app: string): boolean {
    return this.filterState.app_filter.includes(app);
  }

  toggleAppFilter(app: string, event: any): void {
    if (event.target.checked) {
      if (!this.filterState.app_filter.includes(app)) {
        this.filterState.app_filter.push(app);
      }
    } else {
      this.filterState.app_filter = this.filterState.app_filter.filter(a => a !== app);
    }
  }

  clearAppFilter(): void {
    this.filterState.app_filter = [];
  }

  filterAppOptions(): void {
    this.filteredAppOptions = this.filterOptions.apps.filter(app => 
      app.toLowerCase().includes(this.appSearchQuery.toLowerCase())
    );
  }

  // Test Type filter methods
  isTestTypeSelected(type: string): boolean {
    return this.filterState.test_type_filter.includes(type);
  }

  toggleTestTypeFilter(type: string, event: any): void {
    if (event.target.checked) {
      if (!this.filterState.test_type_filter.includes(type)) {
        this.filterState.test_type_filter.push(type);
      }
    } else {
      this.filterState.test_type_filter = this.filterState.test_type_filter.filter(t => t !== type);
    }
  }

  clearTestTypeFilter(): void {
    this.filterState.test_type_filter = [];
  }

  filterTestTypeOptions(): void {
    this.filteredTestTypeOptions = this.filterOptions.test_types.filter(type => 
      type.toLowerCase().includes(this.testTypeSearchQuery.toLowerCase())
    );
  }

  // Priority filter methods
  isPrioritySelected(priority: string): boolean {
    return this.filterState.priority_filter.includes(priority);
  }

  togglePriorityFilter(priority: string, event: any): void {
    if (event.target.checked) {
      if (!this.filterState.priority_filter.includes(priority)) {
        this.filterState.priority_filter.push(priority);
      }
    } else {
      this.filterState.priority_filter = this.filterState.priority_filter.filter(p => p !== priority);
    }
  }

  clearPriorityFilter(): void {
    this.filterState.priority_filter = [];
  }

  filterPriorityOptions(): void {
    this.filteredPriorityOptions = this.filterOptions.priorities.filter(priority => 
      priority.toLowerCase().includes(this.prioritySearchQuery.toLowerCase())
    );
  }

  // Feature filter methods
  isFeatureSelected(feature: string): boolean {
    return this.filterState.feature_filter.includes(feature);
  }

  toggleFeatureFilter(feature: string, event: any): void {
    if (event.target.checked) {
      if (!this.filterState.feature_filter.includes(feature)) {
        this.filterState.feature_filter.push(feature);
      }
    } else {
      this.filterState.feature_filter = this.filterState.feature_filter.filter(f => f !== feature);
    }
  }

  clearFeatureFilter(): void {
    this.filterState.feature_filter = [];
  }

  filterFeatureOptions(): void {
    this.filteredFeatureOptions = this.filterOptions.features.filter(feature => 
      feature.toLowerCase().includes(this.featureSearchQuery.toLowerCase())
    );
  }

  // Screen ID filter methods
  isScreenIdSelected(screenId: string): boolean {
    return this.filterState.screen_id_filter.includes(screenId);
  }

  toggleScreenIdFilter(screenId: string, event: any): void {
    if (event.target.checked) {
      if (!this.filterState.screen_id_filter.includes(screenId)) {
        this.filterState.screen_id_filter.push(screenId);
      }
    } else {
      this.filterState.screen_id_filter = this.filterState.screen_id_filter.filter(s => s !== screenId);
    }
  }

  clearScreenIdFilter(): void {
    this.filterState.screen_id_filter = [];
  }

  filterScreenIdOptions(): void {
    this.filteredScreenIdOptions = this.filterOptions.screen_ids.filter(screenId => 
      screenId.toLowerCase().includes(this.screenIdSearchQuery.toLowerCase())
    );
  }

  // Test Suite Type filter methods
  isTestSuiteTypeSelected(type: string): boolean {
    return this.filterState.test_suite_type_filter.includes(type);
  }

  toggleTestSuiteTypeFilter(type: string, event: any): void {
    if (event.target.checked) {
      if (!this.filterState.test_suite_type_filter.includes(type)) {
        this.filterState.test_suite_type_filter.push(type);
      }
    } else {
      this.filterState.test_suite_type_filter = this.filterState.test_suite_type_filter.filter(t => t !== type);
    }
  }

  clearTestSuiteTypeFilter(): void {
    this.filterState.test_suite_type_filter = [];
  }

  filterTestSuiteTypeOptions(): void {
    this.filteredTestSuiteTypeOptions = this.filterOptions.test_suite_types.filter(type => 
      type.toLowerCase().includes(this.testSuiteTypeSearchQuery.toLowerCase())
    );
  }

  // Requirement Type filter methods
  isRequirementTypeSelected(type: string): boolean {
    return this.filterState.requirement_type_filter.includes(type);
  }

  toggleRequirementTypeFilter(type: string, event: any): void {
    if (event.target.checked) {
      if (!this.filterState.requirement_type_filter.includes(type)) {
        this.filterState.requirement_type_filter.push(type);
      }
    } else {
      this.filterState.requirement_type_filter = this.filterState.requirement_type_filter.filter(t => t !== type);
    }
  }

  clearRequirementTypeFilter(): void {
    this.filterState.requirement_type_filter = [];
  }

  filterRequirementTypeOptions(): void {
    this.filteredRequirementTypeOptions = this.filterOptions.requirement_types.filter(type => 
      type.toLowerCase().includes(this.requirementTypeSearchQuery.toLowerCase())
    );
  }

  // More filters methods
  clearMoreFilters(): void {
    this.clearScreenIdFilter();
    this.clearTestSuiteTypeFilter();
    this.clearRequirementTypeFilter();
  }

  // Apply filters method
  applyFilters(): void {
    this.onFilterChange();
  }

  // Clear all filters method
  clearAllFilters(): void {
    this.filterState = {
      app_filter: [],
      test_type_filter: [],
      priority_filter: [],
      feature_filter: [],
      screen_id_filter: [],
      test_suite_type_filter: [],
      requirement_type_filter: [],
      region_filter: [],
      brand_filter: [],
      search_query: '',
      sort_by: 'Test Case ID',
      sort_order: 'asc'
    };
    
    // Clear search queries
    this.appSearchQuery = '';
    this.testTypeSearchQuery = '';
    this.prioritySearchQuery = '';
    this.featureSearchQuery = '';
    this.screenIdSearchQuery = '';
    this.testSuiteTypeSearchQuery = '';
    this.requirementTypeSearchQuery = '';
    
    // Reset filtered options
    this.initializeFilteredOptions();
    
      this.onFilterChange();
    }

  // Dropdown toggle methods
  toggleAppDropdown(): void {
    this.appDropdownOpen = !this.appDropdownOpen;
    // Close other dropdowns
    this.testTypeDropdownOpen = false;
    this.priorityDropdownOpen = false;
    this.featureDropdownOpen = false;
    this.moreFiltersDropdownOpen = false;
  }

  toggleTestTypeDropdown(): void {
    this.testTypeDropdownOpen = !this.testTypeDropdownOpen;
    // Close other dropdowns
    this.appDropdownOpen = false;
    this.priorityDropdownOpen = false;
    this.featureDropdownOpen = false;
    this.moreFiltersDropdownOpen = false;
  }

  togglePriorityDropdown(): void {
    this.priorityDropdownOpen = !this.priorityDropdownOpen;
    // Close other dropdowns
    this.appDropdownOpen = false;
    this.testTypeDropdownOpen = false;
    this.featureDropdownOpen = false;
    this.moreFiltersDropdownOpen = false;
  }

  toggleFeatureDropdown(): void {
    this.featureDropdownOpen = !this.featureDropdownOpen;
    // Close other dropdowns
    this.appDropdownOpen = false;
    this.testTypeDropdownOpen = false;
    this.priorityDropdownOpen = false;
    this.moreFiltersDropdownOpen = false;
  }

  toggleMoreFiltersDropdown(): void {
    this.moreFiltersDropdownOpen = !this.moreFiltersDropdownOpen;
    // Close other dropdowns
    this.appDropdownOpen = false;
    this.testTypeDropdownOpen = false;
    this.priorityDropdownOpen = false;
    this.featureDropdownOpen = false;
  }
}