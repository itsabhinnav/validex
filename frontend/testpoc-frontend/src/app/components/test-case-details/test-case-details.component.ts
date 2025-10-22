import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { TestCasesService } from '../../services/test-cases.service';
import { TestCase, FilterOptions, FilterState, PaginationState } from '../../models/high-performance-test-case.model';

@Component({
  selector: 'app-test-case-details',
  templateUrl: './test-case-details.component.html',
  styleUrls: ['./test-case-details.component.css']
})
export class TestCaseDetailsComponent implements OnInit {
  testCase: TestCase | null = null;
  loading = true;
  error: string | null = null;
  testCaseId: string | null = null;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private testCasesService: TestCasesService
  ) {}

  ngOnInit(): void {
    // Get test case ID from route parameters
    this.route.params.subscribe(params => {
      this.testCaseId = params['id'];
      if (this.testCaseId) {
        this.loadTestCaseDetails();
      } else {
        this.error = 'No test case ID provided';
        this.loading = false;
      }
    });
  }

  loadTestCaseDetails(): void {
    if (!this.testCaseId) return;

    this.loading = true;
    this.error = null;

    // Create empty filter state for getting all test cases
    const emptyFilterState: FilterState = {
      app_filter: [],
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

    // Create empty pagination state for getting all test cases
    const emptyPaginationState: PaginationState = {
      current_page: 1,
      per_page: 1000,
      total_cases: 0,
      total_pages: 0,
      has_prev: false,
      has_next: false
    };

    // For now, we'll get all test cases and find the one with matching ID
    // In a real application, you'd have a specific endpoint for individual test cases
    this.testCasesService.getTestCases(emptyFilterState, emptyPaginationState).subscribe({
      next: (response) => {
        const foundTestCase = response.test_cases.find(tc => 
          tc.tc_id === this.testCaseId
        );

        if (foundTestCase) {
          this.testCase = foundTestCase;
        } else {
          this.error = 'Test case not found';
        }
        this.loading = false;
      },
      error: (error) => {
        console.error('Error loading test case details:', error);
        this.error = 'Failed to load test case details';
        this.loading = false;
      }
    });
  }

  goBack(): void {
    this.router.navigate(['/test-cases']);
  }

  getFieldValue(fieldName: string): string {
    if (!this.testCase) return '';
    return (this.testCase as any)[fieldName] || '';
  }

  getFieldDisplayName(fieldName: string): string {
    // Convert field name to display name
    return fieldName.replace(/_/g, ' ').replace(/([A-Z])/g, ' $1').trim();
  }

  hasValue(fieldName: string): boolean {
    const value = this.getFieldValue(fieldName);
    return value !== null && value !== undefined && value.trim() !== '';
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
}