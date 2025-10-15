// Modern Multi-Select Implementation with Search and Chips
class ModernMultiSelect {
    constructor(container) {
        console.log(`🎯 ModernMultiSelect constructor called for:`, container.dataset.field);
        console.log(`📍 Container element:`, container);
        
        this.container = container;
        this.input = container.querySelector('.multiselect-input');
        this.searchInput = container.querySelector('.multiselect-search');
        this.dropdown = container.querySelector('.multiselect-dropdown');
        this.options = container.querySelectorAll('.multiselect-option');
        this.hiddenSelect = container.querySelector('select[name]');
        this.selectedValues = new Set();
        this.fieldName = container.dataset.field;
        
        console.log(`📋 Found ${this.options.length} options for ${this.fieldName}`);
        console.log(`🔍 Input element:`, this.input);
        console.log(`🔍 Dropdown element:`, this.dropdown);
        
        this.init();
    }
    
    init() {
        this.loadInitialValues();
        this.bindEvents();
        this.updateDisplay();
    }
    
    loadInitialValues() {
        this.options.forEach(option => {
            const checkbox = option.querySelector('input[type="checkbox"]');
            if (checkbox) {
                console.log(`Found checkbox for ${this.fieldName}:`, checkbox.value, checkbox.checked);
                if (checkbox.checked) {
                    this.selectedValues.add(checkbox.value);
                }
            } else {
                console.log(`No checkbox found in option for ${this.fieldName}:`, option);
            }
        });
    }
    
    bindEvents() {
        // Input click to toggle dropdown
        this.input.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggle();
        });
        
        // Search functionality
        this.searchInput.addEventListener('input', (e) => {
            this.filterOptions(e.target.value);
        });
        
        // Option clicks - handle existing checkboxes
        this.options.forEach(option => {
            option.addEventListener('click', (e) => {
                e.stopPropagation();
                const checkbox = option.querySelector('input[type="checkbox"]');
                if (checkbox) {
                    // Toggle the checkbox
                    checkbox.checked = !checkbox.checked;
                    this.toggleOption(checkbox.value, checkbox.checked);
                }
            });
            
            // Also handle direct checkbox clicks
            const checkbox = option.querySelector('input[type="checkbox"]');
            if (checkbox) {
                checkbox.addEventListener('change', (e) => {
                    e.stopPropagation();
                    this.toggleOption(checkbox.value, checkbox.checked);
                });
            }
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', () => {
            this.close();
        });
        
        // Prevent dropdown from closing when clicking inside
        this.dropdown.addEventListener('click', (e) => {
            e.stopPropagation();
        });
    }
    
    toggle() {
        if (this.container.classList.contains('open')) {
            this.close();
        } else {
            this.open();
        }
    }
    
    open() {
        this.container.classList.add('open');
        this.searchInput.focus();
    }
    
    close() {
        this.container.classList.remove('open');
        this.searchInput.value = '';
        this.filterOptions('');
    }
    
    filterOptions(searchTerm) {
        const term = searchTerm.toLowerCase();
        this.options.forEach(option => {
            const label = option.querySelector('label').textContent.toLowerCase();
            if (label.includes(term)) {
                option.classList.remove('hidden');
            } else {
                option.classList.add('hidden');
            }
        });
    }
    
    toggleOption(value, checked) {
        if (checked) {
            this.selectedValues.add(value);
        } else {
            this.selectedValues.delete(value);
        }
        this.updateDisplay();
        this.updateHiddenSelect();
    }
    
    updateDisplay() {
        const chipsContainer = this.input.querySelector('.selected-chips');
        chipsContainer.innerHTML = '';
        
        if (this.selectedValues.size === 0) {
            this.searchInput.placeholder = `Search ${this.fieldName}...`;
        } else {
            this.selectedValues.forEach(value => {
                const chip = document.createElement('div');
                chip.className = 'chip';
                chip.innerHTML = `
                    ${value}
                    <button type="button" class="chip-remove" data-value="${value}">&times;</button>
                `;
                
                // Add remove functionality
                chip.querySelector('.chip-remove').addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.removeValue(value);
                });
                
                chipsContainer.appendChild(chip);
            });
            
            this.searchInput.placeholder = '';
        }
    }
    
    removeValue(value) {
        this.selectedValues.delete(value);
        
        // Update checkbox
        const option = this.container.querySelector(`[data-value="${value}"]`);
        if (option) {
            const checkbox = option.querySelector('input[type="checkbox"]');
            checkbox.checked = false;
        }
        
        this.updateDisplay();
        this.updateHiddenSelect();
    }
    
    updateHiddenSelect() {
        // Clear all options
        this.hiddenSelect.querySelectorAll('option').forEach(option => {
            option.selected = false;
        });
        
        // Select current values
        this.selectedValues.forEach(value => {
            const option = this.hiddenSelect.querySelector(`option[value="${value}"]`);
            if (option) {
                option.selected = true;
            }
        });
    }
}

// Multi-Select Dropdown Implementation
class MultiSelectDropdown {
    constructor(element) {
        this.element = element;
        this.selectedValues = new Set();
        this.isOpen = false;
        this.storageKey = `multiselect_${element.id}`;
        
        this.init();
    }
    
    init() {
        this.createDropdown();
        this.loadFromStorage();
        this.bindEvents();
        
        // Store reference on element
        this.element.multiselectInstance = this;
    }
    
    createDropdown() {
        const container = document.createElement('div');
        container.className = 'multiselect-container';
        
        const input = document.createElement('div');
        input.className = 'multiselect-input';
        input.innerHTML = `
            <div class="multiselect-placeholder">Select options...</div>
            <div class="multiselect-arrow">▼</div>
        `;
        
        const dropdown = document.createElement('div');
        dropdown.className = 'multiselect-dropdown';
        
        container.appendChild(input);
        container.appendChild(dropdown);
        
        this.input = input;
        this.dropdown = dropdown;
        
        this.element.style.display = 'none';
        this.element.parentNode.insertBefore(container, this.element);
        
        // Load initial values
        this.element.querySelectorAll('option').forEach(option => {
            if (option.value && option.selected) {
                this.selectedValues.add(option.value);
            }
        });
        
        this.renderOptions();
        this.updateDisplay();
    }
    
    saveToStorage() {
        try {
            const values = Array.from(this.selectedValues);
            localStorage.setItem(this.storageKey, JSON.stringify(values));
        } catch (e) {
            console.warn('Could not save multiselect values:', e);
        }
    }
    
    loadFromStorage() {
        try {
            const saved = localStorage.getItem(this.storageKey);
            return saved ? JSON.parse(saved) : [];
        } catch (e) {
            return [];
        }
    }
    
    renderOptions() {
        const options = this.element.querySelectorAll('option');
        let html = '';
        
        // Select All option
        html += `
            <div class="multiselect-option" data-value="__select_all__" style="padding: 8px 12px; border-bottom: 1px solid #e9ecef;">
                <input type="checkbox" id="select_all_${this.element.id}" ${this.areAllOptionsSelected() ? 'checked' : ''}>
                <label for="select_all_${this.element.id}" style="margin-left: 8px; cursor: pointer;">Select all</label>
            </div>
        `;
        
        // Clear All option
        if (this.selectedValues.size > 0) {
            html += `
                <div class="multiselect-option" data-value="__clear_all__" style="padding: 8px 12px; border-bottom: 1px solid #e9ecef; background: #f8f9fa;">
                    <button type="button" style="background: #dc3545; color: white; border: none; padding: 4px 8px; border-radius: 3px; cursor: pointer; font-size: 12px;">
                        Clear All
                    </button>
                </div>
            `;
        }
        
        // Options
        options.forEach(option => {
            if (option.value) {
                const isSelected = this.selectedValues.has(option.value);
                html += `
                    <div class="multiselect-option" data-value="${option.value}" style="padding: 8px 12px; cursor: pointer; ${isSelected ? 'background: #e3f2fd;' : ''}">
                        <input type="checkbox" id="${option.value}_${this.element.id}" ${isSelected ? 'checked' : ''}>
                        <label for="${option.value}_${this.element.id}" style="margin-left: 8px; cursor: pointer;">${option.textContent}</label>
                    </div>
                `;
            }
        });
        
        this.dropdown.innerHTML = html;
        
        // Bind click events
        this.dropdown.addEventListener('click', (e) => {
            const option = e.target.closest('.multiselect-option');
            if (option) {
                const value = option.dataset.value;
                const checkbox = option.querySelector('input[type="checkbox"]');
                
                if (value === '__select_all__') {
                    this.toggleSelectAll();
                } else if (value === '__clear_all__') {
                    this.clearAll();
                } else {
                    this.toggleOption(value, checkbox);
                }
            }
        });
    }
    
