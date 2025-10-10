/**
 * Dynamic Configuration Management
 * Provides interface for analyzing Excel files and updating configuration
 */

class DynamicConfigManager {
    constructor() {
        this.isAnalyzing = false;
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadAppStatus();
    }
    
    setupEventListeners() {
        // Analyze Excel files button
        document.addEventListener('click', (e) => {
            if (e.target.matches('.analyze-excel-btn')) {
                this.analyzeExcelFiles();
            }
            if (e.target.matches('.refresh-status-btn')) {
                this.loadAppStatus();
            }
        });
    }
    
    async loadAppStatus() {
        try {
            const response = await fetch('/api/app-status');
            const data = await response.json();
            
            if (data.success) {
                this.displayAppStatus(data.app_status);
            } else {
                this.showError('Failed to load app status: ' + data.message);
            }
        } catch (error) {
            this.showError('Error loading app status: ' + error.message);
        }
    }
    
    displayAppStatus(appStatus) {
        const container = document.getElementById('app-status-container');
        if (!container) return;
        
        let html = '<div class="row">';
        
        for (const [appName, status] of Object.entries(appStatus)) {
            const statusClass = status.enabled ? 'success' : 'secondary';
            const statusIcon = status.enabled ? 'check-circle' : 'times-circle';
            const statusText = status.enabled ? 'Active' : 'Inactive';
            
            html += `
                <div class="col-md-6 mb-3">
                    <div class="card">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <h6 class="mb-0 text-capitalize">${appName}</h6>
                            <span class="badge bg-${statusClass}">
                                <i class="fas fa-${statusIcon}"></i> ${statusText}
                            </span>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-6">
                                    <small class="text-muted">Directory:</small><br>
                                    <code>${status.directory}</code>
                                </div>
                                <div class="col-6">
                                    <small class="text-muted">Excel Files:</small><br>
                                    <strong>${status.file_count}</strong>
                                </div>
                            </div>
                            ${status.files.length > 0 ? `
                                <div class="mt-2">
                                    <small class="text-muted">Files:</small>
                                    <div class="mt-1">
                                        ${status.files.map(file => 
                                            `<span class="badge bg-light text-dark me-1 mb-1">${file}</span>`
                                        ).join('')}
                                    </div>
                                </div>
                            ` : ''}
                        </div>
                    </div>
                </div>
            `;
        }
        
        html += '</div>';
        container.innerHTML = html;
    }
    
    async analyzeExcelFiles() {
        if (this.isAnalyzing) {
            this.showWarning('Analysis is already in progress...');
            return;
        }
        
        this.isAnalyzing = true;
        this.updateAnalyzeButton(true);
        this.showProgress('Analyzing Excel files...');
        
        try {
            const response = await fetch('/api/analyze-excel-files', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showSuccess('Excel files analyzed successfully!');
                this.displayAnalysisResults(data.analysis_results);
                this.loadAppStatus(); // Refresh status
            } else {
                this.showError('Analysis failed: ' + data.message);
            }
            
        } catch (error) {
            this.showError('Error during analysis: ' + error.message);
        } finally {
            this.isAnalyzing = false;
            this.updateAnalyzeButton(false);
            this.hideProgress();
        }
    }
    
