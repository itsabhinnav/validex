# Progressive Web App (PWA) Guide for Validex

This guide explains how to use Validex as a Progressive Web App (PWA) that can be installed and run as a standalone desktop application.

## What is a PWA?

A Progressive Web App (PWA) is a web application that can be installed on your device and run like a native desktop application. It provides:

- **Standalone Experience**: Runs in its own window without browser UI
- **Offline Functionality**: Works even when you're not connected to the internet
- **Native Feel**: Behaves like a desktop application
- **Automatic Updates**: Updates itself when new versions are available

## Installing Validex as a PWA

### Method 1: Browser Install Prompt

1. **Open Validex** in Chrome, Edge, or Firefox
2. **Look for the install button** in the bottom-right corner of the screen
3. **Click "Install App"** when the prompt appears
4. **Follow the installation wizard** to add Validex to your desktop

### Method 2: Browser Menu Installation

#### Chrome/Edge:
1. Click the **three dots menu** (⋮) in the browser toolbar
2. Select **"Install Validex..."** from the menu
3. Click **"Install"** in the popup dialog

#### Firefox:
1. Click the **three lines menu** (☰) in the browser toolbar
2. Select **"Install"** from the menu
3. Click **"Add"** in the installation dialog

### Method 3: Address Bar Installation

1. Look for the **install icon** (⬇️) in the address bar
2. Click the install icon
3. Follow the installation prompts

## Using the Installed PWA

### Launching the App

Once installed, you can launch Validex like any other desktop application:

- **Windows**: Look for "Validex" in your Start Menu or desktop
- **macOS**: Find "Validex" in your Applications folder or Launchpad
- **Linux**: Check your applications menu

### App Features

The installed PWA provides:

- **Standalone Window**: Runs without browser interface
- **Desktop Integration**: Appears in your taskbar/dock
- **Offline Access**: Works without internet connection
- **Native Shortcuts**: Right-click context menus and keyboard shortcuts
- **Auto-Updates**: Automatically updates when new versions are available

## Offline Functionality

### What Works Offline

- **Viewing Test Cases**: Browse previously loaded test cases
- **Dashboard**: View cached dashboard data
- **Navigation**: Move between pages you've visited
- **Basic Functionality**: Most core features remain available

### What Requires Internet

- **New Data Loading**: Fetching new test cases or reports
- **File Uploads**: Uploading new Excel files
- **Real-time Updates**: Live data synchronization
- **User Authentication**: Login/logout functionality

### Offline Indicators

When you're offline, you'll see:
- **Warning Banner**: "You are offline. Some features may not be available."
- **Limited Functionality**: Some buttons may be disabled
- **Cached Content**: Previously loaded content remains accessible

## PWA Shortcuts

The installed app includes shortcuts for quick access:

- **Dashboard**: Direct access to the main dashboard
- **Test Cases**: Quick jump to test case management
- **Reports**: Fast access to reporting features

## Troubleshooting

### Installation Issues

**Problem**: Install button doesn't appear
**Solution**: 
- Ensure you're using Chrome, Edge, or Firefox
- Check that the site is served over HTTPS (required for PWA)
- Clear browser cache and try again

**Problem**: Installation fails
**Solution**:
- Check your internet connection
- Ensure you have sufficient disk space
- Try refreshing the page and attempting installation again

### Offline Issues

**Problem**: App doesn't work offline
**Solution**:
- Visit the app while online first to cache content
- Check that service worker is registered (look in browser dev tools)
- Clear browser cache and revisit the site

**Problem**: Data not syncing when back online
**Solution**:
- Refresh the app when you regain internet connection
- Check that the service worker is active
- Clear browser cache if issues persist

### Update Issues

**Problem**: App doesn't update automatically
**Solution**:
- Close and reopen the app
- Check for updates in browser settings
- Clear app cache and reinstall if necessary

## Development and Customization

### Service Worker

The PWA uses a service worker for offline functionality:
- **Location**: `/static/sw.js`
- **Features**: Caching, offline support, background sync
- **Updates**: Automatically updates when new versions are deployed

### Manifest Configuration

App behavior is controlled by the manifest file:
- **Location**: `/static/manifest.json`
- **Settings**: App name, icons, display mode, shortcuts
- **Customization**: Modify to change app appearance and behavior

### Icons

PWA icons are located in `/static/icons/`:
- **Multiple Sizes**: 16x16 to 512x512 pixels
- **Formats**: SVG for scalability
- **Customization**: Replace with your own designs

## Best Practices

### For Users

1. **Install the PWA**: Get the full desktop experience
2. **Use Offline**: Take advantage of offline functionality
3. **Keep Updated**: Allow automatic updates for best experience
4. **Bookmark Shortcuts**: Use the provided shortcuts for quick access

### For Developers

1. **Test Installation**: Verify PWA installation works across browsers
2. **Test Offline**: Ensure offline functionality works as expected
3. **Update Icons**: Replace placeholder icons with custom designs
4. **Monitor Performance**: Check service worker performance in dev tools

## Browser Support

### Full PWA Support
- **Chrome**: 67+
- **Edge**: 79+
- **Firefox**: 60+
- **Safari**: 11.1+ (limited)

### Installation Support
- **Chrome**: Full support
- **Edge**: Full support  
- **Firefox**: Full support
- **Safari**: Limited support

## Security Considerations

- **HTTPS Required**: PWAs only work over secure connections
- **Service Worker Scope**: Limited to the app's domain
- **Cache Security**: Cached data is isolated per origin
- **Update Security**: Updates are verified before installation

## Performance Tips

1. **Pre-cache Important Pages**: Visit key pages while online
2. **Clear Cache When Needed**: Use browser dev tools to manage cache
3. **Monitor Storage**: Check storage usage in browser settings
4. **Update Regularly**: Keep the app updated for best performance

## Support

If you encounter issues with the PWA:

1. **Check Browser Compatibility**: Ensure you're using a supported browser
2. **Clear Cache**: Try clearing browser cache and cookies
3. **Reinstall**: Uninstall and reinstall the PWA
4. **Contact Support**: Reach out for technical assistance

---

**Note**: PWA functionality requires a modern browser with service worker support. For the best experience, use Chrome, Edge, or Firefox on a desktop or mobile device.


