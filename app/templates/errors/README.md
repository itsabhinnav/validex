# Error Templates

This folder contains templates for error pages and error handling.

## Templates

### `404.html`
Page not found error template. Features:
- Clear error message
- Helpful navigation options
- Search functionality
- Return to home button
- Professional error page design

### `500.html`
Internal server error template. Includes:
- Server error message
- Contact information
- Error reporting options
- Return to previous page
- Clean error page layout

## Features

- **User-Friendly**: Clear, non-technical error messages
- **Helpful Navigation**: Easy ways to get back to working pages
- **Professional Design**: Consistent with application branding
- **Responsive**: Works on all device sizes
- **Accessible**: Proper error page accessibility

## Usage

These templates are used by Flask error handlers:

```python
@app.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500
```

## Dependencies

- Extends `common/base.html`
- Bootstrap 5.1.3 for styling
- Font Awesome for icons
- Custom error page CSS