    toggle() {
        this.isOpen = !this.isOpen;
        this.dropdown.style.display = this.isOpen ? 'block' : 'none';
        this.input.querySelector('.multiselect-arrow').style.transform = this.isOpen ? 'rotate(180deg)' : 'rotate(0deg)';
    }
    
    close() {
        this.isOpen = false;
        this.dropdown.style.display = 'none';
        this.input.querySelector('.multiselect-arrow').style.transform = 'rotate(0deg)';
    }
    
    toggleOption(value, checkbox) {
        if (this.selectedValues.has(value)) {
            this.selectedValues.delete(value);
            checkbox.checked = false;
        } else {
            this.selectedValues.add(value);
            checkbox.checked = true;
        }
        
        this.updateDisplay();
        this.updateOriginalSelect();
        this.renderOptions();
        this.saveToStorage();
    }
    
    toggleSelectAll() {
        const options = this.element.querySelectorAll('option');
        if (this.areAllOptionsSelected()) {
            options.forEach(option => {
                if (option.value) {
                    this.selectedValues.delete(option.value);
                }
            });
        } else {
            options.forEach(option => {
                if (option.value) {
                    this.selectedValues.add(option.value);
                }
            });
        }
        
        this.updateDisplay();
        this.updateOriginalSelect();
        this.renderOptions();
        this.saveToStorage();
    }
    
    clearAll() {
        this.selectedValues.clear();
        this.updateDisplay();
        this.updateOriginalSelect();
        this.renderOptions();
        this.saveToStorage();
    }
    
    areAllOptionsSelected() {
        const options = this.element.querySelectorAll('option');
        const selectableOptions = Array.from(options).filter(option => option.value);
        return selectableOptions.length > 0 && selectableOptions.every(option => this.selectedValues.has(option.value));
    }
    
    updateDisplay() {
        const placeholder = this.input.querySelector('.multiselect-placeholder');
        
        if (this.selectedValues.size === 0) {
            placeholder.textContent = 'Select options...';
        } else if (this.selectedValues.size === 1) {
            const selectedOption = this.element.querySelector(`option[value="${Array.from(this.selectedValues)[0]}"]`);
            placeholder.textContent = selectedOption ? selectedOption.textContent : '1 selected';
        } else if (this.selectedValues.size <= 3) {
            const selectedTexts = Array.from(this.selectedValues).map(value => {
                const option = this.element.querySelector(`option[value="${value}"]`);
                return option ? option.textContent : value;
            });
            placeholder.textContent = selectedTexts.join(', ');
        } else {
            placeholder.textContent = `${this.selectedValues.size} selected`;
        }
    }
    
    updateOriginalSelect() {
        const options = this.element.querySelectorAll('option');
        options.forEach(option => {
            option.selected = this.selectedValues.has(option.value);
        });
        this.element.dispatchEvent(new Event('change', { bubbles: true }));
    }
}

// Clear all filters function
function clearAllFilters() {
    const containers = document.querySelectorAll('.multiselect-container');
    containers.forEach(container => {
        const multiselect = container.modernMultiSelect;
        if (multiselect) {
            multiselect.selectedValues.clear();
            multiselect.updateDisplay();
            multiselect.updateHiddenSelect();
            
            // Clear checkboxes
            container.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
                checkbox.checked = false;
            });
        }
    });
    
    const searchInput = document.getElementById('search');
    if (searchInput) {
        searchInput.value = '';
    }
    
    window.location.href = window.location.pathname;
}

// Global flag to prevent multiple initializations
window.multiselectInitialized = false;

// Clear any existing multiselect instances before initialization
function clearExistingMultiselects() {
    const existingContainers = document.querySelectorAll('.multiselect-container');
    existingContainers.forEach(container => {
        // Remove any existing initialization markers
        container.removeAttribute('data-initialized');
        // Clear any existing multiselect instance
        if (container.modernMultiSelect) {
            delete container.modernMultiSelect;
        }
    });
    
    // Clear jQuery-based initialization markers
    if (typeof $ !== 'undefined') {
        $('select[multiple]').removeClass('smart-multiselect-initialized checkbox-multiselect-initialized tag-multiselect-initialized');
        
        // Destroy any existing Select2 instances
        $('select[multiple]').each(function() {
            if ($(this).hasClass('select2-hidden-accessible')) {
                $(this).select2('destroy');
            }
        });
        
        // Remove any existing checkbox containers
        $('.checkbox-multiselect-container').remove();
        
        // Show hidden select elements
        $('select[multiple]').show();
    }
}

