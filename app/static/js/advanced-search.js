/**
 * Advanced Search with Autocomplete and Suggestions
 * Enhanced search functionality with real-time suggestions
 */

class AdvancedSearch {
    constructor() {
        this.searchIndex = [];
        this.suggestions = [];
        this.currentQuery = '';
        this.searchHistory = JSON.parse(localStorage.getItem('searchHistory') || '[]');
        this.favoriteSearches = JSON.parse(localStorage.getItem('favoriteSearches') || '[]');
        this.init();
    }

    init() {
        this.createSearchInterface();
        this.buildSearchIndex();
        this.bindEvents();
        this.loadSearchHistory();
    }

    createSearchInterface() {
        const searchContainer = document.createElement('div');
        searchContainer.className = 'advanced-search-container';
        searchContainer.innerHTML = `
            <div class="search-wrapper">
                <div class="search-input-group">
                    <input type="text" 
                           class="form-control search-input" 
                           id="advancedSearchInput" 
                           placeholder="Search test cases, features, or any content..."
                           autocomplete="off">
                    <button class="btn btn-primary search-btn" type="button">
                        <i class="fas fa-search"></i>
                    </button>
                    <button class="btn btn-outline-secondary filter-btn" type="button" data-bs-toggle="collapse" data-bs-target="#searchFilters">
                        <i class="fas fa-filter"></i>
                    </button>
                </div>
                
                <div class="search-suggestions" id="searchSuggestions"></div>
                
                <div class="collapse" id="searchFilters">
                    <div class="search-filters">
                        <div class="row">
                            <div class="col-md-3">
                                <label class="form-label">Priority</label>
                                <select class="form-select" id="filterPriority">
                                    <option value="">All Priorities</option>
                                    <option value="Critical">Critical</option>
                                    <option value="High">High</option>
                                    <option value="Medium">Medium</option>
                                    <option value="Low">Low</option>
                                </select>
                            </div>
                            <div class="col-md-3">
                                <label class="form-label">Status</label>
                                <select class="form-select" id="filterStatus">
                                    <option value="">All Statuses</option>
                                    <option value="Passed">Passed</option>
                                    <option value="Failed">Failed</option>
                                    <option value="Pending">Pending</option>
                                    <option value="Blocked">Blocked</option>
                                </select>
                            </div>
                            <div class="col-md-3">
                                <label class="form-label">App</label>
                                <select class="form-select" id="filterApp">
                                    <option value="">All Apps</option>
                                </select>
                            </div>
                            <div class="col-md-3">
                                <label class="form-label">Test Type</label>
                                <select class="form-select" id="filterType">
                                    <option value="">All Types</option>
                                    <option value="Smoke">Smoke</option>
                                    <option value="Sanity">Sanity</option>
                                    <option value="Regression">Regression</option>
                                    <option value="FMEA">FMEA</option>
                                </select>
                            </div>
                        </div>
                        <div class="row mt-3">
                            <div class="col-md-6">
                                <label class="form-label">Date Range</label>
                                <div class="input-group">
                                    <input type="date" class="form-control" id="filterDateFrom">
                                    <span class="input-group-text">to</span>
                                    <input type="date" class="form-control" id="filterDateTo">
                                </div>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">Search Options</label>
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="exactMatch">
                                    <label class="form-check-label" for="exactMatch">Exact Match</label>
                                </div>
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="caseSensitive">
                                    <label class="form-check-label" for="caseSensitive">Case Sensitive</label>
                                </div>
                            </div>
                        </div>
                        <div class="mt-3">
                            <button class="btn btn-primary" onclick="advancedSearch.performSearch()">
                                <i class="fas fa-search me-2"></i>Search
                            </button>
                            <button class="btn btn-secondary" onclick="advancedSearch.clearFilters()">
                                <i class="fas fa-times me-2"></i>Clear
                            </button>
                            <button class="btn btn-outline-info" onclick="advancedSearch.saveSearch()">
                                <i class="fas fa-bookmark me-2"></i>Save Search
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Add styles
        const style = document.createElement('style');
        style.textContent = `
            .advanced-search-container {
                position: relative;
                margin-bottom: 20px;
            }
            
            .search-wrapper {
                position: relative;
            }
            
            .search-input-group {
                display: flex;
                border-radius: 25px;
                overflow: hidden;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
            
            .search-input {
                border: none;
                padding: 15px 20px;
                font-size: 1.1rem;
                border-radius: 25px 0 0 25px;
            }
            
            .search-input:focus {
                box-shadow: none;
                border-color: #007bff;
            }
            
            .search-btn, .filter-btn {
                border: none;
                padding: 15px 20px;
                border-radius: 0;
            }
            
            .filter-btn {
                border-radius: 0 25px 25px 0;
            }
            
            .search-suggestions {
                position: absolute;
                top: 100%;
                left: 0;
                right: 0;
                background: white;
                border: 1px solid #dee2e6;
                border-top: none;
                border-radius: 0 0 15px 15px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                max-height: 300px;
                overflow-y: auto;
                z-index: 1000;
                display: none;
            }
            
            .suggestion-item {
                padding: 12px 20px;
                cursor: pointer;
                border-bottom: 1px solid #f8f9fa;
                transition: background-color 0.2s;
            }
            
            .suggestion-item:hover,
            .suggestion-item.active {
                background-color: #f8f9fa;
            }
            
            .suggestion-item:last-child {
                border-bottom: none;
            }
            
            .suggestion-text {
                font-weight: 500;
                color: #343a40;
            }
            
            .suggestion-type {
                font-size: 0.85rem;
                color: #6c757d;
                margin-left: 10px;
            }
            
            .suggestion-highlight {
                background-color: #fff3cd;
                padding: 2px 4px;
                border-radius: 3px;
            }
            
            .search-filters {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 15px;
                margin-top: 10px;
                border: 1px solid #dee2e6;
            }
            
            .search-history {
                background: white;
                border: 1px solid #dee2e6;
                border-radius: 10px;
                padding: 15px;
                margin-top: 10px;
            }
            
            .history-item {
                padding: 8px 12px;
                cursor: pointer;
                border-radius: 5px;
                margin-bottom: 5px;
                transition: background-color 0.2s;
            }
            
            .history-item:hover {
                background-color: #f8f9fa;
            }
            
            .search-stats {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 15px;
                border-radius: 10px;
                margin-top: 15px;
            }
        `;
        document.head.appendChild(style);

        // Insert search interface
        const targetElement = document.querySelector('.container') || document.body;
        targetElement.insertBefore(searchContainer, targetElement.firstChild);
    }

    buildSearchIndex() {
        // Build search index from table data
        const table = document.querySelector('table tbody');
        if (!table) return;

        this.searchIndex = [];
        table.querySelectorAll('tr').forEach((row, index) => {
            const cells = row.querySelectorAll('td');
            const item = {
                id: index,
                data: {},
                searchableText: ''
            };

            cells.forEach((cell, cellIndex) => {
                const header = document.querySelector(`thead th:nth-child(${cellIndex + 1})`);
                if (header) {
                    const key = header.textContent.trim();
                    const value = cell.textContent.trim();
                    item.data[key] = value;
                    item.searchableText += value + ' ';
                }
            });

            item.searchableText = item.searchableText.toLowerCase();
            this.searchIndex.push(item);
        });
    }

    bindEvents() {
        const searchInput = document.getElementById('advancedSearchInput');
        if (!searchInput) return;

        // Input events
        searchInput.addEventListener('input', (e) => {
            this.handleSearchInput(e.target.value);
        });

        searchInput.addEventListener('keydown', (e) => {
            this.handleKeyNavigation(e);
        });

        searchInput.addEventListener('focus', () => {
            this.showSuggestions();
        });

        searchInput.addEventListener('blur', () => {
            setTimeout(() => this.hideSuggestions(), 200);
        });

        // Search button
        document.querySelector('.search-btn').addEventListener('click', () => {
            this.performSearch();
        });
    }

    handleSearchInput(query) {
        this.currentQuery = query;
        
        if (query.length < 2) {
            this.hideSuggestions();
            return;
        }

        this.generateSuggestions(query);
        this.showSuggestions();
    }

    generateSuggestions(query) {
        const suggestions = [];
        const queryLower = query.toLowerCase();

        // Search in test case data
        this.searchIndex.forEach(item => {
            const searchText = item.searchableText;
            if (searchText.includes(queryLower)) {
                suggestions.push({
                    text: this.highlightMatch(item.data['Test Case ID'] || item.data['TC ID'] || `Item ${item.id}`),
                    type: 'Test Case',
                    data: item,
                    originalText: item.data['Test Case ID'] || item.data['TC ID'] || `Item ${item.id}`
                });
            }
        });

        // Add common search terms
        const commonTerms = [
            'Critical', 'High', 'Medium', 'Low',
            'Passed', 'Failed', 'Pending', 'Blocked',
            'Smoke', 'Sanity', 'Regression', 'FMEA',
            'Login', 'Dashboard', 'Reports', 'Settings'
        ];

        commonTerms.forEach(term => {
            if (term.toLowerCase().includes(queryLower)) {
                suggestions.push({
                    text: this.highlightMatch(term),
                    type: 'Filter',
                    data: { term },
                    originalText: term
                });
            }
        });

        // Add search history
        this.searchHistory.forEach(historyItem => {
            if (historyItem.toLowerCase().includes(queryLower)) {
                suggestions.push({
                    text: this.highlightMatch(historyItem),
                    type: 'History',
                    data: { term: historyItem },
                    originalText: historyItem
                });
            }
        });

        this.suggestions = suggestions.slice(0, 10); // Limit to 10 suggestions
    }

    highlightMatch(text) {
        if (!this.currentQuery) return text;
        
        const regex = new RegExp(`(${this.currentQuery})`, 'gi');
        return text.replace(regex, '<span class="suggestion-highlight">$1</span>');
    }

    showSuggestions() {
        const container = document.getElementById('searchSuggestions');
        if (!container) return;

        if (this.suggestions.length === 0) {
            container.style.display = 'none';
            return;
        }

        container.innerHTML = this.suggestions.map((suggestion, index) => `
            <div class="suggestion-item ${index === 0 ? 'active' : ''}" 
                 data-index="${index}"
                 onclick="advancedSearch.selectSuggestion(${index})">
                <span class="suggestion-text">${suggestion.text}</span>
                <span class="suggestion-type">${suggestion.type}</span>
            </div>
        `).join('');

        container.style.display = 'block';
    }

    hideSuggestions() {
        const container = document.getElementById('searchSuggestions');
        if (container) {
            container.style.display = 'none';
        }
    }

    selectSuggestion(index) {
        const suggestion = this.suggestions[index];
        if (suggestion) {
            document.getElementById('advancedSearchInput').value = suggestion.originalText;
            this.addToSearchHistory(suggestion.originalText);
            this.hideSuggestions();
            this.performSearch();
        }
    }

    handleKeyNavigation(e) {
        const container = document.getElementById('searchSuggestions');
        if (!container || container.style.display === 'none') return;

        const items = container.querySelectorAll('.suggestion-item');
        const activeItem = container.querySelector('.suggestion-item.active');
        let activeIndex = -1;

        if (activeItem) {
            activeIndex = parseInt(activeItem.dataset.index);
        }

        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                activeIndex = Math.min(activeIndex + 1, items.length - 1);
                this.setActiveSuggestion(activeIndex);
                break;
            case 'ArrowUp':
                e.preventDefault();
                activeIndex = Math.max(activeIndex - 1, 0);
                this.setActiveSuggestion(activeIndex);
                break;
            case 'Enter':
                e.preventDefault();
                if (activeIndex >= 0) {
                    this.selectSuggestion(activeIndex);
                } else {
                    this.performSearch();
                }
                break;
            case 'Escape':
                this.hideSuggestions();
                break;
        }
    }

    setActiveSuggestion(index) {
        const items = document.querySelectorAll('.suggestion-item');
        items.forEach((item, i) => {
            item.classList.toggle('active', i === index);
        });
    }

    performSearch() {
        const query = document.getElementById('advancedSearchInput').value;
        const filters = this.getActiveFilters();
        
        this.addToSearchHistory(query);
        
        // Perform search with filters
        const results = this.searchWithFilters(query, filters);
        this.displaySearchResults(results);
        this.updateSearchStats(results.length);
    }

    getActiveFilters() {
        return {
            priority: document.getElementById('filterPriority').value,
            status: document.getElementById('filterStatus').value,
            app: document.getElementById('filterApp').value,
            type: document.getElementById('filterType').value,
            dateFrom: document.getElementById('filterDateFrom').value,
            dateTo: document.getElementById('filterDateTo').value,
            exactMatch: document.getElementById('exactMatch').checked,
            caseSensitive: document.getElementById('caseSensitive').checked
        };
    }

    searchWithFilters(query, filters) {
        let results = this.searchIndex;

        // Text search
        if (query) {
            const queryLower = filters.caseSensitive ? query : query.toLowerCase();
            results = results.filter(item => {
                const searchText = filters.caseSensitive ? item.searchableText : item.searchableText.toLowerCase();
                return filters.exactMatch ? 
                    searchText === queryLower : 
                    searchText.includes(queryLower);
            });
        }

        // Apply filters
        if (filters.priority) {
            results = results.filter(item => item.data.Priority === filters.priority);
        }
        if (filters.status) {
            results = results.filter(item => item.data.Status === filters.status);
        }
        if (filters.app) {
            results = results.filter(item => item.data.App === filters.app);
        }
        if (filters.type) {
            results = results.filter(item => item.data['Test Type'] === filters.type);
        }

        return results;
    }

    displaySearchResults(results) {
        // Highlight matching rows in the table
        const table = document.querySelector('table tbody');
        if (!table) return;

        // Clear previous highlights
        table.querySelectorAll('tr').forEach(row => {
            row.classList.remove('search-highlight');
            row.style.display = '';
        });

        // Highlight matching rows
        results.forEach(result => {
            const row = table.querySelector(`tr:nth-child(${result.id + 1})`);
            if (row) {
                row.classList.add('search-highlight');
            }
        });

        // Hide non-matching rows if there are results
        if (results.length > 0) {
            table.querySelectorAll('tr').forEach((row, index) => {
                const isMatch = results.some(result => result.id === index);
                row.style.display = isMatch ? '' : 'none';
            });
        }
    }

    updateSearchStats(count) {
        // Create or update search stats display
        let statsElement = document.querySelector('.search-stats');
        if (!statsElement) {
            statsElement = document.createElement('div');
            statsElement.className = 'search-stats';
            document.querySelector('.advanced-search-container').appendChild(statsElement);
        }

        statsElement.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <i class="fas fa-search me-2"></i>
                    <strong>${count}</strong> results found
                </div>
                <div>
                    <button class="btn btn-sm btn-outline-light" onclick="advancedSearch.clearSearch()">
                        <i class="fas fa-times me-1"></i>Clear
                    </button>
                </div>
            </div>
        `;
    }

    clearSearch() {
        document.getElementById('advancedSearchInput').value = '';
        this.hideSuggestions();
        
        // Show all rows
        const table = document.querySelector('table tbody');
        if (table) {
            table.querySelectorAll('tr').forEach(row => {
                row.classList.remove('search-highlight');
                row.style.display = '';
            });
        }

        // Hide stats
        const statsElement = document.querySelector('.search-stats');
        if (statsElement) {
            statsElement.remove();
        }
    }

    clearFilters() {
        document.getElementById('filterPriority').value = '';
        document.getElementById('filterStatus').value = '';
        document.getElementById('filterApp').value = '';
        document.getElementById('filterType').value = '';
        document.getElementById('filterDateFrom').value = '';
        document.getElementById('filterDateTo').value = '';
        document.getElementById('exactMatch').checked = false;
        document.getElementById('caseSensitive').checked = false;
    }

    addToSearchHistory(query) {
        if (!query || query.length < 2) return;
        
        // Remove if already exists
        this.searchHistory = this.searchHistory.filter(item => item !== query);
        
        // Add to beginning
        this.searchHistory.unshift(query);
        
        // Keep only last 10
        this.searchHistory = this.searchHistory.slice(0, 10);
        
        // Save to localStorage
        localStorage.setItem('searchHistory', JSON.stringify(this.searchHistory));
    }

    loadSearchHistory() {
        // Populate search history in suggestions if needed
        // This is handled in generateSuggestions method
    }

    saveSearch() {
        const query = document.getElementById('advancedSearchInput').value;
        const filters = this.getActiveFilters();
        
        if (!query && Object.values(filters).every(v => !v)) {
            alert('Please enter a search query or set filters to save.');
            return;
        }

        const searchName = prompt('Enter a name for this saved search:');
        if (searchName) {
            const savedSearch = {
                name: searchName,
                query: query,
                filters: filters,
                date: new Date().toISOString()
            };
            
            this.favoriteSearches.push(savedSearch);
            localStorage.setItem('favoriteSearches', JSON.stringify(this.favoriteSearches));
            
            alert('Search saved successfully!');
        }
    }
}

// Initialize advanced search when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    if (document.querySelector('table')) {
        window.advancedSearch = new AdvancedSearch();
    }
});
