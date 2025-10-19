

let currentFilters = {};
let isLoading = false;

function getText(keyPath, defaultValue = '') {
    if (typeof window.getText === 'function') {
        return window.getText(keyPath, defaultValue);
    }
    return defaultValue;
}

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    initializeFilters();
});

function initializeApp() {
    console.log(getText('app.name', 'Validex') + ' Test Case Management System initialized');

    const mainContent = document.querySelector('main');
    if (mainContent) {
        mainContent.classList.add('fade-in');
    }

    initializeTooltips();

    initializeSearch();
}

function setupEventListeners() {
    
    const filterForm = document.getElementById('filterForm');
    if (filterForm) {
        filterForm.addEventListener('submit', handleFilterSubmit);
    }

    const clearFiltersBtn = document.querySelector('[href*="test_cases"]');
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', handleClearFilters);
    }

    const executeButtons = document.querySelectorAll('[href*="execute_test"]');
    executeButtons.forEach(button => {
        button.addEventListener('click', handleTestExecution);
    });

    const searchInput = document.getElementById('search');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(handleSearch, 300));
    }
}

function initializeFilters() {
    
    const urlParams = new URLSearchParams(window.location.search);

    const filterInputs = document.querySelectorAll('select[name], input[name]');
    filterInputs.forEach(input => {
        const value = urlParams.get(input.name);
        if (value) {
            input.value = value;
            currentFilters[input.name] = value;
        }
    });
}

function handleFilterSubmit(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const filters = {};

    for (let [key, value] of formData.entries()) {
        if (value.trim() !== '') {
            filters[key] = value.trim();
        }
    }

    updateURLWithFilters(filters);

    showLoadingState();

    window.location.href = buildFilterURL(filters);
}

function handleClearFilters(event) {
    event.preventDefault();

    const filterInputs = document.querySelectorAll('select[name], input[name]');
    filterInputs.forEach(input => {
        input.value = '';
    });

    currentFilters = {};

    window.location.href = window.location.pathname;
}

function handleTestExecution(event) {
    const testId = event.target.closest('a').href.split('/').pop();

    if (confirm(getText('javascript.execute_confirm', 'Execute test case') + ` ${testId}?`)) {
        
        const button = event.target.closest('button, a');
        if (button) {
            const originalText = button.innerHTML;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> ' + getText('javascript.executing', 'Executing...');
            button.disabled = true;

            setTimeout(() => {
                button.innerHTML = originalText;
                button.disabled = false;
            }, 2000);
        }
    }
}

function handleSearch(event) {
    const searchTerm = event.target.value.trim();
    
    if (searchTerm.length >= 2) {
        
        performLiveSearch(searchTerm);
    } else if (searchTerm.length === 0) {
        
        clearSearchResults();
    }
}

function performLiveSearch(searchTerm) {
    
    console.log(getText('javascript.searching_for', 'Searching for:'), searchTerm);

    highlightSearchResults(searchTerm);
}

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

function clearSearchResults() {
    const tableRows = document.querySelectorAll('tbody tr');
    tableRows.forEach(row => {
        row.style.backgroundColor = '';
        row.classList.remove('search-highlight');
    });
}

function initializeTooltips() {
    
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

function initializeSearch() {
    
    const searchInput = document.getElementById('search');
    if (searchInput) {
        
        searchInput.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        searchInput.addEventListener('blur', function() {
            this.parentElement.classList.remove('focused');
        });
    }
}

function showLoadingState() {
    const mainContent = document.querySelector('main');
    if (mainContent) {
        mainContent.style.opacity = '0.6';
        mainContent.style.pointerEvents = 'none';
    }

    const loadingSpinner = document.createElement('div');
    loadingSpinner.id = 'loading-spinner';
    loadingSpinner.className = 'position-fixed top-50 start-50 translate-middle';
    loadingSpinner.innerHTML = '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">' + getText('common.loading', 'Loading...') + '</span></div>';
    document.body.appendChild(loadingSpinner);
}

function hideLoadingState() {
    const mainContent = document.querySelector('main');
    if (mainContent) {
        mainContent.style.opacity = '1';
        mainContent.style.pointerEvents = 'auto';
    }

    const loadingSpinner = document.getElementById('loading-spinner');
    if (loadingSpinner) {
        loadingSpinner.remove();
    }
}

function updateURLWithFilters(filters) {
    const url = new URL(window.location);

    const filterParams = ['search', 'file', 'feature', 'status', 'priority', 'app_name', 'test_type', 'directory_structure'];
    filterParams.forEach(param => {
        url.searchParams.delete(param);
    });

    Object.keys(filters).forEach(key => {
        if (filters[key]) {
            url.searchParams.set(key, filters[key]);
        }
    });

    window.history.pushState({}, '', url);
}

function buildFilterURL(filters) {
    const url = new URL(window.location);

    const filterParams = ['search', 'file', 'feature', 'status', 'priority', 'app_name', 'test_type', 'directory_structure'];
    filterParams.forEach(param => {
        url.searchParams.delete(param);
    });

    Object.keys(filters).forEach(key => {
        if (filters[key]) {
            url.searchParams.set(key, filters[key]);
        }
    });
    
    return url.toString();
}

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

function formatStatusBadge(status) {
    const statusMap = {
        'Passed': 'badge-passed',
        'Failed': 'badge-failed',
        'Pending': 'badge-pending',
        'Running': 'badge-running'
    };
    
    return statusMap[status] || 'badge-pending';
}

function formatPriorityBadge(priority) {
    const priorityMap = {
        'High': 'badge-priority-high',
        'Medium': 'badge-priority-medium',
        'Low': 'badge-priority-low'
    };
    
    return priorityMap[priority] || 'badge-priority-medium';
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);

    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}



window.ValidexApp = {
    showNotification,
    formatStatusBadge,
    formatPriorityBadge,
    showLoadingState,
    hideLoadingState
};

