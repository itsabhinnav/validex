/**
 * Dynamic Filtering System for Test Cases
 * Provides advanced filtering capabilities with multiple filter types
 */

class DynamicFiltering {
    constructor() {
        this.filterOptions = {};
        this.availableColumns = [];
        this.columnStatistics = {};
        this.filterTypes = [];
        this.activeFilters = [];
        this.currentPage = 1;
        this.perPage = 50;
        this.sortBy = 'TC ID';
        this.sortOrder = 'asc';
        
        this.init();
    }
    
    async init() {
        await this.loadFilterOptions();
        this.setupEventListeners();
        this.renderFilterInterface();
    }
    
    async loadFilterOptions() {
        try {
            const response = await fetch('/api/filter-options');
            const data = await response.json();
            
            this.filterOptions = data.filter_options;
            this.availableColumns = data.available_columns;
            this.columnStatistics = data.column_statistics;
            this.filterTypes = data.filter_types;
            
            console.log('Filter options loaded:', this.filterOptions);
        } catch (error) {
            console.error('Error loading filter options:', error);
        }
    }
    
    setupEventListeners() {
        // Add filter button
        document.addEventListener('click', (e) => {
            if (e.target.matches('.add-filter-btn')) {
                this.addFilter();
            }
            if (e.target.matches('.remove-filter-btn')) {
                this.removeFilter(e.target.dataset.filterId);
            }
            if (e.target.matches('.apply-filters-btn')) {
                this.applyFilters();
            }
            if (e.target.matches('.clear-filters-btn')) {
                this.clearFilters();
            }
        });
        
        // Column selection change
        document.addEventListener('change', (e) => {
            if (e.target.matches('.filter-column-select')) {
                this.updateFilterOptions(e.target);
            }
        });
    }
    
    renderFilterInterface() {
        const container = document.getElementById('dynamic-filters-container');
        if (!container) return;
        
        container.innerHTML = `
            <div class="dynamic-filters-header mb-3">
                <h5>Advanced Filters</h5>
                <div class="btn-group">
                    <button class="btn btn-primary btn-sm add-filter-btn">
                        <i class="fas fa-plus"></i> Add Filter
                    </button>
                    <button class="btn btn-success btn-sm apply-filters-btn">
                        <i class="fas fa-search"></i> Apply Filters
                    </button>
                    <button class="btn btn-outline-secondary btn-sm clear-filters-btn">
                        <i class="fas fa-times"></i> Clear All
                    </button>
                </div>
            </div>
            <div class="filters-list" id="filters-list">
                ${this.renderFiltersList()}
            </div>
            <div class="filter-summary mt-3" id="filter-summary">
                ${this.renderFilterSummary()}
            </div>
        `;
    }
    
