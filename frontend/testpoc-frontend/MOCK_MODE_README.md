# Mock Mode Documentation

This document explains how to use the mock mode feature for testing the frontend separately from the backend.

## Overview

The mock mode allows you to run the frontend application with simulated data instead of making real API calls to the backend. This is useful for:

- **Frontend Development**: Develop and test UI components without needing a running backend
- **Demo Purposes**: Show the application functionality with realistic data
- **Testing**: Test frontend behavior with consistent, predictable data
- **Offline Development**: Work on the frontend when the backend is unavailable

## How to Enable Mock Mode

### Method 1: Using the Mock Toggle (Recommended)

1. Start the frontend application:
   ```bash
   cd frontend/testpoc-frontend
   npm start
   ```

2. Open the application in your browser (usually `http://localhost:4200`)

3. Look for the "Mock Mode" toggle in the top-right corner of the application

4. Check the "Mock Mode" checkbox to enable mock data

5. The page will automatically refresh to apply the changes

### Method 2: Using Browser Storage

You can enable mock mode programmatically using browser storage:

```javascript
// Enable mock mode
localStorage.setItem('mockMode', 'true');

// Disable mock mode
localStorage.removeItem('mockMode');

// Refresh the page to apply changes
window.location.reload();
```

### Method 3: Using Environment Configuration

You can set mock mode in the environment files:

**For development with mock data:**
```typescript
// src/environments/environment.mock.ts
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000/api/legacy/api',
  mockMode: true,
  mockDelay: 200
};
```

**For development with real API:**
```typescript
// src/environments/environment.ts
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000/api/legacy/api',
  mockMode: false,
  mockDelay: 200
};
```

## Mock Data Features

### Test Cases Data

The mock system provides 150 realistic test cases with the following characteristics:

- **Test Case IDs**: TC-0001 to TC-0150
- **Features**: Authentication, User Management, Payment Processing, Search, Notifications, Reports, Dashboard, Settings
- **Test Types**: Functional, Integration, Performance, Security, Usability, Regression
- **Priorities**: High, Medium, Low, Critical
- **Statuses**: Passed, Failed, Blocked, Not Executed, In Progress, Pending Review
- **Apps**: Mobile App, Web Portal, Admin Panel, API Service, Desktop App
- **Regions**: North America, Europe, Asia Pacific, Latin America, Middle East
- **Brands**: Brand A, Brand B, Brand C, Brand D, Brand E

### Filtering and Search

All filtering and search functionality works with mock data:

- **Text Search**: Search across test case IDs, summaries, objectives, features, screen IDs, and app names
- **Filter Options**: All filter dropdowns are populated with realistic values from the mock data
- **Pagination**: Mock data supports pagination with configurable page sizes
- **Sorting**: All columns can be sorted in ascending or descending order

### Export Functionality

Mock export functionality includes:

- **CSV Export**: Generates realistic CSV files with all test case data
- **Excel Export**: Simulates Excel file generation (returns CSV format)
- **PDF Export**: Simulates PDF generation (returns Excel format)

### Database Statistics

Mock database statistics provide realistic metrics:

- **Total Test Cases**: 150
- **Total Files**: 15
- **Status Distribution**: Realistic distribution across all statuses
- **Priority Distribution**: Realistic distribution across all priorities
- **App Distribution**: Realistic distribution across all apps
- **Feature Distribution**: Realistic distribution across all features

### Bulk Operations

Mock bulk operations simulate:

- **Update Status**: Simulates updating test case statuses
- **Update Priority**: Simulates updating test case priorities
- **Update Feature**: Simulates updating test case features
- **Delete Operations**: Simulates deleting test cases
- **Export Operations**: Simulates bulk export operations

## Technical Implementation

### Services

- **MockDataService**: Generates and manages mock data
- **MockHttpInterceptor**: Intercepts HTTP requests and returns mock responses
- **TestCasesService**: Updated to support both mock and real data modes

### Data Generation

Mock data is generated using:

- **Realistic Values**: Uses arrays of realistic values for each field
- **Random Distribution**: Randomly distributes values across test cases
- **Consistent Relationships**: Maintains logical relationships between fields
- **Dynamic Updates**: Filter options are dynamically generated from the data

### Performance Simulation

Mock responses include realistic delays:

- **API Calls**: 200-700ms delay to simulate network latency
- **Export Operations**: 1000ms delay to simulate processing time
- **Bulk Operations**: 800ms delay to simulate processing time
- **Database Operations**: 1500ms delay to simulate optimization time

## Development Workflow

### Frontend Development

1. Enable mock mode using the toggle
2. Develop UI components with consistent mock data
3. Test all functionality without backend dependencies
4. Switch to real API when backend is ready

### Testing

1. Use mock mode for unit tests and integration tests
2. Mock data provides consistent, predictable test scenarios
3. Test edge cases by modifying mock data generation

### Demo Preparation

1. Enable mock mode for demos
2. Mock data provides realistic, professional-looking data
3. All features work consistently without backend dependencies

## Troubleshooting

### Mock Mode Not Working

1. Check browser console for errors
2. Verify that `localStorage.getItem('mockMode')` returns `'true'`
3. Ensure the MockHttpInterceptor is properly registered in app.module.ts
4. Check that MockDataService is properly injected

### Data Not Loading

1. Check browser console for mock service logs
2. Verify that mock data is being generated correctly
3. Check that filter and pagination parameters are being processed

### Performance Issues

1. Mock delays are configurable in the environment files
2. Reduce `mockDelay` value for faster responses
3. Check that mock data generation is not blocking the UI

## Configuration Options

### Environment Variables

```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000/api/legacy/api',
  mockMode: true,        // Enable/disable mock mode
  mockDelay: 200          // Base delay for mock responses (ms)
};
```

### Mock Data Customization

You can customize mock data by modifying the `MockDataService`:

```typescript
// Modify the generateMockTestCases method to change data characteristics
private generateMockTestCases(count: number): TestCase[] {
  // Customize the data generation logic here
}
```

## Best Practices

1. **Use Mock Mode for Development**: Enable mock mode during frontend development
2. **Test with Real Data**: Regularly test with real API to ensure compatibility
3. **Keep Mock Data Realistic**: Maintain realistic mock data that represents production scenarios
4. **Document Changes**: Document any changes to mock data structure
5. **Version Control**: Include mock data changes in version control

## API Compatibility

The mock system maintains full compatibility with the real API:

- **Request Format**: Mock requests use the same format as real API requests
- **Response Format**: Mock responses match the real API response structure
- **Error Handling**: Mock system can simulate error scenarios
- **Performance**: Mock responses include realistic delays

This ensures that switching between mock and real data is seamless and doesn't require code changes.
