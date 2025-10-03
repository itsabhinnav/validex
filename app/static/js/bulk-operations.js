/**
 * Bulk Operations for Test Cases
 * Advanced bulk editing, deletion, and export functionality
 */

class BulkOperations {
    constructor() {
        this.selectedItems = new Set();
        this.bulkActions = {
            edit: 'bulk-edit',
            delete: 'bulk-delete',
            export: 'bulk-export',
            execute: 'bulk-execute',
            duplicate: 'bulk-duplicate'
        };
        this.init();
    }

    init() {
        this.createBulkToolbar();
        this.bindEvents();
        this.initializeSelectAll();
    }

    createBulkToolbar() {
        const toolbar = document.createElement('div');
        toolbar.id = 'bulk-toolbar';
        toolbar.className = 'bulk-toolbar';
        toolbar.style.cssText = `
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 25px;
            border-radius: 50px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            z-index: 1000;
            display: none;
            align-items: center;
            gap: 15px;
            backdrop-filter: blur(10px);
        `;

        toolbar.innerHTML = `
            <div class="bulk-info">
                <i class="fas fa-check-circle me-2"></i>
                <span id="selected-count">0</span> selected
            </div>
            <div class="bulk-actions">
                <button class="bulk-btn" data-action="edit" title="Bulk Edit">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="bulk-btn" data-action="export" title="Export Selected">
                    <i class="fas fa-download"></i>
                </button>
                <button class="bulk-btn" data-action="execute" title="Bulk Execute">
                    <i class="fas fa-play"></i>
                </button>
                <button class="bulk-btn" data-action="duplicate" title="Duplicate">
                    <i class="fas fa-copy"></i>
                </button>
                <button class="bulk-btn danger" data-action="delete" title="Delete Selected">
                    <i class="fas fa-trash"></i>
                </button>
                <button class="bulk-btn" data-action="clear" title="Clear Selection">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

        // Add styles for bulk buttons
        const style = document.createElement('style');
        style.textContent = `
            .bulk-btn {
                background: rgba(255,255,255,0.2);
                border: 1px solid rgba(255,255,255,0.3);
                color: white;
                padding: 8px 12px;
                border-radius: 25px;
                cursor: pointer;
                transition: all 0.3s ease;
                font-size: 0.9rem;
            }
            .bulk-btn:hover {
                background: rgba(255,255,255,0.3);
                transform: scale(1.05);
            }
            .bulk-btn.danger {
                background: rgba(220,53,69,0.8);
                border-color: rgba(220,53,69,0.9);
            }
            .bulk-btn.danger:hover {
                background: rgba(220,53,69,1);
            }
            .bulk-toolbar {
                animation: slideUp 0.3s ease;
            }
            @keyframes slideUp {
                from { transform: translateX(-50%) translateY(100px); opacity: 0; }
                to { transform: translateX(-50%) translateY(0); opacity: 1; }
            }
        `;
        document.head.appendChild(style);
        document.body.appendChild(toolbar);
    }

    bindEvents() {
        // Bulk action buttons
        document.addEventListener('click', (e) => {
            if (e.target.closest('.bulk-btn')) {
                const action = e.target.closest('.bulk-btn').dataset.action;
                this.handleBulkAction(action);
            }
        });

        // Individual item selection
        document.addEventListener('change', (e) => {
            if (e.target.type === 'checkbox' && e.target.dataset.itemId) {
                this.toggleItemSelection(e.target.dataset.itemId, e.target.checked);
            }
        });

        // Select all checkbox
        document.addEventListener('change', (e) => {
            if (e.target.id === 'select-all') {
                this.toggleSelectAll(e.target.checked);
            }
        });
    }

    initializeSelectAll() {
        const table = document.querySelector('table');
        if (!table) return;

        const thead = table.querySelector('thead tr');
        if (!thead) return;

        const checkbox = document.createElement('th');
        checkbox.innerHTML = `
            <div class="form-check">
                <input class="form-check-input" type="checkbox" id="select-all">
                <label class="form-check-label" for="select-all"></label>
            </div>
        `;
        thead.insertBefore(checkbox, thead.firstChild);

        // Add checkboxes to each row
        const tbody = table.querySelector('tbody');
        if (tbody) {
            tbody.querySelectorAll('tr').forEach((row, index) => {
                const checkbox = document.createElement('td');
                checkbox.innerHTML = `
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" data-item-id="${index}">
                    </div>
                `;
                row.insertBefore(checkbox, row.firstChild);
            });
        }
    }

    toggleItemSelection(itemId, selected) {
        if (selected) {
            this.selectedItems.add(itemId);
        } else {
            this.selectedItems.delete(itemId);
        }
        this.updateBulkToolbar();
        this.updateSelectAllState();
    }

    toggleSelectAll(selectAll) {
        const checkboxes = document.querySelectorAll('input[type="checkbox"][data-item-id]');
        checkboxes.forEach((checkbox, index) => {
            checkbox.checked = selectAll;
            if (selectAll) {
                this.selectedItems.add(index.toString());
            } else {
                this.selectedItems.delete(index.toString());
            }
        });
        this.updateBulkToolbar();
    }

    updateSelectAllState() {
        const selectAllCheckbox = document.getElementById('select-all');
        const itemCheckboxes = document.querySelectorAll('input[type="checkbox"][data-item-id]');
        
        if (this.selectedItems.size === 0) {
            selectAllCheckbox.indeterminate = false;
            selectAllCheckbox.checked = false;
        } else if (this.selectedItems.size === itemCheckboxes.length) {
            selectAllCheckbox.indeterminate = false;
            selectAllCheckbox.checked = true;
        } else {
            selectAllCheckbox.indeterminate = true;
        }
    }

    updateBulkToolbar() {
        const toolbar = document.getElementById('bulk-toolbar');
        const countElement = document.getElementById('selected-count');
        
        if (this.selectedItems.size > 0) {
            toolbar.style.display = 'flex';
            countElement.textContent = this.selectedItems.size;
        } else {
            toolbar.style.display = 'none';
        }
    }

    handleBulkAction(action) {
        switch (action) {
            case 'edit':
                this.showBulkEditModal();
                break;
            case 'export':
                this.exportSelected();
                break;
            case 'execute':
                this.bulkExecute();
                break;
            case 'duplicate':
                this.duplicateSelected();
                break;
            case 'delete':
                this.confirmBulkDelete();
                break;
            case 'clear':
                this.clearSelection();
                break;
        }
    }

    showBulkEditModal() {
        const modal = this.createBulkEditModal();
        document.body.appendChild(modal);
        
        // Show modal
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }

    createBulkEditModal() {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="fas fa-edit me-2"></i>Bulk Edit Test Cases
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row">
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">Priority</label>
                                    <select class="form-select" id="bulk-priority">
                                        <option value="">No Change</option>
                                        <option value="Critical">Critical</option>
                                        <option value="High">High</option>
                                        <option value="Medium">Medium</option>
                                        <option value="Low">Low</option>
                                    </select>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">Status</label>
                                    <select class="form-select" id="bulk-status">
                                        <option value="">No Change</option>
                                        <option value="Passed">Passed</option>
                                        <option value="Failed">Failed</option>
                                        <option value="Pending">Pending</option>
                                        <option value="Blocked">Blocked</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">Test Type</label>
                                    <select class="form-select" id="bulk-type">
                                        <option value="">No Change</option>
                                        <option value="Smoke">Smoke</option>
                                        <option value="Sanity">Sanity</option>
                                        <option value="Regression">Regression</option>
                                        <option value="FMEA">FMEA</option>
                                    </select>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">Feature</label>
                                    <input type="text" class="form-control" id="bulk-feature" placeholder="Enter feature name">
                                </div>
                            </div>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Add Comments</label>
                            <textarea class="form-control" id="bulk-comments" rows="3" placeholder="Add comments to all selected test cases..."></textarea>
                        </div>
                        <div class="alert alert-info">
                            <i class="fas fa-info-circle me-2"></i>
                            This will update <strong>${this.selectedItems.size}</strong> selected test cases.
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" onclick="bulkOperations.applyBulkEdit()">
                            <i class="fas fa-save me-2"></i>Apply Changes
                        </button>
                    </div>
                </div>
            </div>
        `;
        return modal;
    }