// Initialize all multi-select containers
document.addEventListener('DOMContentLoaded', function() {
    if (window.multiselectInitialized) {
        console.log('⚠️ Multiselect already initialized, skipping...');
        return;
    }
    
    console.log('🚀 DOMContentLoaded: Starting initialization...');
    
    // Clear any existing instances first
    clearExistingMultiselects();
    
    // DISABLE ModernMultiSelect - use only smart multi-select
    console.log('📦 Skipping ModernMultiSelect initialization, using smart multi-select only');
    
    // Mark as initialized
    window.multiselectInitialized = true;
    
    // Initialize jQuery-dependent functionality
    if (typeof $ !== 'undefined') {
        $(document).ready(function() {
            setTimeout(function() {
                initializeSmartMultiSelect();
            }, 100);

            $(document).on('DOMNodeInserted', function(e) {
                if ($(e.target).find('select').length > 0) {
                    setTimeout(function() {
                        initializeSmartMultiSelect();
                    }, 50);
                }
            });
        });
    }
    
    // Double-check for any duplicate containers
    setTimeout(() => {
        const duplicateContainers = document.querySelectorAll('.multiselect-container[data-initialized="true"]');
        console.log(`🔍 Final check: ${duplicateContainers.length} initialized containers found`);
        
        // Check for duplicate elements
        const allMultiselectInputs = document.querySelectorAll('.multiselect-input');
        const allMultiselectDropdowns = document.querySelectorAll('.multiselect-dropdown');
        console.log(`🔍 Found ${allMultiselectInputs.length} multiselect inputs and ${allMultiselectDropdowns.length} dropdowns`);
        
        if (allMultiselectInputs.length > 0) {
            console.error('❌ DUPLICATE ELEMENTS DETECTED!');
            console.log('Expected: 0 Found:', allMultiselectInputs.length);
        }
    }, 1000);
    
    // Initialize multi-select dropdowns
    const multiselectElements = document.querySelectorAll('.multiselect');
    multiselectElements.forEach(element => {
        // Check if already initialized to prevent duplicates
        if (!element.hasAttribute('data-initialized')) {
            try {
                new MultiSelectDropdown(element);
                element.setAttribute('data-initialized', 'true');
            } catch (error) {
                console.error('Error initializing dropdown:', error);
                element.style.display = 'block';
                element.classList.remove('multiselect');
            }
        }
    });
    
    // Form submission handler
    const filterForm = document.getElementById('filterForm');
    if (filterForm) {
        filterForm.addEventListener('submit', function(e) {
            multiselectElements.forEach(element => {
                if (element.multiselectInstance) {
                    element.multiselectInstance.updateOriginalSelect();
                }
            });
        });
    }
    
    // Initialize dynamic dropdown functionality
    initializeDynamicDropdowns();
    
    // Initialize save filter functionality
    initializeSaveFilter();
    
    // Initialize load saved filters functionality
    initializeLoadSavedFilters();
    
    // Initialize column management functionality
    initializeColumnManagement();
    
    // Initialize dynamic filters functionality
    initializeDynamicFilters();
    
    // Initialize smart multi-select with delay
    setTimeout(function() {
        initializeSmartMultiSelect();
    }, 100);
    
    // Initialize jQuery-dependent functionality
    if (typeof $ !== 'undefined') {
        $(document).ready(function() {
            setTimeout(function() {
                initializeSmartMultiSelect();
            }, 100);

            $(document).on('DOMNodeInserted', function(e) {
                if ($(e.target).find('select').length > 0) {
                    setTimeout(function() {
                        initializeSmartMultiSelect();
                    }, 50);
                }
            });
        });
    }
    
    // Initialize view toggle functionality
    const viewGridBtn = document.getElementById('viewGrid');
    const viewTableBtn = document.getElementById('viewTable');
    const tableView = document.getElementById('tableView');
    const gridView = document.getElementById('gridView');
    
    if (viewGridBtn && viewTableBtn && tableView && gridView) {
        viewGridBtn.addEventListener('click', function() {
            tableView.style.display = 'none';
            gridView.style.display = 'block';
            viewGridBtn.classList.add('active');
            viewTableBtn.classList.remove('active');
        });
        
        viewTableBtn.addEventListener('click', function() {
            gridView.style.display = 'none';
            tableView.style.display = 'block';
            viewTableBtn.classList.add('active');
            viewGridBtn.classList.remove('active');
        });
    }

    // Initialize bulk selection functionality
    const selectAllCheckbox = document.getElementById('selectAll');
    const testCaseCheckboxes = document.querySelectorAll('.test-case-checkbox');
    const bulkActions = document.querySelector('.bulk-actions');
    const selectedCount = document.getElementById('selectedCount');
    
    if (selectAllCheckbox && testCaseCheckboxes.length > 0) {
        selectAllCheckbox.addEventListener('change', function() {
            testCaseCheckboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });
            updateBulkActions();
        });
        
        testCaseCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                updateBulkActions();
                updateSelectAllState();
            });
        });
    }
    
    function updateBulkActions() {
        const checkedBoxes = document.querySelectorAll('.test-case-checkbox:checked');
        if (checkedBoxes.length > 0) {
            if (bulkActions) bulkActions.style.display = 'block';
            if (selectedCount) selectedCount.textContent = checkedBoxes.length;
        } else {
            if (bulkActions) bulkActions.style.display = 'none';
        }
    }
    
    function updateSelectAllState() {
        const checkedBoxes = document.querySelectorAll('.test-case-checkbox:checked');
        const totalBoxes = testCaseCheckboxes.length;
        
        if (checkedBoxes.length === 0) {
            selectAllCheckbox.indeterminate = false;
            selectAllCheckbox.checked = false;
        } else if (checkedBoxes.length === totalBoxes) {
            selectAllCheckbox.indeterminate = false;
            selectAllCheckbox.checked = true;
        } else {
            selectAllCheckbox.indeterminate = true;
        }
    }

    const clearSelectionBtn = document.getElementById('clearSelection');
    if (clearSelectionBtn) {
        clearSelectionBtn.addEventListener('click', function() {
            testCaseCheckboxes.forEach(checkbox => {
                checkbox.checked = false;
            });
            selectAllCheckbox.checked = false;
            selectAllCheckbox.indeterminate = false;
            updateBulkActions();
        });
    }

    const bulkExecuteBtn = document.getElementById('bulkExecute');
    if (bulkExecuteBtn) {
        bulkExecuteBtn.addEventListener('click', function() {
            const checkedBoxes = document.querySelectorAll('.test-case-checkbox:checked');
            if (checkedBoxes.length > 0) {
                if (confirm(`Execute ${checkedBoxes.length} test cases?`)) {
                    console.log('Bulk execute:', Array.from(checkedBoxes).map(cb => cb.value));
                    alert('Bulk execution started!');
                }
            }
        });
    }

    // Initialize action buttons
    document.querySelectorAll('.execute-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const testId = this.getAttribute('data-id');
            showExecuteModal(testId);
        });
    });
    
    document.querySelectorAll('.view-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const testId = this.getAttribute('data-id');
            showTestCaseDetails(testId);
        });
    });
    
    document.querySelectorAll('.edit-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const testId = this.getAttribute('data-id');
            console.log('Edit test case:', testId);
            alert('Edit functionality coming soon!');
        });
    });

    const confirmExecuteBtn = document.getElementById('confirmExecute');
    if (confirmExecuteBtn) {
        confirmExecuteBtn.addEventListener('click', function() {
            const testId = this.getAttribute('data-test-id');
            const environment = document.getElementById('testEnvironment').value;
            const testData = document.getElementById('testData').value;
            const runInBackground = document.getElementById('runInBackground').checked;
            
            if (!environment) {
                alert('Please select a test environment');
                return;
            }

            console.log('Executing test:', {
                testId: testId,
                environment: environment,
                testData: testData,
                runInBackground: runInBackground
            });
            
            alert(`Test case ${testId} execution started in ${environment} environment!`);

            const executeModal = bootstrap.Modal.getInstance(document.getElementById('executeModal'));
            executeModal.hide();
        });
    }

    const executeFromModalBtn = document.getElementById('executeFromModal');
    if (executeFromModalBtn) {
        executeFromModalBtn.addEventListener('click', function() {
            const testCaseModal = bootstrap.Modal.getInstance(document.getElementById('testCaseModal'));
            testCaseModal.hide();

            setTimeout(() => {
                showExecuteModal('1'); 
            }, 300);
        });
    }

    const exportBtn = document.getElementById('exportBtn');
    if (exportBtn) {
        exportBtn.addEventListener('click', function(e) {
            const button = this;
            const originalText = button.innerHTML;

            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Exporting...';
            button.disabled = true;

            setTimeout(() => {
                button.innerHTML = originalText;
                button.disabled = false;
            }, 5000);
        });
    }
    
    // Initialize test suite functionality
    updateAvailableColumns();
    
    // Add event listeners for test suite form
    const releaseVersionInput = document.getElementById('releaseVersion');
    if (releaseVersionInput) {
        releaseVersionInput.addEventListener('input', updateExportButton);
    }
    
    // Listen for checkbox changes
    document.addEventListener('change', function(e) {
        if (e.target.classList.contains('test-case-checkbox')) {
            updateExportButton();
            updateSelectedTestCases();
        }
    });
    
    // Initialize selected test cases from localStorage
    loadSelectedTestCases();
    
    // Store filtered test cases on page load
    storeFilteredTestCases();
});

// Filter toggle functionality
function toggleFilters() {
    const content = document.getElementById('filterContent');
    const toggle = document.getElementById('filterToggle');
    const icon = toggle.querySelector('i');
    
    if (content.style.display === 'none') {
        content.style.display = 'block';
        icon.className = 'fas fa-chevron-up';
    } else {
        content.style.display = 'none';
        icon.className = 'fas fa-chevron-down';
    }
}

// Dynamic Dropdown Functionality
function initializeDynamicDropdowns() {
    const appSelect = document.getElementById('app');
    const testTypeSelect = document.getElementById('test_type');
    const prioritySelect = document.getElementById('priority');
    
    if (!appSelect || !testTypeSelect || !prioritySelect) {
        console.log('Dropdown elements not found');
        return;
    }
    
    // Add event listener to app dropdown
    appSelect.addEventListener('change', function() {
        updateDropdownOptions();
    });
    
    console.log('Dynamic dropdowns initialized');
}

function updateDropdownOptions() {
    const appSelect = document.getElementById('app');
    const testTypeSelect = document.getElementById('test_type');
    const prioritySelect = document.getElementById('priority');
    
    // Get selected apps
    const selectedApps = Array.from(appSelect.selectedOptions).map(option => option.value).filter(value => value !== '');
    
    console.log('Selected apps:', selectedApps);
    
    // Show loading state
    showDropdownLoading(testTypeSelect, 'Loading test types...');
    showDropdownLoading(prioritySelect, 'Loading priorities...');
    
    // Make API call to get updated options
    const params = new URLSearchParams();
    selectedApps.forEach(app => params.append('apps', app));
    
    fetch(`/api/filter-options?${params.toString()}`)
        .then(response => response.json())
        .then(data => {
            console.log('Filter options received:', data);
            updateDropdownOptionsFromData(data);
        })
        .catch(error => {
            console.error('Error fetching filter options:', error);
            // Fallback to original options
            restoreOriginalDropdownOptions();
        });
}

function showDropdownLoading(selectElement, loadingText) {
    // Store original options
    if (!selectElement.dataset.originalOptions) {
        selectElement.dataset.originalOptions = selectElement.innerHTML;
    }
    
    // Show loading state with spinner
    selectElement.innerHTML = `<option value=""><i class="fas fa-spinner fa-spin"></i> ${loadingText}</option>`;
    selectElement.disabled = true;
    
    // Add visual feedback
    selectElement.style.opacity = '0.7';
    selectElement.style.cursor = 'not-allowed';
}

function updateDropdownOptionsFromData(data) {
    const testTypeSelect = document.getElementById('test_type');
    const prioritySelect = document.getElementById('priority');
    
    // Update test types dropdown
    updateDropdown(testTypeSelect, data.test_types, 'All Test Types');
    
    // Update priorities dropdown
    updateDropdown(prioritySelect, data.priorities, 'All Priorities');
    
    // Re-enable dropdowns and restore visual state
    testTypeSelect.disabled = false;
    prioritySelect.disabled = false;
    testTypeSelect.style.opacity = '1';
    prioritySelect.style.opacity = '1';
    testTypeSelect.style.cursor = 'pointer';
    prioritySelect.style.cursor = 'pointer';
    
    // Show success message
    showDropdownUpdateMessage(`Updated options for ${data.test_types.length} test types and ${data.priorities.length} priorities`);
}

function updateDropdown(selectElement, options, defaultText) {
    // Clear current options
    selectElement.innerHTML = '';
    
    // Add default option
    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.textContent = defaultText;
    selectElement.appendChild(defaultOption);
    
    // Add new options
    options.forEach(option => {
        const optionElement = document.createElement('option');
        optionElement.value = option;
        optionElement.textContent = option;
        selectElement.appendChild(optionElement);
    });
    
    console.log(`Updated ${selectElement.id} with ${options.length} options`);
}

