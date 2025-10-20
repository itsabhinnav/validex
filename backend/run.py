
import os
import sys
import time
import webbrowser
import threading
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.mvc_app import create_mvc_app
from config.settings import config

def launch_browser(url, delay=2):
    """Launch browser after a delay"""
    def _launch():
        time.sleep(delay)
        try:
            webbrowser.open(url)
            print(f"Browser launched: {url}")
        except Exception as e:
            print(f"Failed to launch browser: {e}")
    
    thread = threading.Thread(target=_launch, daemon=True)
    thread.start()

def main():
    config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = create_mvc_app(config_name)
    host = os.environ.get('FLASK_HOST', config.get('app.host', '127.0.0.1'))
    port = int(os.environ.get('FLASK_PORT', config.get('app.port', 8000)))
    debug = os.environ.get('FLASK_DEBUG', str(config.get('app.debug', True))).lower() == 'true'
    
    if config_name == 'production':
        host = '127.0.0.1'
        debug = False
    
    url = f"http://{host}:{port}"
    
    print("Starting Validex Test Case Management System")
    print(f"Environment: {config_name}")
    print(f"Server: {url}")
    print(f"Debug: {debug}")
    print(f"Working Directory: {project_root}")
    
    # Auto-launch browser if enabled
    if config.is_auto_launch_browser_enabled():
        startup_delay = config.get_startup_delay()
        print(f"Auto-launching browser in {startup_delay} seconds...")
        launch_browser(url, startup_delay)
    else:
        print("Auto-launch browser is disabled")
    
    print("Server starting...")
    print("=" * 50)
    
    try:
        app.run(host=host, port=port, debug=debug, use_reloader=False)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Server error: {e}")

if __name__ == '__main__':
    main()
