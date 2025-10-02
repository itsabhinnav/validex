# Text Configuration System

This document describes the centralized text configuration system for the Validex application, which allows you to manage all UI text strings from a single location.

## Overview

The text configuration system decouples all text strings from the application code, making it easy to:
- Change text content without modifying code
- Support multiple languages (future enhancement)
- Maintain consistency across the application
- Update text content without redeploying the application

## File Structure

```
config/
├── text_config.json          # Main text configuration file
app/
├── utils/
│   └── text_config.py         # Python utility for server-side text management
├── static/js/
│   └── text-config.js        # JavaScript configuration (auto-generated)
scripts/
└── generate_text_config.py   # Script to generate JS config from JSON
```

## Configuration File

The main configuration is stored in `config/text_config.json`. This file contains all text strings organized hierarchically:

```json
{
  "app": {
    "name": "Validex",
    "tagline": "Professional Test Case Management Platform"
  },
  "navigation": {
    "dashboard": "Dashboard",
    "test_cases": "Test Cases",
    "reports": "Reports"
  },
  "roles": {
    "admin": "Administrator",
    "tester": "Tester",
    "guest": "Guest"
  }
}
```

## Usage

### Server-Side (Python/Flask)

In your Flask templates, use the `get_text()` function:

```html
<!-- Instead of hardcoded text -->
<h1>Validex - Test Case Management Platform</h1>

<!-- Use text configuration -->
<h1>{{ get_text('app.name') }} - {{ get_text('app.tagline') }}</h1>
```

You can also use nested keys with dot notation:

```html
<p>{{ get_text('landing_page.hero_description') }}</p>
```

For lists and dictionaries:

```html
<!-- Get a list -->
{% for feature in get_text_list('landing_page.features.items') %}
  <li>{{ feature }}</li>
{% endfor %}

<!-- Get a dictionary -->
{% for role, title in get_text_dict('roles').items() %}
  <span>{{ title }}</span>
{% endfor %}
```

### Client-Side (JavaScript)

In your JavaScript files, use the `getText()` function:

```javascript
// Instead of hardcoded strings
alert('Execute test case');

// Use text configuration
alert(getText('javascript.execute_confirm', 'Execute test case'));
```

The JavaScript configuration is automatically generated from the JSON file and includes helper functions:

```javascript
// Basic usage
const appName = getText('app.name');

// With default value
const message = getText('non.existent.key', 'Default Message');

// With fallback
const text = getTextWithFallback('primary.key', 'fallback.key', 'Default');
```

## Available Functions

### Server-Side Functions

- `get_text(key_path, default="")` - Get a text value
- `get_text_dict(key_path, default={})` - Get a dictionary
- `get_text_list(key_path, default=[])` - Get a list
- `text_config.reload()` - Reload configuration from file

### Client-Side Functions

- `getText(keyPath, defaultValue="")` - Get a text value
- `getTextWithFallback(keyPath, fallbackKeyPath, defaultValue="")` - Get text with fallback

## Adding New Text

1. **Add to JSON configuration**: Edit `config/text_config.json` and add your text under the appropriate section.

2. **Update templates**: Replace hardcoded strings with `get_text()` calls.

3. **Update JavaScript**: Replace hardcoded strings with `getText()` calls.

4. **Regenerate JS config**: Run the generation script to update the JavaScript configuration:

```bash
python scripts/generate_text_config.py
```

## Configuration Sections

The text configuration is organized into the following main sections:

- `app` - Application name and basic information
- `navigation` - Navigation menu items
- `roles` - User role names
- `landing_page` - Landing page content
- `dashboard` - Dashboard page content
- `test_cases` - Test cases page content
- `admin` - Admin panel content
- `reports` - Reports page content
- `execute_test` - Test execution page content
- `statuses` - Test status labels
- `priorities` - Priority labels
- `environments` - Environment names
- `common` - Common UI elements
- `javascript` - JavaScript-specific messages

## Best Practices

1. **Use descriptive key names**: Choose clear, hierarchical key names that describe the content.

2. **Group related content**: Organize text into logical groups (e.g., `landing_page`, `dashboard`).

3. **Provide fallbacks**: Always provide default values for text that might not exist.

4. **Keep it simple**: Don't over-engineer the key structure - keep it flat where possible.

5. **Document changes**: When adding new text, document it in this file.

## Maintenance

### Updating Text Content

To change any text in the application:

1. Edit `config/text_config.json`
2. Run `python scripts/generate_text_config.py` to update JavaScript config
3. Restart the application (if needed)

### Adding New Languages (Future)

The system is designed to support multiple languages. To add language support:

1. Create language-specific JSON files (e.g., `text_config_es.json`)
2. Modify the text configuration loader to detect user language
3. Load the appropriate configuration file

## Testing

Run the test script to verify the text configuration system:

```bash
python test_text_config.py
```

This will test:
- Basic text retrieval
- Nested key access
- Default value handling
- Dictionary and list retrieval
- Flask integration
- Configuration reloading

## Troubleshooting

### Common Issues

1. **Text not appearing**: Check that the key path is correct and the JSON file is valid.

2. **JavaScript errors**: Ensure `text-config.js` is loaded before `main.js`.

3. **Path issues**: Verify the configuration file path is correct in `text_config.py`.

4. **Template errors**: Make sure you're using the correct function name (`get_text` not `getText` in templates).

### Debug Mode

Enable debug mode to see configuration loading:

```python
# In your Flask app
app.config['TEXT_CONFIG_DEBUG'] = True
```

## Future Enhancements

- [ ] Multi-language support
- [ ] Dynamic text loading from database
- [ ] Text validation and linting
- [ ] Translation management interface
- [ ] Text versioning and history
- [ ] A/B testing for text variations

## Contributing

When adding new text to the application:

1. Add the text to the appropriate section in `config/text_config.json`
2. Update the relevant templates to use `get_text()`
3. Update any JavaScript code to use `getText()`
4. Run the generation script
5. Test your changes
6. Update this documentation if needed