function restoreOriginalDropdownOptions() {
    const testTypeSelect = document.getElementById('test_type');
    const prioritySelect = document.getElementById('priority');
    
    if (testTypeSelect.dataset.originalOptions) {
        testTypeSelect.innerHTML = testTypeSelect.dataset.originalOptions;
        testTypeSelect.disabled = false;
        testTypeSelect.style.opacity = '1';
        testTypeSelect.style.cursor = 'pointer';
    }
    
    if (prioritySelect.dataset.originalOptions) {
        prioritySelect.innerHTML = prioritySelect.dataset.originalOptions;
        prioritySelect.disabled = false;
        prioritySelect.style.opacity = '1';
        prioritySelect.style.cursor = 'pointer';
    }
}

function showDropdownUpdateMessage(message) {
    // Create or update a temporary message element
    let messageElement = document.getElementById('dropdown-update-message');
    if (!messageElement) {
        messageElement = document.createElement('div');
        messageElement.id = 'dropdown-update-message';
        messageElement.className = 'alert alert-info alert-dismissible fade show position-fixed';
        messageElement.style.top = '20px';
        messageElement.style.right = '20px';
        messageElement.style.zIndex = '9999';
        messageElement.style.minWidth = '300px';
        
        const closeButton = document.createElement('button');
        closeButton.type = 'button';
        closeButton.className = 'btn-close';
        closeButton.setAttribute('data-bs-dismiss', 'alert');
        messageElement.appendChild(closeButton);
        
        document.body.appendChild(messageElement);
    }
    
    messageElement.innerHTML = `
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        <i class="fas fa-check-circle me-2"></i>${message}
    `;
    
    // Auto-hide after 3 seconds
    setTimeout(() => {
        if (messageElement && messageElement.parentNode) {
            messageElement.remove();
        }
    }, 3000);
}

// Save Filter Functionality
function initializeSaveFilter() {
    const saveFilterBtn = document.getElementById('saveFilterBtn');
    if (!saveFilterBtn) {
        console.log('Save filter button not found');
        return;
    }
    
    saveFilterBtn.addEventListener('click', function() {
        saveCurrentFilters();
    });
    
    console.log('Save filter functionality initialized');
}

function saveCurrentFilters() {
    const saveFilterBtn = document.getElementById('saveFilterBtn');
    
    // Show loading state
    const originalContent = saveFilterBtn.innerHTML;
    saveFilterBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    saveFilterBtn.disabled = true;
    
    // Collect current filter values
    const filters = {
        search: document.getElementById('search')?.value || '',
        apps: Array.from(document.getElementById('app')?.selectedOptions || []).map(option => option.value).filter(value => value !== ''),
        test_types: Array.from(document.getElementById('test_type')?.selectedOptions || []).map(option => option.value).filter(value => value !== ''),
        priorities: Array.from(document.getElementById('priority')?.selectedOptions || []).map(option => option.value).filter(value => value !== ''),
        sort: document.getElementById('sort')?.value || 'Test Case ID',
        order: document.getElementById('order')?.value || 'asc'
    };
    
    // Create a unique name for the saved filter
    const filterName = generateFilterName(filters);
    
    // Save to localStorage
    try {
        const savedFilters = JSON.parse(localStorage.getItem('savedFilters') || '{}');
        savedFilters[filterName] = {
            filters: filters,
            timestamp: new Date().toISOString(),
            name: filterName
        };
        localStorage.setItem('savedFilters', JSON.stringify(savedFilters));
        
        // Show success feedback
        showSaveFilterSuccess(filterName);
        
        // Update button to show saved state
        saveFilterBtn.innerHTML = '<i class="fas fa-check"></i>';
        saveFilterBtn.classList.remove('btn-outline-light');
        saveFilterBtn.classList.add('btn-success');
        
        // Reset button after 2 seconds
        setTimeout(() => {
            saveFilterBtn.innerHTML = originalContent;
            saveFilterBtn.disabled = false;
            saveFilterBtn.classList.remove('btn-success');
            saveFilterBtn.classList.add('btn-outline-light');
        }, 2000);
        
    } catch (error) {
        console.error('Error saving filters:', error);
        showSaveFilterError();
        
        // Reset button
        saveFilterBtn.innerHTML = originalContent;
        saveFilterBtn.disabled = false;
    }
}

function generateFilterName(filters) {
    const parts = [];
    
    if (filters.search) {
        parts.push(`Search: ${filters.search.substring(0, 20)}${filters.search.length > 20 ? '...' : ''}`);
    }
    
    if (filters.apps.length > 0) {
        parts.push(`Apps: ${filters.apps.join(', ')}`);
    }
    
    if (filters.test_types.length > 0) {
        parts.push(`Types: ${filters.test_types.join(', ')}`);
    }
    
    if (filters.priorities.length > 0) {
        parts.push(`Priority: ${filters.priorities.join(', ')}`);
    }
    
    if (parts.length === 0) {
        return `Default Filter - ${new Date().toLocaleString()}`;
    }
    
    return parts.join(' | ') + ` - ${new Date().toLocaleString()}`;
}

function showSaveFilterSuccess(filterName) {
    // Create success message
    let messageElement = document.getElementById('save-filter-message');
    if (!messageElement) {
        messageElement = document.createElement('div');
        messageElement.id = 'save-filter-message';
        messageElement.className = 'alert alert-success alert-dismissible fade show position-fixed';
        messageElement.style.top = '20px';
        messageElement.style.right = '20px';
        messageElement.style.zIndex = '9999';
        messageElement.style.minWidth = '400px';
        document.body.appendChild(messageElement);
    }
    
    messageElement.innerHTML = `
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        <i class="fas fa-bookmark me-2"></i>
        <strong>Filter Saved!</strong><br>
        <small>Saved as: "${filterName}"</small>
    `;
    
    // Auto-hide after 4 seconds
    setTimeout(() => {
        if (messageElement && messageElement.parentNode) {
            messageElement.remove();
        }
    }, 4000);
}

function showSaveFilterError() {
    // Create error message
    let messageElement = document.getElementById('save-filter-error');
    if (!messageElement) {
        messageElement = document.createElement('div');
        messageElement.id = 'save-filter-error';
        messageElement.className = 'alert alert-danger alert-dismissible fade show position-fixed';
        messageElement.style.top = '20px';
        messageElement.style.right = '20px';
        messageElement.style.zIndex = '9999';
        messageElement.style.minWidth = '300px';
        document.body.appendChild(messageElement);
    }
    
    messageElement.innerHTML = `
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        <i class="fas fa-exclamation-triangle me-2"></i>
        <strong>Error!</strong> Could not save filter.
    `;
    
    // Auto-hide after 3 seconds
    setTimeout(() => {
        if (messageElement && messageElement.parentNode) {
            messageElement.remove();
        }
    }, 3000);
}

// Load Saved Filters Functionality
function initializeLoadSavedFilters() {
    const loadFilterDropdown = document.getElementById('loadFilterDropdown');
    const savedFiltersList = document.getElementById('savedFiltersList');
    
    if (!loadFilterDropdown || !savedFiltersList) {
        console.log('Load saved filters elements not found');
        return;
    }
    
    // Load saved filters on page load
    loadSavedFiltersList();
    
    console.log('Load saved filters functionality initialized');
}

function loadSavedFiltersList() {
    const savedFiltersList = document.getElementById('savedFiltersList');
    if (!savedFiltersList) return;
    
    try {
        const savedFilters = JSON.parse(localStorage.getItem('savedFilters') || '{}');
        const filterNames = Object.keys(savedFilters);
        
        // Clear existing items
        savedFiltersList.innerHTML = '<li><h6 class="dropdown-header">Saved Filters</h6></li>';
        
        if (filterNames.length === 0) {
            savedFiltersList.innerHTML += '<li><span class="dropdown-item-text text-muted">No saved filters</span></li>';
            return;
        }
        
        // Sort by timestamp (newest first)
        const sortedFilters = filterNames.sort((a, b) => {
            return new Date(savedFilters[b].timestamp) - new Date(savedFilters[a].timestamp);
        });
        
        // Add each saved filter
        sortedFilters.forEach(filterName => {
            const filterData = savedFilters[filterName];
            const listItem = document.createElement('li');
            
            listItem.innerHTML = `
                <div class="dropdown-item d-flex justify-content-between align-items-center" style="cursor: pointer;">
                    <div class="flex-grow-1">
                        <div class="fw-bold">${filterName}</div>
                        <small class="text-muted">${new Date(filterData.timestamp).toLocaleString()}</small>
                    </div>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-primary btn-sm" onclick="loadSavedFilter('${filterName}')" title="Load filter">
                            <i class="fas fa-play"></i>
                        </button>
                        <button class="btn btn-outline-danger btn-sm" onclick="deleteSavedFilter('${filterName}')" title="Delete filter">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            `;
            
            savedFiltersList.appendChild(listItem);
        });
        
    } catch (error) {
        console.error('Error loading saved filters:', error);
        savedFiltersList.innerHTML = '<li><span class="dropdown-item-text text-danger">Error loading filters</span></li>';
    }
}

