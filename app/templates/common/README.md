# Common Templates

This folder contains shared templates used across the entire application.

## Templates

### `base.html`
The main base template that all other templates extend from. Contains:
- HTML structure and head section
- Navigation bar
- Sidebar
- Footer
- Common JavaScript and CSS includes
- Auto-refresh configuration injection

### `landing.html`
Landing page template for the application. Features:
- Hero section with application branding
- Call-to-action buttons
- Application description
- Clean, modern design

### `app_selector.html`
Application selector page template. Allows users to choose between:
- Validex (Test Case Management)
- Sakura (Requirements Management)
- Shows application status and availability

### `role_selection.html`
Role selection template for user authentication. Provides:
- Role-based access control
- Administrator and Tester role options
- Application statistics display
- Clean role selection interface

## Usage

These templates are extended by application-specific templates:

```html
{% extends "common/base.html" %}
{% block content %}
    <!-- Page content here -->
{% endblock %}
```

## Dependencies

- Bootstrap 5.1.3
- Font Awesome 6.0.0
- jQuery 3.7.1
- Custom CSS and JavaScript files
