/**
 * Main JavaScript for Validex Test Case Management System
 * 
 * Copyright 2025 Validex Project
 * 
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * 
 *     http://www.apache.org/licenses/LICENSE-2.0
 * 
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

// Global variables
let currentFilters = {};
let isLoading = false;

// Text configuration helper
function getText(keyPath, defaultValue = '') {
    if (typeof window.getText === 'function') {
        return window.getText(keyPath, defaultValue);
    }
    return defaultValue;
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    initializeFilters();
});

/**
 * Initialize the application
 */
function initializeApp() {
    console.log(getText('app.name', 'Validex') + ' Test Case Management System initialized');
    
    // Add fade-in animation to main content
    const mainContent = document.querySelector('main');
    if (mainContent) {
        mainContent.classList.add('fade-in');
    }
    
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize search functionality
    initializeSearch();
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Filter form submission
    const filterForm = document.getElementById('filterForm');
    if (filterForm) {
        filterForm.addEventListener('submit', handleFilterSubmit);
    }
    
    // Clear filters button
    const clearFiltersBtn = document.querySelector('[href*="test_cases"]');
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', handleClearFilters);
    }
    
    // Test case execution buttons
    const executeButtons = document.querySelectorAll('[href*="execute_test"]');
    executeButtons.forEach(button => {
        button.addEventListener('click', handleTestExecution);
    });
    
    // Search input
    const searchInput = document.getElementById('search');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(handleSearch, 300));
    }
}

/**
 * Initialize filters
 */
function initializeFilters() {
    // Get current filter values from URL
    const urlParams = new URLSearchParams(window.location.search);
    
    // Populate filter inputs
    const filterInputs = document.querySelectorAll('select[name], input[name]');
    filterInputs.forEach(input => {
        const value = urlParams.get(input.name);
        if (value) {
            input.value = value;
            currentFilters[input.name] = value;
        }
    });
}

/**
 * Handle filter form submission
 */
function handleFilterSubmit(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const filters = {};
    
    // Collect filter values
    for (let [key, value] of formData.entries()) {
        if (value.trim() !== '') {
            filters[key] = value.trim();
        }
    }
    
    // Update URL with filters
    updateURLWithFilters(filters);
    
    // Show loading state
    showLoadingState();
    
    // Reload page with new filters
    window.location.href = buildFilterURL(filters);
}

/**
 * Handle clear filters
 */
function handleClearFilters(event) {
    event.preventDefault();
    
    // Clear all filter inputs
    const filterInputs = document.querySelectorAll('select[name], input[name]');
    filterInputs.forEach(input => {
        input.value = '';
    });
    
    // Clear current filters
    currentFilters = {};
    
    // Redirect to clean URL
    window.location.href = window.location.pathname;
}

/**
 * Handle test execution
 */
function handleTestExecution(event) {
    const testId = event.target.closest('a').href.split('/').pop();
    
    // Show confirmation dialog
    if (confirm(getText('javascript.execute_confirm', 'Execute test case') + ` ${testId}?`)) {
        // Add loading state to button
        const button = event.target.closest('button, a');
        if (button) {
            const originalText = button.innerHTML;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> ' + getText('javascript.executing', 'Executing...');
            button.disabled = true;
            
            // Re-enable after 2 seconds (simulate execution)
            setTimeout(() => {
                button.innerHTML = originalText;
                button.disabled = false;
            }, 2000);
        }
    }
}

/**
 * Handle search input
 */
function handleSearch(event) {
    const searchTerm = event.target.value.trim();
    
    if (searchTerm.length >= 2) {
        // Perform live search
        performLiveSearch(searchTerm);
    } else if (searchTerm.length === 0) {
        // Clear search results
        clearSearchResults();
    }
}

/**
 * Perform live search
 */
function performLiveSearch(searchTerm) {
    // This would typically make an AJAX request to the server
    console.log(getText('javascript.searching_for', 'Searching for:'), searchTerm);
    
    // For now, just highlight matching rows
    highlightSearchResults(searchTerm);
}

/**
 * Highlight search results
 */