    renderFiltersList() {
        if (this.activeFilters.length === 0) {
            return '<p class="text-muted">No filters applied. Click "Add Filter" to start filtering.</p>';
        }
        
        return this.activeFilters.map((filter, index) => `
            <div class="filter-item card mb-2" data-filter-id="${filter.id}">
                <div class="card-body py-2">
                    <div class="row align-items-center">
                        <div class="col-md-3">
                            <select class="form-select form-select-sm filter-column-select" data-filter-id="${filter.id}">
                                <option value="">Select Column</option>
                                ${this.availableColumns.map(col => 
                                    `<option value="${col}" ${filter.column === col ? 'selected' : ''}>${col}</option>`
                                ).join('')}
                            </select>
                        </div>
                        <div class="col-md-2">
                            <select class="form-select form-select-sm filter-type-select" data-filter-id="${filter.id}">
                                ${this.filterTypes.map(type => 
                                    `<option value="${type}" ${filter.type === type ? 'selected' : ''}>${this.getFilterTypeLabel(type)}</option>`
                                ).join('')}
                            </select>
                        </div>
                        <div class="col-md-4">
                            ${this.renderFilterValueInput(filter)}
                        </div>
                        <div class="col-md-2">
                            <div class="form-check">
                                <input class="form-check-input filter-enabled-check" type="checkbox" 
                                       data-filter-id="${filter.id}" ${filter.enabled ? 'checked' : ''}>
                                <label class="form-check-label">Enabled</label>
                            </div>
                        </div>
                        <div class="col-md-1">
                            <button class="btn btn-outline-danger btn-sm remove-filter-btn" 
                                    data-filter-id="${filter.id}">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }
    
    renderFilterValueInput(filter) {
        const columnOptions = this.filterOptions[filter.column] || [];
        
        switch (filter.type) {
            case 'in_list':
            case 'not_in_list':
                return `
                    <select class="form-select form-select-sm filter-value-select" multiple 
                            data-filter-id="${filter.id}">
                        ${columnOptions.map(option => 
                            `<option value="${option}" ${filter.value.includes(option) ? 'selected' : ''}>${option}</option>`
                        ).join('')}
                    </select>
                `;
            case 'between':
                return `
                    <div class="input-group input-group-sm">
                        <input type="text" class="form-control filter-value-input" 
                               placeholder="Min" data-filter-id="${filter.id}" data-part="min" 
                               value="${filter.value.min || ''}">
                        <span class="input-group-text">to</span>
                        <input type="text" class="form-control filter-value-input" 
                               placeholder="Max" data-filter-id="${filter.id}" data-part="max" 
                               value="${filter.value.max || ''}">
                    </div>
                `;
            case 'is_empty':
            case 'is_not_empty':
                return '<span class="text-muted">No value needed</span>';
            default:
                return `
                    <input type="text" class="form-control form-control-sm filter-value-input" 
                           data-filter-id="${filter.id}" value="${filter.value || ''}" 
                           placeholder="Enter value...">
                `;
        }
    }
    
    renderFilterSummary() {
        const enabledFilters = this.activeFilters.filter(f => f.enabled);
        if (enabledFilters.length === 0) {
            return '<p class="text-muted">No active filters</p>';
        }
        
        return `
            <div class="alert alert-info">
                <strong>Active Filters (${enabledFilters.length}):</strong>
                ${enabledFilters.map(filter => 
                    `<span class="badge bg-primary me-1">
                        ${filter.column} ${this.getFilterTypeLabel(filter.type)} ${filter.value || ''}
                    </span>`
                ).join('')}
            </div>
        `;
    }
    
    addFilter() {
        const filterId = Date.now().toString();
        const newFilter = {
            id: filterId,
            column: '',
            type: 'exact',
            value: '',
            enabled: true
        };
        
        this.activeFilters.push(newFilter);
        this.renderFilterInterface();
    }
    
    removeFilter(filterId) {
        this.activeFilters = this.activeFilters.filter(f => f.id !== filterId);
        this.renderFilterInterface();
    }
    
    updateFilterOptions(selectElement) {
        const filterId = selectElement.dataset.filterId;
        const filter = this.activeFilters.find(f => f.id === filterId);
        
        if (filter) {
            filter.column = selectElement.value;
            filter.value = '';
            this.renderFilterInterface();
        }
    }
    
    getFilterTypeLabel(type) {
        const labels = {
            'exact': 'Equals',
            'contains': 'Contains',
            'starts_with': 'Starts With',
            'ends_with': 'Ends With',
            'regex': 'Regex',
            'in_list': 'In List',
            'not_in_list': 'Not In List',
            'greater_than': 'Greater Than',
            'less_than': 'Less Than',
            'between': 'Between',
            'is_empty': 'Is Empty',
            'is_not_empty': 'Is Not Empty'
        };
        return labels[type] || type;
    }
    
    collectFilters() {
        const filters = [];
        
        this.activeFilters.forEach(filter => {
            if (!filter.enabled) return;
            
            const enabledCheck = document.querySelector(`.filter-enabled-check[data-filter-id="${filter.id}"]`);
            if (enabledCheck && !enabledCheck.checked) return;
            
            const columnSelect = document.querySelector(`.filter-column-select[data-filter-id="${filter.id}"]`);
            const typeSelect = document.querySelector(`.filter-type-select[data-filter-id="${filter.id}"]`);
            
            if (!columnSelect || !typeSelect) return;
            
            const column = columnSelect.value;
            const type = typeSelect.value;
            let value = '';
            
            // Collect value based on filter type
            switch (type) {
                case 'in_list':
                case 'not_in_list':
                    const valueSelect = document.querySelector(`.filter-value-select[data-filter-id="${filter.id}"]`);
                    if (valueSelect) {
                        value = Array.from(valueSelect.selectedOptions).map(opt => opt.value);
                    }
                    break;
                case 'between':
                    const minInput = document.querySelector(`.filter-value-input[data-filter-id="${filter.id}"][data-part="min"]`);
                    const maxInput = document.querySelector(`.filter-value-input[data-filter-id="${filter.id}"][data-part="max"]`);
                    value = {
                        min: minInput ? minInput.value : '',
                        max: maxInput ? maxInput.value : ''
                    };
                    break;
                case 'is_empty':
                case 'is_not_empty':
                    value = null;
                    break;
                default:
                    const valueInput = document.querySelector(`.filter-value-input[data-filter-id="${filter.id}"]`);
                    if (valueInput) {
                        value = valueInput.value;
                    }
            }
            
            if (column && type) {
                filters.push({
                    column: column,
                    type: type,
                    value: value
                });
            }
        });
        
        return filters;
    }
    
    async applyFilters() {
        const filters = this.collectFilters();
        
        const requestData = {
            dynamic_filters: filters,
            search_query: document.getElementById('search-input')?.value || '',
            sort_by: this.sortBy,
            sort_order: this.sortOrder,
            page: this.currentPage,
            per_page: this.perPage
        };
        
        try {
            const response = await fetch('/api/filter-test-cases', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });
            
            const data = await response.json();
            this.displayResults(data);
            
        } catch (error) {
            console.error('Error applying filters:', error);
            alert('Error applying filters. Please try again.');
        }
    }
    
    displayResults(data) {
        const resultsContainer = document.getElementById('test-cases-results');
        if (!resultsContainer) return;
        
        // Update pagination info
        const paginationInfo = document.getElementById('pagination-info');
        if (paginationInfo) {
            paginationInfo.innerHTML = `
                Showing ${data.test_cases.length} of ${data.total_count} test cases
                (Page ${data.page} of ${data.total_pages})
            `;
        }
        
        // Render test cases table
        this.renderTestCasesTable(data.test_cases);
        
        // Update pagination controls
        this.renderPagination(data);
    }
    
    renderTestCasesTable(testCases) {
        const tableContainer = document.getElementById('test-cases-table-container');
        if (!tableContainer) return;
        
        if (testCases.length === 0) {
            tableContainer.innerHTML = '<p class="text-muted">No test cases found matching the criteria.</p>';
            return;
        }
        
        // Get all unique columns from the test cases
        const columns = [...new Set(testCases.flatMap(tc => Object.keys(tc)))];
        
        const tableHTML = `
            <div class="table-responsive">
                <table class="table table-striped table-hover">
                    <thead class="table-dark">
                        <tr>
                            ${columns.map(col => `<th>${col}</th>`).join('')}
                        </tr>
                    </thead>
                    <tbody>
                        ${testCases.map(tc => `
                            <tr>
                                ${columns.map(col => `<td>${tc[col] || ''}</td>`).join('')}
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
        
        tableContainer.innerHTML = tableHTML;
    }
    
    renderPagination(data) {
        const paginationContainer = document.getElementById('pagination-container');
        if (!paginationContainer || data.total_pages <= 1) {
            if (paginationContainer) paginationContainer.innerHTML = '';
            return;
        }
        
        const currentPage = data.page;
        const totalPages = data.total_pages;
        
        let paginationHTML = '<nav><ul class="pagination justify-content-center">';
        
        // Previous button
        if (currentPage > 1) {
            paginationHTML += `<li class="page-item"><a class="page-link" href="#" data-page="${currentPage - 1}">Previous</a></li>`;
        }
        
        // Page numbers
        const startPage = Math.max(1, currentPage - 2);
        const endPage = Math.min(totalPages, currentPage + 2);
        
        for (let i = startPage; i <= endPage; i++) {
            const activeClass = i === currentPage ? 'active' : '';
            paginationHTML += `<li class="page-item ${activeClass}"><a class="page-link" href="#" data-page="${i}">${i}</a></li>`;
        }
        
        // Next button
        if (currentPage < totalPages) {
            paginationHTML += `<li class="page-item"><a class="page-link" href="#" data-page="${currentPage + 1}">Next</a></li>`;
        }
        
        paginationHTML += '</ul></nav>';
        
        paginationContainer.innerHTML = paginationHTML;
        
        // Add click handlers for pagination
        paginationContainer.addEventListener('click', (e) => {
            if (e.target.matches('.page-link')) {
                e.preventDefault();
                this.currentPage = parseInt(e.target.dataset.page);
                this.applyFilters();
            }
        });
    }
    
    clearFilters() {
        this.activeFilters = [];
        this.currentPage = 1;
        this.renderFilterInterface();
        
        // Clear search input
        const searchInput = document.getElementById('search-input');
        if (searchInput) searchInput.value = '';
        
        // Apply empty filters to show all results
        this.applyFilters();
    }
}

// Initialize dynamic filtering when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('dynamic-filters-container')) {
        window.dynamicFiltering = new DynamicFiltering();
    }
});