function loadSavedFilter(filterName) {
    try {
        const savedFilters = JSON.parse(localStorage.getItem('savedFilters') || '{}');
        const filterData = savedFilters[filterName];
        
        if (!filterData) {
            showLoadFilterError('Filter not found');
            return;
        }
        
        const filters = filterData.filters;
        
        // Apply the saved filters
        if (filters.search) {
            document.getElementById('search').value = filters.search;
        }
        
        if (filters.apps && filters.apps.length > 0) {
            const appSelect = document.getElementById('app');
            Array.from(appSelect.options).forEach(option => {
                option.selected = filters.apps.includes(option.value);
            });
        }
        
        if (filters.test_types && filters.test_types.length > 0) {
            const testTypeSelect = document.getElementById('test_type');
            Array.from(testTypeSelect.options).forEach(option => {
                option.selected = filters.test_types.includes(option.value);
            });
        }
        
        if (filters.priorities && filters.priorities.length > 0) {
            const prioritySelect = document.getElementById('priority');
            Array.from(prioritySelect.options).forEach(option => {
                option.selected = filters.priorities.includes(option.value);
            });
        }
        
        if (filters.sort) {
            document.getElementById('sort').value = filters.sort;
        }
        
        if (filters.order) {
            document.getElementById('order').value = filters.order;
        }
        
        // Show success message
        showLoadFilterSuccess(filterName);
        
        // Submit the form to apply filters
        document.getElementById('filterForm').submit();
        
    } catch (error) {
        console.error('Error loading filter:', error);
        showLoadFilterError('Error loading filter');
    }
}

function deleteSavedFilter(filterName) {
    if (!confirm(`Are you sure you want to delete the filter "${filterName}"?`)) {
        return;
    }
    
    try {
        const savedFilters = JSON.parse(localStorage.getItem('savedFilters') || '{}');
        delete savedFilters[filterName];
        localStorage.setItem('savedFilters', JSON.stringify(savedFilters));
        
        // Reload the list
        loadSavedFiltersList();
        
        // Show success message
        showDeleteFilterSuccess(filterName);
        
    } catch (error) {
        console.error('Error deleting filter:', error);
        showLoadFilterError('Error deleting filter');
    }
}

function showLoadFilterSuccess(filterName) {
    let messageElement = document.getElementById('load-filter-message');
    if (!messageElement) {
        messageElement = document.createElement('div');
        messageElement.id = 'load-filter-message';
        messageElement.className = 'alert alert-info alert-dismissible fade show position-fixed';
        messageElement.style.top = '20px';
        messageElement.style.right = '20px';
        messageElement.style.zIndex = '9999';
        messageElement.style.minWidth = '300px';
        document.body.appendChild(messageElement);
    }
    
    messageElement.innerHTML = `
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        <i class="fas fa-play me-2"></i>
        <strong>Filter Loaded!</strong><br>
        <small>Applied: "${filterName}"</small>
    `;
    
    setTimeout(() => {
        if (messageElement && messageElement.parentNode) {
            messageElement.remove();
        }
    }, 3000);
}

function showDeleteFilterSuccess(filterName) {
    let messageElement = document.getElementById('delete-filter-message');
    if (!messageElement) {
        messageElement = document.createElement('div');
        messageElement.id = 'delete-filter-message';
        messageElement.className = 'alert alert-warning alert-dismissible fade show position-fixed';
        messageElement.style.top = '20px';
        messageElement.style.right = '20px';
        messageElement.style.zIndex = '9999';
        messageElement.style.minWidth = '300px';
        document.body.appendChild(messageElement);
    }
    
    messageElement.innerHTML = `
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        <i class="fas fa-trash me-2"></i>
        <strong>Filter Deleted!</strong><br>
        <small>Removed: "${filterName}"</small>
    `;
    
    setTimeout(() => {
        if (messageElement && messageElement.parentNode) {
            messageElement.remove();
        }
    }, 3000);
}

function showLoadFilterError(message) {
    let messageElement = document.getElementById('load-filter-error');
    if (!messageElement) {
        messageElement = document.createElement('div');
        messageElement.id = 'load-filter-error';
        messageElement.className = 'alert alert-danger alert-dismissible fade show position-fixed';
        messageElement.style.top = '20px';
        messageElement.style.right = '20px';
        messageElement.style.zIndex = '9999';
        messageElement.style.minWidth = '300px';
        document.body.appendChild(messageElement);
    }
    
    messageElement.innerHTML = `
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        <i class="fas fa-exclamation-triangle me-2"></i>
        <strong>Error!</strong> ${message}
    `;
    
    setTimeout(() => {
        if (messageElement && messageElement.parentNode) {
            messageElement.remove();
        }
    }, 3000);
}

// Column Management Functionality
function initializeColumnManagement() {
    const columnManagerBtn = document.getElementById('columnManagerBtn');
    if (!columnManagerBtn) {
        console.log('Column manager button not found');
        return;
    }
    
    columnManagerBtn.addEventListener('click', function() {
        showColumnManagerModal();
    });
    
    // Load saved column preferences
    loadColumnPreferences();
    
    console.log('Column management functionality initialized');
}

function showColumnManagerModal() {
    // Create modal if it doesn't exist
    let modal = document.getElementById('columnManagerModal');
    if (!modal) {
        modal = createColumnManagerModal();
        document.body.appendChild(modal);
    }
    
    // Populate the modal with current column states
    populateColumnManagerModal();
    
    // Show the modal
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
}

function createColumnManagerModal() {
    const modal = document.createElement('div');
    modal.id = 'columnManagerModal';
    modal.className = 'modal fade';
    modal.setAttribute('tabindex', '-1');
    modal.setAttribute('aria-labelledby', 'columnManagerModalLabel');
    modal.setAttribute('aria-hidden', 'true');
    
    modal.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="columnManagerModalLabel">
                        <i class="fas fa-columns me-2"></i>Manage Table Columns
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <div class="mb-3">
                        <p class="text-muted">Select which columns to display in the table. You can also reorder columns by dragging them.</p>
                    </div>
                    <div class="row">
                        <div class="col-md-6">
                            <h6>Column Visibility</h6>
                            <div id="columnCheckboxes" class="list-group">
                                <!-- Column checkboxes will be populated here -->
                            </div>
                        </div>
                        <div class="col-md-6">
                            <h6>Column Order</h6>
                            <div id="columnOrder" class="list-group">
                                <!-- Column order will be populated here -->
                            </div>
                        </div>
                    </div>
                    <div class="mt-3">
                        <button type="button" class="btn btn-outline-secondary btn-sm" onclick="resetColumnPreferences()">
                            <i class="fas fa-undo me-1"></i>Reset to Default
                        </button>
                        <button type="button" class="btn btn-outline-primary btn-sm" onclick="showAllColumns()">
                            <i class="fas fa-eye me-1"></i>Show All
                        </button>
                        <button type="button" class="btn btn-outline-secondary btn-sm" onclick="hideAllColumns()">
                            <i class="fas fa-eye-slash me-1"></i>Hide All
                        </button>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary" onclick="applyColumnChanges()">
                        <i class="fas fa-check me-1"></i>Apply Changes
                    </button>
                </div>
            </div>
        </div>
    `;
    
    return modal;
}

function populateColumnManagerModal() {
    const columnCheckboxes = document.getElementById('columnCheckboxes');
    const columnOrder = document.getElementById('columnOrder');
    
    if (!columnCheckboxes || !columnOrder) return;
    
    // Define column configuration
    const columns = [
        { key: 'select', name: 'Select', required: true },
        { key: 'test_case_id', name: 'Test Case ID', required: true },
        { key: 'summary', name: 'Summary', required: false },
        { key: 'app', name: 'App', required: false },
        { key: 'test_type', name: 'Test Type', required: false },
        { key: 'feature', name: 'Feature', required: false },
        { key: 'status', name: 'Status', required: false },
        { key: 'priority', name: 'Priority', required: false },
        { key: 'source_file', name: 'Source File', required: false }
    ];
    
    // Get current column preferences
    const preferences = getColumnPreferences();
    
    // Clear existing content
    columnCheckboxes.innerHTML = '';
    columnOrder.innerHTML = '';
    
    // Populate checkboxes
    columns.forEach(column => {
        const isVisible = preferences.visible[column.key] !== false;
        const isRequired = column.required;
        
        const checkboxItem = document.createElement('div');
        checkboxItem.className = 'form-check';
        checkboxItem.innerHTML = `
            <input class="form-check-input" type="checkbox" 
                   id="col_${column.key}" 
                   data-column="${column.key}"
                   ${isVisible ? 'checked' : ''}
                   ${isRequired ? 'disabled' : ''}>
            <label class="form-check-label" for="col_${column.key}">
                ${column.name}
                ${isRequired ? '<small class="text-muted"> (Required)</small>' : ''}
            </label>
        `;
        columnCheckboxes.appendChild(checkboxItem);
    });
    
    // Populate order (only visible columns)
    const visibleColumns = columns.filter(col => preferences.visible[col.key] !== false);
    visibleColumns.forEach((column, index) => {
        const orderItem = document.createElement('div');
        orderItem.className = 'list-group-item d-flex justify-content-between align-items-center';
        orderItem.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="fas fa-grip-vertical text-muted me-2"></i>
                <span>${column.name}</span>
            </div>
            <small class="text-muted">${index + 1}</small>
        `;
        columnOrder.appendChild(orderItem);
    });
}