function highlightSearchResults(searchTerm) {
    const tableRows = document.querySelectorAll('tbody tr');
    const regex = new RegExp(searchTerm, 'gi');
    
    tableRows.forEach(row => {
        const text = row.textContent;
        if (regex.test(text)) {
            row.style.backgroundColor = '#fff3cd';
            row.classList.add('search-highlight');
        } else {
            row.style.backgroundColor = '';
            row.classList.remove('search-highlight');
        }
    });
}

/**
 * Clear search results
 */
function clearSearchResults() {
    const tableRows = document.querySelectorAll('tbody tr');
    tableRows.forEach(row => {
        row.style.backgroundColor = '';
        row.classList.remove('search-highlight');
    });
}

/**
 * Initialize tooltips
 */
function initializeTooltips() {
    // Initialize Bootstrap tooltips if available
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

/**
 * Initialize search functionality
 */
function initializeSearch() {
    // Add search suggestions if needed
    const searchInput = document.getElementById('search');
    if (searchInput) {
        // Add search input enhancements
        searchInput.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        searchInput.addEventListener('blur', function() {
            this.parentElement.classList.remove('focused');
        });
    }
}

/**
 * Show loading state
 */
function showLoadingState() {
    const mainContent = document.querySelector('main');
    if (mainContent) {
        mainContent.style.opacity = '0.6';
        mainContent.style.pointerEvents = 'none';
    }
    
    // Show loading spinner
    const loadingSpinner = document.createElement('div');
    loadingSpinner.id = 'loading-spinner';
    loadingSpinner.className = 'position-fixed top-50 start-50 translate-middle';
    loadingSpinner.innerHTML = '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">' + getText('common.loading', 'Loading...') + '</span></div>';
    document.body.appendChild(loadingSpinner);
}

/**
 * Hide loading state
 */
function hideLoadingState() {
    const mainContent = document.querySelector('main');
    if (mainContent) {
        mainContent.style.opacity = '1';
        mainContent.style.pointerEvents = 'auto';
    }
    
    // Remove loading spinner
    const loadingSpinner = document.getElementById('loading-spinner');
    if (loadingSpinner) {
        loadingSpinner.remove();
    }
}

/**
 * Update URL with filters
 */
function updateURLWithFilters(filters) {
    const url = new URL(window.location);
    
    // Clear existing filter parameters
    const filterParams = ['search', 'file', 'feature', 'status', 'priority', 'app_name', 'test_type', 'directory_structure'];
    filterParams.forEach(param => {
        url.searchParams.delete(param);
    });
    
    // Add new filter parameters
    Object.keys(filters).forEach(key => {
        if (filters[key]) {
            url.searchParams.set(key, filters[key]);
        }
    });
    
    // Update URL without reloading
    window.history.pushState({}, '', url);
}

/**
 * Build filter URL
 */
function buildFilterURL(filters) {
    const url = new URL(window.location);
    
    // Clear existing filter parameters
    const filterParams = ['search', 'file', 'feature', 'status', 'priority', 'app_name', 'test_type', 'directory_structure'];
    filterParams.forEach(param => {
        url.searchParams.delete(param);
    });
    
    // Add new filter parameters
    Object.keys(filters).forEach(key => {
        if (filters[key]) {
            url.searchParams.set(key, filters[key]);
        }
    });
    
    return url.toString();
}

/**
 * Debounce function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Format status badge
 */
function formatStatusBadge(status) {
    const statusMap = {
        'Passed': 'badge-passed',
        'Failed': 'badge-failed',
        'Pending': 'badge-pending',
        'Running': 'badge-running'
    };
    
    return statusMap[status] || 'badge-pending';
}

/**
 * Format priority badge
 */
function formatPriorityBadge(priority) {
    const priorityMap = {
        'High': 'badge-priority-high',
        'Medium': 'badge-priority-medium',
        'Low': 'badge-priority-low'
    };
    
    return priorityMap[priority] || 'badge-priority-medium';
}

/**
 * Utility function to show notifications
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

/**
 * Export functions for global use
 */
window.ValidexApp = {
    showNotification,
    formatStatusBadge,
    formatPriorityBadge,
    showLoadingState,
    hideLoadingState
};



