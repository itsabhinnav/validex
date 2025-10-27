import { Component, OnInit, HostListener } from '@angular/core';
import { Router } from '@angular/router';
import { TestCasesService } from '../../services/test-cases.service';
import { TestCase, FilterOptions, FilterState, PaginationState } from '../../models/high-performance-test-case.model';

export type ViewMode = 'list' | 'detail' | 'more';

export interface DynamicFilter {
  columnName: string;
  displayName: string;
  values: string[];
  selectedValues: string[];
  dropdownOpen?: boolean;
  searchQuery?: string;
  filteredValues?: string[];
}

@Component({
  selector: 'app-test-cases',
  templateUrl: './test-cases.component.html',
  styleUrls: ['./test-cases.component.css']
})
export class TestCasesComponent implements OnInit {
  testCases: TestCase[] = [];
  filterOptions: FilterOptions = {
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
  
  filterState: FilterState = {
    app_filter: [],  // Empty since app filter is removed
    test_type_filter: [],
    priority_filter: [],
    feature_filter: [],
    screen_id_filter: [],
    test_suite_type_filter: [],
    requirement_type_filter: [],
    region_filter: [],
    brand_filter: [],
    status_filter: [],
    search_query: '',
    sort_by: 'tc_id',
    sort_order: 'asc'
  };
  
  paginationState: PaginationState = {
    current_page: 1,
    per_page: 20,
    total_cases: 0,
    total_pages: 0,
    has_prev: false,
    has_next: false
  };

  currentView: ViewMode = 'list';
  searchQuery: string = '';
  
  // Default filters that should always be visible
  defaultFilters: string[] = ['feature', 'screen_id', 'test_type', 'test_suite_type', 'requirement_type'];
  
  // Available columns for "More filters" dropdown (excluding default filters)
  availableColumns: string[] = [
    'tc_id', 'summary', 'test_objective', 'priority', 'preconditions', 
    'procedure', 'expected_behavior', 'region', 'brand', 'app_name', 
    'test_category', 'reference_document', 'associated_requirements', 
    'dr_applicable_screens', 'test_data', 'test_environment', 'automation_status'
  ];
  
  // Currently active filters in the main filter bar
  activeFilters: DynamicFilter[] = [];
  
  // Available filters for "More filters" dropdown (remaining columns)
  availableFilters: DynamicFilter[] = [];
  
  // Search query for more filters dropdown
  moreFiltersSearchQuery: string = '';
  
  // Dropdown states
  moreFiltersDropdownOpen: boolean = false;

  // Selected test case for detail view
  selectedTestCase: TestCase | null = null;
  selectedTestCaseIndex: number = -1;

  loading = false;
  totalTestCases: number = 0;
  error: string | null = null;
  private searchTimeout: any;
  
  // Filter dropdown state
  activeDropdown: string | null = null;
  filterSearchQuery: string = '';
  columnSearchQuery: string = '';

  constructor(
    private testCasesService: TestCasesService,
    private router: Router
  ) { }

  @HostListener('document:click', ['$event'])
  onDocumentClick(event: Event): void {
    const target = event.target as HTMLElement;
    
    // Check if click is outside filter dropdowns
    if (!target.closest('.filter-dropdown') && !target.closest('.more-filters-dropdown')) {
      this.closeAllDropdowns();
    }
    
    // Close more filters dropdown
    this.moreFiltersDropdownOpen = false;
  }

  navigateToTestCaseDetails(testCase: TestCase, event?: Event): void {
    if (event) {
      event.preventDefault();
      event.stopPropagation();
    }
    
    const testCaseId = testCase.tc_id;
    if (testCaseId) {
      this.router.navigate(['/test-case', testCaseId]);
    }
  }

  ngOnInit(): void {
    console.log('=== COMPONENT INITIALIZATION ===');
    this.loadFilterOptions();
    this.loadTestCases();
    this.initializeDynamicFilters();
    
    // Restore persisted state
    this.restorePersistedState();
    
    console.log('=== END COMPONENT INITIALIZATION ===');
  }

  initializeDynamicFilters(): void {
    // Initialize default filters
    this.initializeDefaultFilters();
    
    // Initialize available filters
    this.updateAvailableFilters();
  }

  initializeDefaultFilters(): void {
    this.defaultFilters.forEach(columnName => {
      const defaultFilter: DynamicFilter = {
        columnName,
        displayName: this.getDisplayName(columnName),
        values: this.getColumnValues(columnName),
        selectedValues: [],
        dropdownOpen: false,
        searchQuery: '',
        filteredValues: this.getColumnValues(columnName)
      };
      this.activeFilters.push(defaultFilter);
    });
  }

  updateAvailableFilters(): void {
    // Create available filters for all non-default columns
    // The "More filters" dropdown should always show all available columns
    this.availableFilters = this.availableColumns.map(columnName => ({
      columnName,
      displayName: this.getDisplayName(columnName),
      values: this.getColumnValues(columnName),
      selectedValues: []
    }));
  }

  updateDynamicFilterValues(): void {
    // Update values for active filters
    this.activeFilters.forEach(filter => {
      filter.values = this.getColumnValues(filter.columnName);
      filter.filteredValues = this.getColumnValues(filter.columnName);
    });
    
    // Update values for available filters
    this.availableFilters.forEach(filter => {
      filter.values = this.getColumnValues(filter.columnName);
    });
  }

  getColumnValues(columnName: string): string[] {
    const values = new Set<string>();
    this.testCases.forEach(testCase => {
      const value = (testCase as any)[columnName];
      if (value && typeof value === 'string' && value.trim()) {
        values.add(value.trim());
      }
    });
    return Array.from(values).sort();
  }

  getDisplayName(columnName: string): string {
    // Handle specific column names that should not be split
    const specialCases: { [key: string]: string } = {
      'screen_id': 'Screen ID',
      'tc_id': 'Test Case ID',
      'test_suite_type': 'TestSuite Type',
      'requirement_type': 'Requirement Type',
      'test_objective': 'Test Objective',
      'expected_behavior': 'Expected Behavior',
      'app_name': 'App Name',
      'test_category': 'Test Category',
      'reference_document': 'Reference Document',
      'associated_requirements': 'Associated Requirements',
      'dr_applicable_screens': 'DR Applicable Screens',
      'test_data': 'Test Data',
      'test_environment': 'Test Environment',
      'automation_status': 'Automation Status'
    };
    
    // Return special case if exists
    if (specialCases[columnName]) {
      return specialCases[columnName];
    }
    
    // Convert column name to display name for other cases
    return columnName.replace(/_/g, ' ').replace(/([A-Z])/g, ' $1').trim();
  }

  addFilterToActive(columnName: string): void {
    const availableFilter = this.availableFilters.find(f => f.columnName === columnName);
    if (availableFilter) {
      // Create a new active filter (non-default filters will use success styling)
      const newFilter: DynamicFilter = {
        columnName: availableFilter.columnName,
        displayName: availableFilter.displayName,
        values: [...availableFilter.values],
        selectedValues: [],
        dropdownOpen: false,
        searchQuery: '',
        filteredValues: [...availableFilter.values]
      };
      
      this.activeFilters.push(newFilter);
      this.updateAvailableFilters();
      this.applyDynamicFilters();
      
      // Save state
      this.savePersistedState();
    }
  }

  removeFilterFromActive(columnName: string): void {
    // Prevent removal of default filters
    if (this.defaultFilters.includes(columnName)) {
      return;
    }
    
    this.activeFilters = this.activeFilters.filter(f => f.columnName !== columnName);
    this.updateAvailableFilters();
    this.applyDynamicFilters();
    
    // Save state
    this.savePersistedState();
  }

  toggleDynamicFilterValue(columnName: string, value: string, isChecked: boolean): void {
    const filter = this.activeFilters.find(f => f.columnName === columnName);
    if (filter) {
      if (isChecked) {
        if (!filter.selectedValues.includes(value)) {
          filter.selectedValues.push(value);
        }
      } else {
        filter.selectedValues = filter.selectedValues.filter(v => v !== value);
      }
      this.applyDynamicFilters();
      
      // Save state
      this.savePersistedState();
    }
  }

  applyDynamicFilters(): void {
    // Apply dynamic filters to the main filter state
    this.activeFilters.forEach(filter => {
      const columnName = filter.columnName;
      
      // Map dynamic filter values to filterState properties
      switch (columnName) {
        case 'test_type':
          this.filterState.test_type_filter = filter.selectedValues;
          break;
        case 'priority':
          this.filterState.priority_filter = filter.selectedValues;
          break;
        case 'feature':
          this.filterState.feature_filter = filter.selectedValues;
          break;
        case 'screen_id':
          this.filterState.screen_id_filter = filter.selectedValues;
          break;
        case 'test_suite_type':
          this.filterState.test_suite_type_filter = filter.selectedValues;
          break;
        case 'requirement_type':
          this.filterState.requirement_type_filter = filter.selectedValues;
          break;
        case 'region':
          this.filterState.region_filter = filter.selectedValues;
          break;
        case 'brand':
          this.filterState.brand_filter = filter.selectedValues;
          break;
        case 'status':
          this.filterState.status_filter = filter.selectedValues;
          break;
        default:
          console.warn('Unknown filter column:', columnName);
      }
    });
    
    console.log('Applied dynamic filters to filterState:', this.filterState);
    
    // Trigger filter change to reload data
    this.onFilterChange();
  }

  clearDynamicFilter(columnName: string): void {
    const filter = this.activeFilters.find(f => f.columnName === columnName);
    if (filter) {
      filter.selectedValues = [];
      this.applyDynamicFilters();
    }
  }

  clearAllDynamicFilters(): void {
    this.activeFilters.forEach(filter => {
      filter.selectedValues = [];
    });
    this.applyDynamicFilters();
  }

  getFilteredAvailableFilters(): DynamicFilter[] {
    if (!this.moreFiltersSearchQuery.trim()) {
      return this.availableFilters;
    }
    
    return this.availableFilters.filter(filter => 
      filter.displayName.toLowerCase().includes(this.moreFiltersSearchQuery.toLowerCase())
    );
  }

  isDynamicFilterValueSelected(columnName: string, value: string): boolean {
    const filter = this.activeFilters.find(f => f.columnName === columnName);
    return filter ? filter.selectedValues.includes(value) : false;
  }

  getDynamicFilterCount(columnName: string): number {
    const filter = this.activeFilters.find(f => f.columnName === columnName);
    return filter ? filter.selectedValues.length : 0;
  }

  isDefaultFilter(columnName: string): boolean {
    return this.defaultFilters.includes(columnName);
  }

  getFilteredValues(filter: DynamicFilter): string[] {
    if (!filter.searchQuery || !filter.searchQuery.trim()) {
      return filter.values;
    }
    
    return filter.values.filter(value => 
      value.toLowerCase().includes(filter.searchQuery!.toLowerCase())
    );
  }

  filterFilterValues(filter: DynamicFilter): void {
    filter.filteredValues = this.getFilteredValues(filter);
  }

  getStatusTagClass(status: string): string {
    if (!status) return 'status-tag-default';
    
    const statusLower = status.toLowerCase();
    if (statusLower.includes('done') || statusLower.includes('completed')) {
      return 'status-tag-done';
    } else if (statusLower.includes('progress') || statusLower.includes('in progress')) {
      return 'status-tag-progress';
    } else if (statusLower.includes('review')) {
      return 'status-tag-review';
    } else if (statusLower.includes('todo') || statusLower.includes('pending')) {
      return 'status-tag-todo';
    }
    return 'status-tag-default';
  }

  toggleFilterDropdown(columnName: string, event?: Event): void {
    if (event) {
      event.preventDefault();
      event.stopPropagation();
    }
    
    const filter = this.activeFilters.find(f => f.columnName === columnName);
    if (filter) {
      filter.dropdownOpen = !filter.dropdownOpen;
      
      // Close other dropdowns
      this.activeFilters.forEach(f => {
        if (f.columnName !== columnName) {
          f.dropdownOpen = false;
        }
      });
      
      // Close more filters dropdown
      this.moreFiltersDropdownOpen = false;
    }
  }

  toggleMoreFiltersDropdown(event?: Event): void {
    if (event) {
      event.preventDefault();
      event.stopPropagation();
    }
    
    this.moreFiltersDropdownOpen = !this.moreFiltersDropdownOpen;
    
    // Close all filter dropdowns
    this.activeFilters.forEach(filter => {
      filter.dropdownOpen = false;
    });
  }

  closeAllDropdowns(): void {
    this.activeFilters.forEach(filter => {
      filter.dropdownOpen = false;
    });
    this.moreFiltersDropdownOpen = false;
  }

  loadFilterOptions(): void {
    this.testCasesService.getFilterOptions().subscribe({
      next: (options) => {
        this.filterOptions = options;
        console.log('Filter options loaded:', options);
      },
      error: (error) => {
        console.error('Error loading filter options:', error);
      }
    });
  }

  loadTestCases(): void {
    console.log('=== LOADING TEST CASES ===');
    this.loading = true;
    this.error = null;
    
    this.testCasesService.getTestCases(this.filterState, this.paginationState).subscribe({
      next: (response) => {
        console.log('Test cases loaded:', response.test_cases.length);
        this.testCases = response.test_cases;
        this.filterOptions = response.filter_options;
        this.paginationState = response.pagination;
        this.totalTestCases = response.pagination.total_cases;
        this.loading = false;
        
        // Update dynamic filters with new data
        this.updateDynamicFilterValues();
        
        // Handle selected test case for detail view
        if (this.currentView === 'detail' && this.testCases.length > 0) {
          // Check if current selected test case is still valid
          if (this.selectedTestCase && this.selectedTestCaseIndex >= 0) {
            const testCaseId = this.selectedTestCase.tc_id;
            const foundIndex = this.testCases.findIndex(tc => 
              tc.tc_id === testCaseId
            );
            
            if (foundIndex >= 0) {
              // Update the selected test case with fresh data
              this.selectedTestCase = this.testCases[foundIndex];
              this.selectedTestCaseIndex = foundIndex;
              console.log('Updated selected test case with fresh data:', this.selectedTestCase);
            } else {
              // Selected test case not found, select first one
              this.selectTestCase(0);
              console.log('Selected test case not found, selected first test case');
            }
          } else {
            // No selected test case, select first one
          this.selectTestCase(0);
            console.log('No selected test case, selected first test case');
          }
        }
        
        console.log('After load - selectedTestCase:', this.selectedTestCase);
        console.log('After load - currentView:', this.currentView);
        console.log('=== END LOADING TEST CASES ===');
      },
      error: (error) => {
        console.error('Error loading test cases:', error);
        this.error = 'Failed to load test cases';
        this.loading = false;
      }
    });
  }

  onSearchChange(searchQuery: string): void {
    this.filterState.search_query = searchQuery;
    // Debounce search to avoid too many requests
    clearTimeout(this.searchTimeout);
    this.searchTimeout = setTimeout(() => {
      this.onFilterChange();
    }, 300);
    
    // Save state
    this.savePersistedState();
  }

  onFilterChange(): void {
    this.paginationState.current_page = 1; // Reset to first page
    this.loadTestCases();
  }

  onSortChange(sortBy: string, sortOrder: 'asc' | 'desc'): void {
    this.filterState.sort_by = sortBy;
    this.filterState.sort_order = sortOrder;
    this.applySorting();
    
    // Save state
    this.savePersistedState();
  }

  onPageChange(page: number): void {
    console.log('=== PAGE CHANGE DEBUG ===');
    console.log('Requested page:', page);
    console.log('Current page before change:', this.paginationState.current_page);
    console.log('Total pages:', this.paginationState.total_pages);
    
    // Validate page number
    if (page < 1 || page > this.paginationState.total_pages) {
      console.warn('Invalid page number:', page);
      return;
    }
    
    this.paginationState.current_page = page;
    console.log('Page set to:', this.paginationState.current_page);
    
    this.loadTestCases();
    
    console.log('=== END PAGE CHANGE DEBUG ===');
    
    // Save state
    this.savePersistedState();
  }

  onPerPageChange(perPage: number): void {
    this.paginationState.per_page = perPage;
    this.paginationState.current_page = 1; // Reset to first page
    this.loadTestCases();
    
    // Save state
    this.savePersistedState();
  }

  onViewChange(view: ViewMode): void {
    this.currentView = view;
    
    // If switching to detail view and no test case selected, select first one
    if (view === 'detail' && this.testCases.length > 0 && !this.selectedTestCase) {
      this.selectTestCase(0);
    }
    
    // Save state
    this.savePersistedState();
  }

  selectTestCase(index: number): void {
    if (index >= 0 && index < this.testCases.length) {
      this.selectedTestCase = this.testCases[index];
      this.selectedTestCaseIndex = index;
      console.log('Selected test case:', this.selectedTestCase);
    }
  }

  viewTestCaseDetails(testCase: TestCase, event?: Event): void {
    if (event) {
      event.preventDefault();
      event.stopPropagation();
    }
    
    // Switch to detail view
    this.currentView = 'detail';
    
    // Find and select the test case
    const index = this.testCases.findIndex(tc => 
      tc.tc_id === testCase.tc_id
    );
    
    if (index >= 0) {
      this.selectTestCase(index);
    }
    
    // Save state
    this.savePersistedState();
  }

  clearFilters(): void {
    // Clear all dynamic filters but preserve default filters
    this.activeFilters.forEach(filter => {
      filter.selectedValues = [];
    });
    
    // Clear search query
    this.filterState.search_query = '';
    this.searchQuery = '';
    
    // Reset pagination
    this.paginationState.current_page = 1;
    
    // Clear persisted state
    this.clearPersistedState();
    
    // Reload data
    this.loadTestCases();
  }

  // Sorting functionality
  sortColumn(column: string): void {
    if (this.filterState.sort_by === column) {
      this.filterState.sort_order = this.filterState.sort_order === 'asc' ? 'desc' : 'asc';
    } else {
      this.filterState.sort_by = column;
      this.filterState.sort_order = 'asc';
    }
    
    this.applySorting();
    
    // Save state
    this.savePersistedState();
  }

  applySorting(): void {
    // Client-side sorting
    this.testCases.sort((a, b) => {
      const aValue = (a as any)[this.filterState.sort_by] || '';
      const bValue = (b as any)[this.filterState.sort_by] || '';
      
      let comparison = 0;
      if (aValue < bValue) {
        comparison = -1;
      } else if (aValue > bValue) {
        comparison = 1;
      }
      
      return this.filterState.sort_order === 'asc' ? comparison : -comparison;
    });
  }

  getSortIconClass(column: string): string {
    if (this.filterState.sort_by !== column) {
      return 'fas fa-sort';
    }
    return this.filterState.sort_order === 'asc' ? 'fas fa-sort-up' : 'fas fa-sort-down';
  }

  // Persistence functionality
  savePersistedState(): void {
    const state = {
      currentView: this.currentView,
      searchQuery: this.searchQuery,
      pagination: {
        current_page: this.paginationState.current_page,
        per_page: this.paginationState.per_page
      },
      sorting: {
        sort_by: this.filterState.sort_by,
        sort_order: this.filterState.sort_order
      },
      activeFilters: this.activeFilters.map(filter => ({
        columnName: filter.columnName,
        selectedValues: filter.selectedValues
      })),
      availableFilters: this.availableFilters.map(filter => ({
        columnName: filter.columnName,
        selectedValues: filter.selectedValues
      }))
    };
    
    localStorage.setItem('testCasesState', JSON.stringify(state));
  }

  restorePersistedState(): void {
    const savedState = localStorage.getItem('testCasesState');
    if (savedState) {
      try {
        const state = JSON.parse(savedState);
        
        // Restore view
        if (state.currentView) {
          this.currentView = state.currentView;
        }
        
        // Restore search query
        if (state.searchQuery) {
          this.searchQuery = state.searchQuery;
          this.filterState.search_query = state.searchQuery;
        }
        
        // Restore pagination
        if (state.pagination) {
          this.paginationState.current_page = state.pagination.current_page || 1;
          this.paginationState.per_page = state.pagination.per_page || 20;
        }
        
        // Restore sorting
        if (state.sorting) {
          this.filterState.sort_by = state.sorting.sort_by || 'tc_id';
          this.filterState.sort_order = state.sorting.sort_order || 'asc';
        }
        
        // Restore active filters
        if (state.activeFilters) {
          state.activeFilters.forEach((savedFilter: any) => {
            const filter = this.activeFilters.find(f => f.columnName === savedFilter.columnName);
            if (filter) {
              filter.selectedValues = savedFilter.selectedValues || [];
            }
          });
        }
        
        console.log('Restored persisted state:', state);
      } catch (error) {
        console.error('Error restoring persisted state:', error);
      }
    }
  }

  clearPersistedState(): void {
    localStorage.removeItem('testCasesState');
  }

  trackByTestCaseId(index: number, testCase: TestCase): string {
    return testCase.tc_id || index.toString();
  }

  hasActiveFilters(): boolean {
    return this.activeFilters.some(f => f.selectedValues.length > 0);
  }

  // Filter dropdown methods
  isFilterActive(filter: string): boolean {
    return this.activeFilters.some(f => f.columnName === filter && f.selectedValues.length > 0);
  }

  closeFilterDropdown(): void {
    this.activeDropdown = null;
  }

  onFilterSearchChange(): void {
    // Filter search logic can be implemented here
  }

  getFilterOptions(filter: string): string[] {
    const filterObj = this.filterOptions as any;
    return filterObj[filter] || [];
  }

  isOptionSelected(filter: string, option: string): boolean {
    const activeFilter = this.activeFilters.find(f => f.columnName === filter);
    return activeFilter ? activeFilter.selectedValues.includes(option) : false;
  }

  toggleFilterOption(filter: string, option: string): void {
    const activeFilter = this.activeFilters.find(f => f.columnName === filter);
    if (activeFilter) {
      const index = activeFilter.selectedValues.indexOf(option);
      if (index > -1) {
        activeFilter.selectedValues.splice(index, 1);
      } else {
        activeFilter.selectedValues.push(option);
      }
    }
    this.applyDynamicFilters();
  }

  closeMoreFiltersDropdown(): void {
    this.moreFiltersDropdownOpen = false;
  }

  onColumnSearchChange(): void {
    // Column search logic can be implemented here
  }

  getAvailableColumns(): string[] {
    return this.availableColumns;
  }

  isColumnActive(column: string): boolean {
    return this.activeFilters.some(f => f.columnName === column);
  }

  toggleColumnFilter(column: string): void {
    const existingFilter = this.activeFilters.find(f => f.columnName === column);
    if (existingFilter) {
      // Remove filter
      const index = this.activeFilters.indexOf(existingFilter);
      this.activeFilters.splice(index, 1);
    } else {
      // Add filter
      this.activeFilters.push({
        columnName: column,
        displayName: this.getDisplayName(column),
        selectedValues: [],
        values: []
      });
    }
    this.applyDynamicFilters();
  }

  getPriorityBadgeClass(priority: string): string {
    if (!priority) return 'bg-secondary';
    
    const priorityLower = priority.toLowerCase();
    if (priorityLower.includes('high')) {
      return 'bg-danger';
    } else if (priorityLower.includes('medium')) {
      return 'bg-warning';
    } else if (priorityLower.includes('low')) {
      return 'bg-success';
    }
    return 'bg-secondary';
  }
}