function getColumnPreferences() {
    const defaultPreferences = {
        visible: {
            select: true,
            test_case_id: true,
            summary: true,
            app: true,
            test_type: true,
            feature: true,
            status: true,
            priority: true,
            source_file: true
        },
        order: [
            'select', 'test_case_id', 'summary', 'app', 'test_type', 
            'feature', 'status', 'priority', 'source_file'
        ]
    };
    
    try {
        const saved = localStorage.getItem('columnPreferences');
        if (saved) {
            return JSON.parse(saved);
        }
    } catch (error) {
        console.error('Error loading column preferences:', error);
    }
    
    return defaultPreferences;
}

function saveColumnPreferences(preferences) {
    try {
        localStorage.setItem('columnPreferences', JSON.stringify(preferences));
    } catch (error) {
        console.error('Error saving column preferences:', error);
    }
}

function loadColumnPreferences() {
    const preferences = getColumnPreferences();
    
    // Apply column visibility
    Object.keys(preferences.visible).forEach(columnKey => {
        const isVisible = preferences.visible[columnKey];
        toggleColumn(columnKey, isVisible);
    });
    
    // Apply column order
    applyColumnOrder(preferences.order);
}

function toggleColumn(columnKey, isVisible) {
    const elements = document.querySelectorAll(`[data-column="${columnKey}"]`);
    elements.forEach(element => {
        if (isVisible) {
            element.style.display = '';
        } else {
            element.style.display = 'none';
        }
    });
}

function applyColumnOrder(order) {
    // This is a simplified version - in a real implementation, you'd need to reorder DOM elements
    // For now, we'll just ensure the columns are in the correct order
    console.log('Applying column order:', order);
}

function applyColumnChanges() {
    const preferences = {
        visible: {},
        order: []
    };
    
    // Get visibility preferences
    const checkboxes = document.querySelectorAll('#columnCheckboxes input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        const columnKey = checkbox.dataset.column;
        preferences.visible[columnKey] = checkbox.checked;
    });
    
    // Get order preferences (simplified - in real implementation, you'd get from drag & drop)
    const orderItems = document.querySelectorAll('#columnOrder .list-group-item');
    orderItems.forEach((item, index) => {
        const columnName = item.textContent.trim();
        // Map column name back to key (simplified)
        const columnKey = getColumnKeyFromName(columnName);
        if (columnKey) {
            preferences.order.push(columnKey);
        }
    });
    
    // Save preferences
    saveColumnPreferences(preferences);
    
    // Apply changes
    loadColumnPreferences();
    
    // Close modal
    const modal = bootstrap.Modal.getInstance(document.getElementById('columnManagerModal'));
    modal.hide();
    
    // Show success message
    showColumnUpdateMessage('Column preferences updated successfully!');
}

function getColumnKeyFromName(name) {
    const mapping = {
        'Select': 'select',
        'Test Case ID': 'test_case_id',
        'Summary': 'summary',
        'App': 'app',
        'Test Type': 'test_type',
        'Feature': 'feature',
        'Status': 'status',
        'Priority': 'priority',
        'Source File': 'source_file'
    };
    return mapping[name];
}

function resetColumnPreferences() {
    if (confirm('Are you sure you want to reset all column preferences to default?')) {
        localStorage.removeItem('columnPreferences');
        loadColumnPreferences();
        populateColumnManagerModal();
        showColumnUpdateMessage('Column preferences reset to default!');
    }
}

function showAllColumns() {
    const checkboxes = document.querySelectorAll('#columnCheckboxes input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        if (!checkbox.disabled) {
            checkbox.checked = true;
        }
    });
}

function hideAllColumns() {
    const checkboxes = document.querySelectorAll('#columnCheckboxes input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        if (!checkbox.disabled) {
            checkbox.checked = false;
        }
    });
}

function showColumnUpdateMessage(message) {
    let messageElement = document.getElementById('column-update-message');
    if (!messageElement) {
        messageElement = document.createElement('div');
        messageElement.id = 'column-update-message';
        messageElement.className = 'alert alert-success alert-dismissible fade show position-fixed';
        messageElement.style.top = '20px';
        messageElement.style.right = '20px';
        messageElement.style.zIndex = '9999';
        messageElement.style.minWidth = '300px';
        document.body.appendChild(messageElement);
    }
    
    messageElement.innerHTML = `
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        <i class="fas fa-columns me-2"></i>
        <strong>Success!</strong> ${message}
    `;
    
    setTimeout(() => {
        if (messageElement && messageElement.parentNode) {
            messageElement.remove();
        }
    }, 3000);
}

// Dynamic Filters Functionality
function initializeDynamicFilters() {
    const dynamicFiltersBtn = document.getElementById('dynamicFiltersBtn');
    if (!dynamicFiltersBtn) {
        console.log('Dynamic filters button not found');
        return;
    }
    
    dynamicFiltersBtn.addEventListener('click', function() {
        toggleDynamicFilters();
    });
    
    // Load available columns for dynamic filters
    loadAvailableColumns();
    
    console.log('Dynamic filters functionality initialized');
}

function toggleDynamicFilters() {
    const section = document.getElementById('dynamicFiltersSection');
    const btn = document.getElementById('dynamicFiltersBtn');
    
    if (section.style.display === 'none') {
        section.style.display = 'block';
        btn.classList.add('active');
        btn.classList.remove('btn-outline-light');
        btn.classList.add('btn-info');
    } else {
        section.style.display = 'none';
        btn.classList.remove('active');
        btn.classList.remove('btn-info');
        btn.classList.add('btn-outline-light');
    }
}

function loadAvailableColumns() {
    // Get available columns from the API
    fetch('/api/filter-options')
        .then(response => response.json())
        .then(data => {
            window.availableColumns = data.available_columns || [];
            console.log('Available columns loaded:', window.availableColumns);
        })
        .catch(error => {
            console.error('Error loading available columns:', error);
            // Fallback to default columns
            window.availableColumns = [
                'Test Case ID', 'Summary', 'App', 'Test Type', 'Feature', 
                'Status', 'Priority', 'Source File', 'Expected Behavior', 
                'Screen ID', 'Assignee', 'Category', 'Created Date', 'Due Date'
            ];
        });
}

function addDynamicFilter() {
    const container = document.getElementById('dynamicFiltersContainer');
    if (!container) return;
    
    const filterId = 'dynamic_filter_' + Date.now();
    const filterElement = document.createElement('div');
    filterElement.className = 'col-md-4 mb-3';
    filterElement.id = filterId;
    
    filterElement.innerHTML = `
        <div class="card border-secondary">
            <div class="card-body p-3">
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <h6 class="mb-0">Filter</h6>
                    <button type="button" class="btn btn-sm btn-outline-danger" onclick="removeDynamicFilter('${filterId}')">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="mb-2">
                    <label class="form-label small">Column</label>
                    <select class="form-select form-select-sm" name="dynamic_column_${filterId}">
                        <option value="">Select Column</option>
                        ${generateColumnOptions()}
                    </select>
                </div>
                <div class="mb-2">
                    <label class="form-label small">Filter Type</label>
                    <select class="form-select form-select-sm" name="dynamic_type_${filterId}">
                        <option value="exact">Exact Match</option>
                        <option value="contains">Contains</option>
                        <option value="starts_with">Starts With</option>
                        <option value="ends_with">Ends With</option>
                        <option value="regex">Regex</option>
                        <option value="in_list">In List</option>
                        <option value="not_in_list">Not In List</option>
                        <option value="greater_than">Greater Than</option>
                        <option value="less_than">Less Than</option>
                        <option value="between">Between</option>
                        <option value="is_empty">Is Empty</option>
                        <option value="is_not_empty">Is Not Empty</option>
                    </select>
                </div>
                <div class="mb-2">
                    <label class="form-label small">Value</label>
                    <input type="text" class="form-control form-control-sm" name="dynamic_value_${filterId}" placeholder="Enter filter value">
                </div>
                <div class="mb-2">
                    <label class="form-label small">Second Value (for 'Between')</label>
                    <input type="text" class="form-control form-control-sm" name="dynamic_value2_${filterId}" placeholder="Enter second value">
                </div>
            </div>
        </div>
    `;
    
    container.appendChild(filterElement);
}

