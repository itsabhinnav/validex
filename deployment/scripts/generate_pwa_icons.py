#!/usr/bin/env python3
"""
Script to generate PWA icons for Validex application.
Creates simple placeholder icons that can be replaced with proper designs.
"""

import os
from pathlib import Path

def create_simple_icon(size, filename):
    """Create a simple SVG icon that can be converted to PNG."""
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#007bff;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#0056b3;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="{size}" height="{size}" rx="{size//8}" fill="url(#grad1)"/>
  <text x="50%" y="50%" font-family="Arial, sans-serif" font-size="{size//3}" font-weight="bold" 
        text-anchor="middle" dominant-baseline="middle" fill="white">V</text>
</svg>'''
    
    return svg_content

def create_icon_files():
    """Create all required icon files."""
    icons_dir = Path(__file__).parent.parent / 'app' / 'static' / 'icons'
    icons_dir.mkdir(parents=True, exist_ok=True)
    
    # Icon sizes needed for PWA
    icon_sizes = [
        16, 32, 57, 60, 72, 76, 96, 114, 120, 128, 144, 152, 180, 192, 384, 512
    ]
    
    print("Generating PWA icons...")
    
    for size in icon_sizes:
        filename = f"icon-{size}x{size}.svg"
        filepath = icons_dir / filename
        
        svg_content = create_simple_icon(size, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        print(f"Created {filename}")
    
    # Create shortcut icons
    shortcut_icons = [
        ('shortcut-dashboard.png', 'Dashboard'),
        ('shortcut-test-cases.png', 'Test Cases'),
        ('shortcut-reports.png', 'Reports')
    ]
    
    for filename, label in shortcut_icons:
        filepath = icons_dir / filename
        # Create a simple SVG for shortcuts too
        svg_content = create_simple_icon(96, filename)
        
        with open(str(filepath).replace('.png', '.svg'), 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        print(f"Created {filename.replace('.png', '.svg')}")
    
    print("\nPWA icons generated successfully!")
    print("Note: These are SVG placeholders. For production, convert to PNG format.")
    print("You can use online tools like https://convertio.co/svg-png/ to convert them.")

def create_browserconfig():
    """Create browserconfig.xml for Windows tiles."""
    browserconfig_content = '''<?xml version="1.0" encoding="utf-8"?>
<browserconfig>
    <msapplication>
        <tile>
            <square150x150logo src="/static/icons/icon-152x152.png"/>
            <TileColor>#007bff</TileColor>
        </tile>
    </msapplication>
</browserconfig>'''
    
    static_dir = Path(__file__).parent.parent / 'app' / 'static'
    browserconfig_path = static_dir / 'browserconfig.xml'
    
    with open(browserconfig_path, 'w', encoding='utf-8') as f:
        f.write(browserconfig_content)
    
    print("Created browserconfig.xml")

def main():
    """Main function."""
    print("=" * 50)
    print("PWA Icon Generator for Validex")
    print("=" * 50)
    
    try:
        create_icon_files()
        create_browserconfig()
        
        print("\n" + "=" * 50)
        print("✅ PWA setup completed successfully!")
        print("=" * 50)
        print("\nNext steps:")
        print("1. Convert SVG icons to PNG format for better compatibility")
        print("2. Replace placeholder icons with your custom designs")
        print("3. Test PWA installation in Chrome/Edge")
        print("4. Verify offline functionality")
        
    except Exception as e:
        print(f"❌ Error generating PWA icons: {e}")
        return False
    
    return True

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