    applyBulkEdit() {
        const changes = {
            priority: document.getElementById('bulk-priority').value,
            status: document.getElementById('bulk-status').value,
            type: document.getElementById('bulk-type').value,
            feature: document.getElementById('bulk-feature').value,
            comments: document.getElementById('bulk-comments').value
        };

        // Filter out empty values
        const filteredChanges = Object.fromEntries(
            Object.entries(changes).filter(([key, value]) => value !== '')
        );

        if (Object.keys(filteredChanges).length === 0) {
            alert('Please select at least one field to update.');
            return;
        }

        // Show loading state
        this.showLoadingState();

        // Simulate API call
        setTimeout(() => {
            this.showSuccessMessage(`Successfully updated ${this.selectedItems.size} test cases.`);
            this.clearSelection();
            this.hideModal();
        }, 2000);
    }

    exportSelected() {
        const selectedData = this.getSelectedData();
        
        if (selectedData.length === 0) {
            alert('No test cases selected for export.');
            return;
        }

        // Create CSV content
        const csvContent = this.convertToCSV(selectedData);
        
        // Download file
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `test_cases_export_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);

        this.showSuccessMessage(`Exported ${selectedData.length} test cases.`);
    }

    bulkExecute() {
        if (this.selectedItems.size === 0) {
            alert('No test cases selected for execution.');
            return;
        }

        const confirmed = confirm(`Execute ${this.selectedItems.size} selected test cases?`);
        if (confirmed) {
            this.showLoadingState();
            setTimeout(() => {
                this.showSuccessMessage(`Started execution of ${this.selectedItems.size} test cases.`);
            }, 1500);
        }
    }

    duplicateSelected() {
        if (this.selectedItems.size === 0) {
            alert('No test cases selected for duplication.');
            return;
        }

        const confirmed = confirm(`Duplicate ${this.selectedItems.size} selected test cases?`);
        if (confirmed) {
            this.showLoadingState();
            setTimeout(() => {
                this.showSuccessMessage(`Duplicated ${this.selectedItems.size} test cases.`);
            }, 1500);
        }
    }

    confirmBulkDelete() {
        if (this.selectedItems.size === 0) {
            alert('No test cases selected for deletion.');
            return;
        }

        const confirmed = confirm(`Are you sure you want to delete ${this.selectedItems.size} selected test cases? This action cannot be undone.`);
        if (confirmed) {
            this.showLoadingState();
            setTimeout(() => {
                this.showSuccessMessage(`Deleted ${this.selectedItems.size} test cases.`);
                this.clearSelection();
            }, 1500);
        }
    }

    clearSelection() {
        this.selectedItems.clear();
        document.querySelectorAll('input[type="checkbox"][data-item-id]').forEach(checkbox => {
            checkbox.checked = false;
        });
        document.getElementById('select-all').checked = false;
        this.updateBulkToolbar();
    }

    getSelectedData() {
        const selectedData = [];
        this.selectedItems.forEach(itemId => {
            const row = document.querySelector(`input[data-item-id="${itemId}"]`).closest('tr');
            if (row) {
                const cells = row.querySelectorAll('td');
                const data = {};
                // Extract data from table cells (adjust based on your table structure)
                cells.forEach((cell, index) => {
                    if (index > 0) { // Skip checkbox column
                        const header = document.querySelector(`thead th:nth-child(${index + 1})`);
                        if (header) {
                            data[header.textContent.trim()] = cell.textContent.trim();
                        }
                    }
                });
                selectedData.push(data);
            }
        });
        return selectedData;
    }

    convertToCSV(data) {
        if (data.length === 0) return '';
        
        const headers = Object.keys(data[0]);
        const csvRows = [headers.join(',')];
        
        data.forEach(row => {
            const values = headers.map(header => {
                const value = row[header] || '';
                return `"${value.replace(/"/g, '""')}"`;
            });
            csvRows.push(values.join(','));
        });
        
        return csvRows.join('\n');
    }

    showLoadingState() {
        const toolbar = document.getElementById('bulk-toolbar');
        toolbar.innerHTML = `
            <div class="d-flex align-items-center">
                <div class="spinner-border spinner-border-sm me-2" role="status"></div>
                <span>Processing...</span>
            </div>
        `;
    }

    showSuccessMessage(message) {
        const toolbar = document.getElementById('bulk-toolbar');
        toolbar.innerHTML = `
            <div class="d-flex align-items-center text-success">
                <i class="fas fa-check-circle me-2"></i>
                <span>${message}</span>
            </div>
        `;
        
        setTimeout(() => {
            this.updateBulkToolbar();
        }, 3000);
    }

    hideModal() {
        const modal = document.querySelector('.modal.show');
        if (modal) {
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) {
                bsModal.hide();
            }
        }
    }
}

// Initialize bulk operations when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    if (document.querySelector('table')) {
        window.bulkOperations = new BulkOperations();
    }
});