function generateColumnOptions() {
    if (!window.availableColumns) return '';
    
    return window.availableColumns.map(column => 
        `<option value="${column}">${column}</option>`
    ).join('');
}

function removeDynamicFilter(filterId) {
    const element = document.getElementById(filterId);
    if (element) {
        element.remove();
    }
}

function clearAllDynamicFilters() {
    const container = document.getElementById('dynamicFiltersContainer');
    if (container) {
        container.innerHTML = '';
    }
    
    // Also clear the dynamic filters section
    const section = document.getElementById('dynamicFiltersSection');
    if (section) {
        section.style.display = 'none';
    }
    
    // Reset button state
    const btn = document.getElementById('dynamicFiltersBtn');
    if (btn) {
        btn.classList.remove('active');
        btn.classList.remove('btn-info');
        btn.classList.add('btn-outline-light');
    }
}

// Override the existing clearAllDynamicFilters function if it exists
if (typeof clearAllDynamicFilters === 'undefined') {
    window.clearAllDynamicFilters = clearAllDynamicFilters;
}

// Dynamic filter functionality
let filterCounter = 0;
const usedColumns = new Set();

function addDynamicFilter() {
    const columnSelect = document.getElementById('filterColumn');
    const selectedColumn = columnSelect.value;
    
    if (!selectedColumn || usedColumns.has(selectedColumn)) {
        return;
    }
    
    usedColumns.add(selectedColumn);
    filterCounter++;
    
    const container = document.getElementById('dynamicFilterContainer');
    const filterDiv = document.createElement('div');
    filterDiv.className = 'col-md-3 mb-2 dynamic-filter-item';
    filterDiv.id = `filter-${filterCounter}`;

    const uniqueValues = getUniqueValuesForColumn(selectedColumn);
    
    filterDiv.innerHTML = `
        <div class="d-flex align-items-end">
            <div class="flex-grow-1 me-2">
                <label class="form-label small">${selectedColumn}</label>
                <select class="form-select form-select-sm" name="dynamic_${selectedColumn.toLowerCase().replace(' ', '_')}" id="dynamic_${filterCounter}">
                    <option value="">All ${selectedColumn}</option>
                    ${uniqueValues.map(value => `<option value="${value}">${value}</option>`).join('')}
                </select>
            </div>
            <button type="button" class="btn btn-outline-danger btn-sm" onclick="removeDynamicFilter(${filterCounter}, '${selectedColumn}')" title="Remove filter">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    container.appendChild(filterDiv);

    // Initialize Select2 if jQuery is available
    if (typeof $ !== 'undefined') {
        $(filterDiv).find('select').select2({
            theme: 'bootstrap-5',
            placeholder: function() {
                return $(this).find('option:first').text();
            },
            allowClear: true,
            width: '100%',
            minimumResultsForSearch: 0,
            multiple: function() {
                return $(this).attr('multiple') !== undefined;
            }
        });
    }

    columnSelect.value = '';
    updateAvailableColumns();
}

function removeDynamicFilter(filterId, column) {
    const filterElement = document.getElementById(`filter-${filterId}`);
    if (filterElement) {
        filterElement.classList.add('removing');
        
        setTimeout(() => {
            filterElement.remove();
            usedColumns.delete(column);
            updateAvailableColumns();
        }, 300);
    }
}

function updateAvailableColumns() {
    const columnSelect = document.getElementById('filterColumn');
    if (!columnSelect) return;
    
    const options = columnSelect.querySelectorAll('option');
    
    options.forEach(option => {
        if (option.value && usedColumns.has(option.value)) {
            option.style.display = 'none';
            option.disabled = true;
        } else {
            option.style.display = 'block';
            option.disabled = false;
        }
    });

    const availableOptions = Array.from(options).filter(opt => opt.value && !opt.disabled);
    if (availableOptions.length === 0) {
        columnSelect.querySelector('option[value=""]').textContent = 'All columns selected';
    } else {
        columnSelect.querySelector('option[value=""]').textContent = 'Select column to filter...';
    }
}

function getUniqueValuesForColumn(column) {
    // This function will be overridden by template-specific code
    const columnValues = {
        'Feature': [],
        'Screen ID': [],
        'Test Type': [],
        'TestSuite Type': [],
        'Requirement Type': [],
        'Summary': ['Login Test', 'Data Validation', 'API Test', 'UI Test', 'Performance Test', 'Security Test'], 
        'Test Case ID': ['TC-001', 'TC-002', 'TC-003', 'TC-004', 'Auto-Generated'] 
    };
    
    return columnValues[column] || [];
}

function clearAllDynamicFilters() {
    const container = document.getElementById('dynamicFilterContainer');
    if (container) {
        container.innerHTML = '';
    }
    usedColumns.clear();
    filterCounter = 0;
    updateAvailableColumns();
}

function initializeSmartMultiSelect() {
    console.log('Initializing smart multi-select...');
    // Note: This would need the multiselect_threshold variable from the template
    const threshold = 2; // Lower threshold to make Requirement Type use tag UI like others
    
    if (typeof $ !== 'undefined') {
        $('select[multiple]').each(function() {
            const $select = $(this);
            
            // Check if already initialized to prevent duplicates
            if ($select.hasClass('smart-multiselect-initialized')) {
                return;
            }
            
            // Make sure the select element is visible for initialization
            $select.show();
            
            const options = $select.find('option').length - 1; 
            console.log('Select element found with', options, 'options for field:', $select.attr('name'));
            
            if (options <= threshold) {
                console.log('Using checkbox UI for', options, 'options for field:', $select.attr('name'));
                initializeCheckboxMultiSelect($select);
            } else {
                console.log('Using tag UI for', options, 'options for field:', $select.attr('name'));
                initializeTagMultiSelect($select);
            }
            
            // Mark as initialized
            $select.addClass('smart-multiselect-initialized');
        });
    }
}

function initializeCheckboxMultiSelect($select) {
    // Check if already initialized to prevent duplicates
    if ($select.hasClass('checkbox-multiselect-initialized')) {
        console.log('Checkbox multiselect already initialized, skipping...');
        return;
    }
    
    if ($select.hasClass('select2-hidden-accessible')) {
        console.log('Select2 already initialized, destroying first...');
        $select.select2('destroy');
    }

    // Create a simple, clean checkbox container
    const $container = $('<div class="checkbox-multiselect-container" style="border: 1px solid #ced4da; border-radius: 4px; padding: 10px; background: white;"></div>');
    
    // Add search input
    const $searchInput = $('<input type="text" class="form-control form-control-sm mb-2" placeholder="Search options..." style="width: 100%;">');
    $container.append($searchInput);
    
    // Add options container
    const $optionsContainer = $('<div class="checkbox-options"></div>');

    // Get options from select
    const options = $select.find('option').not(':first');
    console.log('Creating checkboxes for', options.length, 'options');

    options.each(function() {
        const $option = $(this);
        const value = $option.val();
        const text = $option.text();
        const isSelected = $option.is(':selected');
        
        console.log('Creating checkbox for:', value, text, isSelected);
        
        const $checkboxDiv = $('<div class="form-check mb-1"></div>');
        const $checkbox = $(`<input class="form-check-input" type="checkbox" value="${value}" id="cb_${value}" ${isSelected ? 'checked' : ''}>`);
        const $label = $(`<label class="form-check-label" for="cb_${value}" style="cursor: pointer;">${text}</label>`);
        
        $checkboxDiv.append($checkbox).append($label);
        $optionsContainer.append($checkboxDiv);
    });

    $container.append($optionsContainer);
    
    // Replace the entire multiselect container with our simple checkbox container
    const $multiselectContainer = $select.closest('.multiselect-container');
    if ($multiselectContainer.length) {
        $multiselectContainer.replaceWith($container);
    } else {
        $select.hide().after($container);
    }
    
    // Add search functionality
    $searchInput.on('input', function() {
        const searchTerm = $(this).val().toLowerCase();
        $optionsContainer.find('.form-check').each(function() {
            const $check = $(this);
            const text = $check.find('label').text().toLowerCase();
            if (text.includes(searchTerm)) {
                $check.show();
            } else {
                $check.hide();
            }
        });
    });

    // Sync checkbox changes with hidden select
    $container.on('change', 'input[type="checkbox"]', function() {
        const $checkbox = $(this);
        const value = $checkbox.val();
        const $option = $select.find('option[value="' + value + '"]');
        
        if ($checkbox.is(':checked')) {
            $option.prop('selected', true);
        } else {
            $option.prop('selected', false);
        }
        
        console.log('Checkbox changed:', value, $checkbox.is(':checked'));
    });
    
    // Mark as initialized
    $select.addClass('checkbox-multiselect-initialized');
    
    console.log('Checkbox multiselect initialized for:', $select.attr('name'));
}

function initializeTagMultiSelect($select) {
    // Check if already initialized to prevent duplicates
    if ($select.hasClass('tag-multiselect-initialized')) {
        console.log('Tag multiselect already initialized, skipping...');
        return;
    }
    
    if ($select.hasClass('select2-hidden-accessible')) {
        console.log('Select2 already initialized, destroying first...');
        $select.select2('destroy');
    }

    // Hide the multiselect container since we're using Select2
    const container = $select.closest('.multiselect-container');
    if (container.length) {
        container.find('.multiselect-input, .multiselect-dropdown').hide();
    }

    $select.select2({
        theme: 'bootstrap-5',
        placeholder: function() {
            return $(this).find('option:first').text();
        },
        allowClear: true,
        width: '100%',
        minimumResultsForSearch: 0,
        multiple: true,
        tags: false,
        tokenSeparators: [','],
        
        templateResult: function(data) {
            if (data.loading) return data.text;
            return $('<span class="select2-option">' + data.text + '</span>');
        },
        templateSelection: function(data) {
            return $('<span class="select2-tag">' + data.text + '</span>');
        }
    });
    
    // Mark as initialized
    $select.addClass('tag-multiselect-initialized');
}

function updateSelectFromCheckboxes($select, $checkboxContainer) {
    const selectedValues = [];
    $checkboxContainer.find('input[type="checkbox"]:checked').each(function() {
        selectedValues.push($(this).val());
    });

    $select.val(selectedValues);
    $select.trigger('change');
}

// Test Suite Preparation Functions
function toggleTestSuite() {
    const content = document.getElementById('testSuiteContent');
    const toggle = document.getElementById('testSuiteToggle');
    const icon = toggle.querySelector('i');
    
    if (content.style.display === 'none') {
        content.style.display = 'block';
        icon.className = 'fas fa-chevron-up';
    } else {
        content.style.display = 'none';
        icon.className = 'fas fa-chevron-down';
    }
}

function clearTestSuiteForm() {
    const form = document.getElementById('releaseDetailsForm');
    if (form) {
        form.reset();
        updateExportButton();
    }
}

function updateExportButton() {
    const releaseVersion = document.getElementById('releaseVersion');
    const selectedCases = document.querySelectorAll('.test-case-checkbox:checked').length;
    const exportBtn = document.getElementById('exportSuiteBtn');
    
    if (releaseVersion && exportBtn) {
        if (releaseVersion.value.trim() && selectedCases > 0) {
            exportBtn.disabled = false;
            exportBtn.innerHTML = `<i class="fas fa-download me-1"></i>Export Test Suite (${selectedCases} cases)`;
        } else {
            exportBtn.disabled = true;
            exportBtn.innerHTML = '<i class="fas fa-download me-1"></i>Export Test Suite';
        }
    }
}

function exportTestSuite() {
    const releaseVersion = document.getElementById('releaseVersion');
    const selectedCases = document.querySelectorAll('.test-case-checkbox:checked');
    
    if (!releaseVersion || !releaseVersion.value.trim()) {
        alert('Please enter a release version');
        return;
    }
    
    if (selectedCases.length === 0) {
        alert('Please select at least one test case');
        return;
    }
    
    // Collect form data
    const formData = new FormData();
    formData.append('releaseVersion', releaseVersion.value);
    formData.append('sprint', document.getElementById('sprint').value);
    formData.append('buildNumber', document.getElementById('buildNumber').value);
    formData.append('environment', document.getElementById('environment').value);
    formData.append('testSuiteName', document.getElementById('testSuiteName').value);
    formData.append('testSuiteDescription', document.getElementById('testSuiteDescription').value);
    
    // Collect selected test case IDs
    const selectedIds = Array.from(selectedCases).map(cb => cb.value);
    formData.append('selectedTestCases', selectedIds.join(','));
    
    // Submit form
    // Note: This would need to be updated to use proper URL generation
    fetch(window.location.pathname + '/export_test_suite', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (response.ok) {
            return response.blob();
        }
        throw new Error('Export failed');
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `test_suite_${releaseVersion.value}_${new Date().toISOString().split('T')[0]}.xlsx`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    })
    .catch(error => {
        console.error('Export error:', error);
        alert('Failed to export test suite. Please try again.');
    });
}

// Additional initialization for test suite functionality
// This functionality is now handled in the main DOMContentLoaded event listener above

// Store all visible/filtered test cases
function storeFilteredTestCases() {
    const filteredTestCases = [];
    
    // Get all visible test case rows (not hidden by filters)
    const rows = document.querySelectorAll('.test-case-row');
    
    rows.forEach(row => {
        const testCaseData = extractTestCaseData(row);
        if (testCaseData) {
            filteredTestCases.push(testCaseData);
        }
    });
    
    // Store in localStorage
    localStorage.setItem('filteredTestCases', JSON.stringify(filteredTestCases));
    console.log(`Stored ${filteredTestCases.length} filtered test cases`);
}

// Test Case Selection Functions
function updateSelectedTestCases() {
    const checkboxes = document.querySelectorAll('.test-case-checkbox:checked');
    const selectedTestCases = [];
    
    checkboxes.forEach(checkbox => {
        const row = checkbox.closest('tr') || checkbox.closest('.card');
        if (row) {
            const testCaseData = extractTestCaseData(row);
            if (testCaseData) {
                selectedTestCases.push(testCaseData);
            }
        }
    });
    
    // Store in localStorage
    localStorage.setItem('selectedTestCases', JSON.stringify(selectedTestCases));
    
    // Update UI indicators
    updateSelectedCount(selectedTestCases.length);
}

function extractTestCaseData(row) {
    try {
        const testCaseId = row.querySelector('[data-column="test_case_id"]')?.textContent?.trim() || 
                          row.querySelector('.text-primary')?.textContent?.trim() || 
                          'N/A';
        
        const summary = row.querySelector('[data-column="summary"]')?.textContent?.trim() || 
                       row.querySelector('.card-title')?.textContent?.trim() || 
                       'Test case summary';
        
        const app = row.querySelector('[data-column="app"]')?.textContent?.trim() || 'N/A';
        const testType = row.querySelector('[data-column="test_type"]')?.textContent?.trim() || 'N/A';
        const priority = row.querySelector('[data-column="priority"]')?.textContent?.trim() || 'N/A';
        
        return {
            id: testCaseId,
            summary: summary,
            app: app,
            testType: testType,
            priority: priority
        };
    } catch (error) {
        console.error('Error extracting test case data:', error);
        return null;
    }
}

function loadSelectedTestCases() {
    const selectedTestCases = JSON.parse(localStorage.getItem('selectedTestCases') || '[]');
    
    // Restore checkbox states
    const checkboxes = document.querySelectorAll('.test-case-checkbox');
    checkboxes.forEach(checkbox => {
        const row = checkbox.closest('tr') || checkbox.closest('.card');
        if (row) {
            const testCaseData = extractTestCaseData(row);
            if (testCaseData && selectedTestCases.some(tc => tc.id === testCaseData.id)) {
                checkbox.checked = true;
            }
        }
    });
    
    updateSelectedCount(selectedTestCases.length);
}

function updateSelectedCount(count) {
    // Update any UI elements that show selected count
    const countElements = document.querySelectorAll('.selected-count');
    countElements.forEach(element => {
        element.textContent = `${count} selected`;
    });
}

function clearSelectedTestCases() {
    localStorage.removeItem('selectedTestCases');
    
    // Uncheck all checkboxes
    const checkboxes = document.querySelectorAll('.test-case-checkbox');
    checkboxes.forEach(checkbox => {
        checkbox.checked = false;
    });
    
    updateSelectedCount(0);
}

// Make functions available globally
window.clearAllFilters = clearAllFilters;
window.updateSelectedTestCases = updateSelectedTestCases;
window.loadSelectedTestCases = loadSelectedTestCases;
window.clearSelectedTestCases = clearSelectedTestCases;
window.clearAllDynamicFilters = clearAllDynamicFilters;
