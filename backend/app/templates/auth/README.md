# Authentication Templates

This folder contains templates related to user authentication and access control.

## Templates

### `login.html`
User login page template. Features:
- Clean login form
- Username and password fields
- Remember me option
- Error message display
- Responsive design

### `role_selection.html`
Role selection page template. Provides:
- Role-based access control interface
- Administrator and Tester role options
- Application statistics display
- Clean, card-based selection interface
- Role-specific feature descriptions

### `setup.html`
Initial setup page template. Includes:
- Remote sync configuration
- Database setup options
- Initial application configuration
- Setup wizard interface
- Progress indicators

## Features

- **Responsive Design**: Works on all device sizes
- **Role-Based Access**: Different access levels for different users
- **Clean UI**: Modern, professional appearance
- **Error Handling**: Proper error message display
- **Security**: Secure authentication forms

## Usage

These templates are used by the authentication system:

```python
# Login page
return render_template('auth/login.html')

# Role selection
return render_template('auth/role_selection.html', admin_enabled=True)

# Setup page
return render_template('auth/setup.html')
```

## Dependencies

- Extends `common/base.html`
- Bootstrap 5.1.3 for styling
- Font Awesome for icons
- Custom authentication CSS