    displayAnalysisResults(results) {
        const container = document.getElementById('analysis-results-container');
        if (!container) return;
        
        let html = '<div class="analysis-results">';
        
        for (const [appName, analysis] of Object.entries(results)) {
            if (analysis.total_files === 0) {
                html += `
                    <div class="alert alert-warning">
                        <h6><i class="fas fa-exclamation-triangle"></i> ${appName.toUpperCase()}</h6>
                        <p class="mb-0">No Excel files found in directory.</p>
                    </div>
                `;
                continue;
            }
            
            html += `
                <div class="card mb-3">
                    <div class="card-header">
                        <h6 class="mb-0">
                            <i class="fas fa-chart-bar"></i> ${appName.toUpperCase()} Analysis Results
                        </h6>
                    </div>
                    <div class="card-body">
                        <div class="row mb-3">
                            <div class="col-md-3">
                                <div class="text-center">
                                    <h4 class="text-primary">${analysis.total_files}</h4>
                                    <small class="text-muted">Files Analyzed</small>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="text-center">
                                    <h4 class="text-success">${analysis.total_columns}</h4>
                                    <small class="text-muted">Total Columns</small>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="text-center">
                                    <h4 class="text-warning">${analysis.required_columns.length}</h4>
                                    <small class="text-muted">Required</small>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="text-center">
                                    <h4 class="text-info">${analysis.optional_columns.length}</h4>
                                    <small class="text-muted">Optional</small>
                                </div>
                            </div>
                        </div>
                        
                        <div class="row">
                            <div class="col-md-6">
                                <h6>Required Columns:</h6>
                                ${analysis.required_columns.length > 0 ? 
                                    analysis.required_columns.map(col => 
                                        `<span class="badge bg-warning me-1 mb-1">${col}</span>`
                                    ).join('') : 
                                    '<span class="text-muted">None</span>'
                                }
                            </div>
                            <div class="col-md-6">
                                <h6>Optional Columns:</h6>
                                ${analysis.optional_columns.length > 0 ? 
                                    analysis.optional_columns.map(col => 
                                        `<span class="badge bg-info me-1 mb-1">${col}</span>`
                                    ).join('') : 
                                    '<span class="text-muted">None</span>'
                                }
                            </div>
                        </div>
                        
                        ${Object.keys(analysis.column_definitions).length > 0 ? `
                            <div class="mt-3">
                                <h6>Column Details:</h6>
                                <div class="table-responsive">
                                    <table class="table table-sm">
                                        <thead>
                                            <tr>
                                                <th>Column</th>
                                                <th>Type</th>
                                                <th>Required</th>
                                                <th>Frequency</th>
                                                <th>Description</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            ${Object.entries(analysis.column_definitions).map(([col, def]) => `
                                                <tr>
                                                    <td><strong>${col}</strong></td>
                                                    <td><span class="badge bg-secondary">${def.type}</span></td>
                                                    <td>${def.required ? '<i class="fas fa-check text-success"></i>' : '<i class="fas fa-times text-muted"></i>'}</td>
                                                    <td>${def.frequency_percentage}%</td>
                                                    <td>${def.description}</td>
                                                </tr>
                                            `).join('')}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        ` : ''}
                    </div>
                </div>
            `;
        }
        
        html += '</div>';
        container.innerHTML = html;
    }
    
    updateAnalyzeButton(analyzing) {
        const button = document.querySelector('.analyze-excel-btn');
        if (!button) return;
        
        if (analyzing) {
            button.disabled = true;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
        } else {
            button.disabled = false;
            button.innerHTML = '<i class="fas fa-search"></i> Analyze Excel Files';
        }
    }
    
    showProgress(message) {
        const container = document.getElementById('progress-container');
        if (!container) return;
        
        container.innerHTML = `
            <div class="alert alert-info">
                <div class="d-flex align-items-center">
                    <div class="spinner-border spinner-border-sm me-2" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    ${message}
                </div>
            </div>
        `;
    }
    
    hideProgress() {
        const container = document.getElementById('progress-container');
        if (container) {
            container.innerHTML = '';
        }
    }
    
    showSuccess(message) {
        this.showAlert(message, 'success');
    }
    
    showError(message) {
        this.showAlert(message, 'danger');
    }
    
    showWarning(message) {
        this.showAlert(message, 'warning');
    }
    
    showAlert(message, type) {
        const container = document.getElementById('alert-container');
        if (!container) return;
        
        const alertId = 'alert-' + Date.now();
        container.innerHTML = `
            <div class="alert alert-${type} alert-dismissible fade show" id="${alertId}">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            const alert = document.getElementById(alertId);
            if (alert) {
                alert.remove();
            }
        }, 5000);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('app-status-container')) {
        window.dynamicConfigManager = new DynamicConfigManager();
    }
});
