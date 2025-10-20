import { Component, EventEmitter, Input, Output } from '@angular/core';

export type ViewMode = 'list' | 'detail' | 'more';

@Component({
  selector: 'app-view-toggle',
  template: `
    <div class="btn-group" role="group" aria-label="View toggle">
      <!-- List View Button -->
      <button type="button" 
              class="btn btn-outline-secondary"
              [class.active]="currentView === 'list'"
              (click)="onViewChange('list')"
              title="List View">
        <i class="fas fa-th-list"></i>
      </button>
      
      <!-- Detail View Button -->
      <button type="button" 
              class="btn btn-outline-secondary"
              [class.active]="currentView === 'detail'"
              (click)="onViewChange('detail')"
              title="Detail View">
        <i class="fas fa-columns"></i>
      </button>
      
      <!-- More Options Button -->
      <div class="btn-group" role="group">
        <button type="button" 
                class="btn btn-outline-secondary dropdown-toggle"
                data-bs-toggle="dropdown"
                aria-expanded="false"
                title="More Options">
          <i class="fas fa-ellipsis-h"></i>
        </button>
        <ul class="dropdown-menu">
          <li><a class="dropdown-item" href="#" (click)="onExportClick('excel')">
            <i class="fas fa-file-excel text-success me-2"></i>Export to Excel
          </a></li>
          <li><a class="dropdown-item" href="#" (click)="onExportClick('csv')">
            <i class="fas fa-file-csv text-info me-2"></i>Export to CSV
          </a></li>
          <li><hr class="dropdown-divider"></li>
          <li><a class="dropdown-item" href="#" (click)="onRefreshClick()">
            <i class="fas fa-sync-alt text-primary me-2"></i>Refresh Data
          </a></li>
          <li><a class="dropdown-item" href="#" (click)="onClearFiltersClick()">
            <i class="fas fa-filter text-warning me-2"></i>Clear All Filters
          </a></li>
        </ul>
      </div>
    </div>
  `,
  styles: [`
    .btn-group .btn {
      border-radius: 0;
    }
    
    .btn-group .btn:first-child {
      border-top-left-radius: 0.375rem;
      border-bottom-left-radius: 0.375rem;
    }
    
    .btn-group .btn:last-child {
      border-top-right-radius: 0.375rem;
      border-bottom-right-radius: 0.375rem;
    }
    
    .btn-group .btn.active {
      background-color: #0d6efd;
      border-color: #0d6efd;
      color: white;
    }
    
    .btn-group .btn:hover:not(.active) {
      background-color: #f8f9fa;
      border-color: #dee2e6;
    }
    
    .dropdown-menu {
      min-width: 200px;
    }
    
    .dropdown-item {
      padding: 0.5rem 1rem;
    }
    
    .dropdown-item:hover {
      background-color: #f8f9fa;
    }
  `]
})
export class ViewToggleComponent {
  @Input() currentView: ViewMode = 'detail'; // Default to detail view
  @Output() viewChange = new EventEmitter<ViewMode>();
  @Output() exportRequest = new EventEmitter<string>();
  @Output() refreshRequest = new EventEmitter<void>();
  @Output() clearFiltersRequest = new EventEmitter<void>();

  onViewChange(view: ViewMode): void {
    this.currentView = view;
    this.viewChange.emit(view);
  }

  onExportClick(format: string): void {
    this.exportRequest.emit(format);
  }

  onRefreshClick(): void {
    this.refreshRequest.emit();
  }

  onClearFiltersClick(): void {
    this.clearFiltersRequest.emit();
  }
}
