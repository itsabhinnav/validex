# Admin Section Toggle Guide

This guide explains how to temporarily disable the admin section in the Validex application.

## 🎯 Overview

The admin section can be temporarily disabled using a configuration flag. When disabled:
- Admin role selection is hidden
- Admin dashboard is not accessible
- Admin navigation links are hidden
- All admin routes are protected

## 🔧 Configuration

### Configuration File
The admin toggle is controlled by the `app.admin_enabled` setting in `config/validex_config.json`:

```json
{
  "app": {
    "admin_enabled": false
  }
}
```

### Default State
- **Default**: `false` (admin disabled)
- **Purpose**: Temporarily disable admin features during development or maintenance

## 🚀 Usage

### Using the Toggle Script

#### Disable Admin Section
```bash
python scripts/toggle_admin.py disable
```

#### Enable Admin Section
```bash
python scripts/toggle_admin.py enable
```

### Manual Configuration

You can also manually edit `config/validex_config.json`:

```json
{
  "app": {
    "admin_enabled": false  // Set to true to enable
  }
}
```

## 🔄 What Happens When Disabled

### ✅ Features Hidden
- **Role Selection**: Admin option is hidden from role selection page
- **Navigation**: Admin links are hidden from navigation menu
- **Routes**: All admin routes redirect to role selection
- **Dashboard**: Admin-specific features are not accessible

### ✅ Routes Protected
- `/admin` - Admin dashboard
- `/jfrog-config` - JFrog configuration
- `/sync-dashboard` - Sync management
- `/set-role` - Prevents admin role selection

### ✅ User Experience
- **Clean Interface**: No admin clutter for regular users
- **Focused Experience**: Users see only tester features
- **Security**: Admin features are completely inaccessible

## 🎨 Visual Changes

### Role Selection Page
- Admin card shows "Coming Soon" message
- Admin button is disabled
- Visual indication that admin is not available

### Navigation Menu
- Admin links are conditionally hidden
- Only tester-relevant navigation is shown

### Dashboard
- No admin-specific quick actions
- Focus on test case management

## 🔧 Technical Implementation

### Configuration Check
```python
from config.settings import config

if not config.is_admin_enabled():
    return redirect(url_for('main.role_selection'))
```

### Template Conditions
```html
{% if get_text('app.features.admin_enabled') %}
    <!-- Admin content -->
{% endif %}
```

### Route Protection
All admin routes check the configuration flag before allowing access.

## 📋 Admin Features (When Enabled)

### Dashboard
- File management
- Test case statistics
- System overview

### JFrog Configuration
- Artifactory integration setup
- Repository configuration
- Access token management

### Sync Management
- Background sync control
- Sync status monitoring
- Log viewing

## 🚨 Important Notes

### Restart Required
After toggling the admin setting, **restart the application** to apply changes.

### Configuration Persistence
The setting is saved in `config/validex_config.json` and persists across application restarts.

### Development vs Production
- **Development**: Admin can be enabled for testing
- **Production**: Admin can be disabled for security

## 🔍 Troubleshooting

### Admin Still Visible
1. Check if application was restarted
2. Verify `config/validex_config.json` has `"admin_enabled": false`
3. Clear browser cache

### Configuration Not Saving
1. Check file permissions on `config/validex_config.json`
2. Verify the config directory exists
3. Check application logs for errors

### Script Not Working
1. Ensure you're in the project root directory
2. Check Python path includes the project directory
3. Verify `config/settings.py` is accessible

## 📝 Example Workflow

### Disable Admin for Production
```bash
# 1. Disable admin
python scripts/toggle_admin.py disable

# 2. Restart application
# (restart your Flask application)

# 3. Verify admin is hidden
# - Check role selection page
# - Verify navigation menu
# - Test admin routes
```

### Enable Admin for Development
```bash
# 1. Enable admin
python scripts/toggle_admin.py enable

# 2. Restart application
# (restart your Flask application)

# 3. Access admin features
# - Select admin role
# - Access admin dashboard
# - Configure JFrog settings
```

---

**🎯 The admin section is now temporarily disabled and can be easily toggled on/off as needed!**
