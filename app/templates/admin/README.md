# Admin Templates

This folder contains templates for administrative functions and system management.

## Templates

### `admin_edit.html`
Administrative edit page template. Features:
- Test case editing interface
- Form validation
- Dynamic field management
- Save and cancel options
- Responsive design

## Features

- **Administrative Interface**: Tools for system administrators
- **Form Management**: Dynamic form handling
- **Validation**: Client and server-side validation
- **Responsive Design**: Works on all device sizes
- **User-Friendly**: Clean, intuitive interface

## Usage

These templates are used by the admin system:

```python
# Admin edit page
return render_template('admin/admin_edit.html', mode='edit', test_case=data)
```

## Dependencies

- Extends `common/base.html`
- Bootstrap 5.1.3 for styling
- Font Awesome for icons
- Custom admin CSS
- JavaScript for form handling
