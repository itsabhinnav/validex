import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-mock-toggle',
  template: `
    <div class="mock-toggle-container">
      <div class="mock-toggle">
        <label class="form-check-label">
          <input 
            type="checkbox" 
            class="form-check-input" 
            [checked]="isMockModeEnabled()"
            (change)="toggleMockMode($event)"
          >
          Mock Mode
        </label>
        <small class="text-muted d-block">
          {{ isMockModeEnabled() ? 'Using mock data' : 'Using real API' }}
        </small>
      </div>
    </div>
  `,
  styles: [`
    .mock-toggle-container {
      position: fixed;
      top: 10px;
      right: 10px;
      z-index: 1000;
      background: white;
      padding: 10px;
      border-radius: 5px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.1);
      border: 1px solid #ddd;
    }
    
    .mock-toggle {
      font-size: 14px;
    }
    
    .form-check-input {
      margin-right: 8px;
    }
    
    .text-muted {
      font-size: 12px;
      margin-top: 2px;
    }
  `]
})
export class MockToggleComponent implements OnInit {

  constructor() { }

  ngOnInit(): void {
  }

  isMockModeEnabled(): boolean {
    return localStorage.getItem('mockMode') === 'true' || 
           sessionStorage.getItem('mockMode') === 'true';
  }

  toggleMockMode(event: Event): void {
    const target = event.target as HTMLInputElement;
    const enabled = target.checked;
    
    if (enabled) {
      localStorage.setItem('mockMode', 'true');
      console.log('Mock mode enabled - refreshing page to apply changes');
      // Refresh the page to apply mock mode
      setTimeout(() => {
        window.location.reload();
      }, 500);
    } else {
      localStorage.removeItem('mockMode');
      sessionStorage.removeItem('mockMode');
      console.log('Mock mode disabled - refreshing page to apply changes');
      // Refresh the page to apply real mode
      setTimeout(() => {
        window.location.reload();
      }, 500);
    }
  }
}
