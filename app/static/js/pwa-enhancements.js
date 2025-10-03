/**
 * PWA Enhancements for Validex
 * Mobile responsiveness, offline support, and app-like experience
 */

class PWAEnhancements {
    constructor() {
        this.isOnline = navigator.onLine;
        this.offlineData = new Map();
        this.syncQueue = [];
        this.init();
    }

    init() {
        this.registerServiceWorker();
        this.setupOfflineSupport();
        this.enhanceMobileExperience();
        this.setupPushNotifications();
        this.setupBackgroundSync();
        this.addTouchGestures();
        this.optimizeForMobile();
    }

    registerServiceWorker() {
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/static/js/sw.js')
                .then(registration => {
                    console.log('Service Worker registered:', registration);
                    this.setupUpdateNotification(registration);
                })
                .catch(error => {
                    console.log('Service Worker registration failed:', error);
                });
        }
    }

    setupOfflineSupport() {
        // Cache critical resources
        this.cacheCriticalResources();
        
        // Handle online/offline events
        window.addEventListener('online', () => {
            this.isOnline = true;
            this.showOnlineStatus();
            this.syncOfflineData();
        });

        window.addEventListener('offline', () => {
            this.isOnline = false;
            this.showOfflineStatus();
        });

        // Intercept fetch requests for offline support
        this.setupFetchInterception();
    }

    cacheCriticalResources() {
        const criticalResources = [
            '/static/css/main.css',
            '/static/js/main.js',
            '/static/js/charts.js',
            '/static/js/bulk-operations.js',
            '/static/js/advanced-search.js',
            '/static/js/pwa-enhancements.js',
            '/static/manifest.json'
        ];

        if ('caches' in window) {
            caches.open('validex-critical-v1').then(cache => {
                cache.addAll(criticalResources);
            });
        }
    }

    setupFetchInterception() {
        const originalFetch = window.fetch;
        window.fetch = async (url, options) => {
            try {
                const response = await originalFetch(url, options);
                return response;
            } catch (error) {
                if (!this.isOnline) {
                    return this.handleOfflineRequest(url, options);
                }
                throw error;
            }
        };
    }

    async handleOfflineRequest(url, options) {
        // Check if we have cached data
        const cache = await caches.open('validex-data-v1');
        const cachedResponse = await cache.match(url);
        
        if (cachedResponse) {
            return cachedResponse;
        }

        // Store request for later sync
        this.syncQueue.push({ url, options, timestamp: Date.now() });
        
        // Return offline response
        return new Response(JSON.stringify({
            offline: true,
            message: 'You are offline. Data will sync when connection is restored.',
            data: this.offlineData.get(url) || []
        }), {
            headers: { 'Content-Type': 'application/json' }
        });
    }

    showOnlineStatus() {
        this.showToast('Connection restored', 'success');
    }

    showOfflineStatus() {
        this.showToast('You are offline. Some features may be limited.', 'warning');
    }

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast-notification toast-${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'warning' ? 'exclamation-triangle' : 'info-circle'} me-2"></i>
                ${message}
            </div>
        `;

        // Add toast styles
        if (!document.querySelector('#toast-styles')) {
            const style = document.createElement('style');
            style.id = 'toast-styles';
            style.textContent = `
                .toast-notification {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: white;
                    border-radius: 10px;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
                    padding: 15px 20px;
                    z-index: 10000;
                    animation: slideInRight 0.3s ease;
                }
                .toast-success { border-left: 4px solid #28a745; }
                .toast-warning { border-left: 4px solid #ffc107; }
                .toast-info { border-left: 4px solid #17a2b8; }
                .toast-content {
                    display: flex;
                    align-items: center;
                    font-weight: 500;
                }
                @keyframes slideInRight {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
            `;
            document.head.appendChild(style);
        }

        document.body.appendChild(toast);

        // Auto remove after 3 seconds
        setTimeout(() => {
            toast.style.animation = 'slideInRight 0.3s ease reverse';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    enhanceMobileExperience() {
        // Add mobile-specific styles
        this.addMobileStyles();
        
        // Enhance touch interactions
        this.enhanceTouchInteractions();
        
        // Add pull-to-refresh
        this.addPullToRefresh();
        
        // Optimize for mobile viewport
        this.optimizeViewport();
    }

    addMobileStyles() {
        const style = document.createElement('style');
        style.textContent = `
            @media (max-width: 768px) {
                .container {
                    padding: 10px;
                }
                
                .card {
                    margin-bottom: 15px;
                    border-radius: 15px;
                }
                
                .btn {
                    padding: 12px 20px;
                    font-size: 1rem;
                    border-radius: 25px;
                }
                
                .table-responsive {
                    border-radius: 15px;
                    overflow: hidden;
                }
                
                .navbar-brand {
                    font-size: 1.2rem;
                }
                
                .search-input {
                    font-size: 16px; /* Prevents zoom on iOS */
                }
                
                .floating-actions {
                    bottom: 20px;
                    right: 20px;
                }
                
                .floating-btn {
                    width: 50px;
                    height: 50px;
                    font-size: 1rem;
                }
                
                .bulk-toolbar {
                    bottom: 10px;
                    left: 10px;
                    right: 10px;
                    transform: none;
                    border-radius: 25px;
                    padding: 10px 15px;
                }
                
                .chart-container {
                    height: 250px;
                    margin-bottom: 15px;
                }
                
                .metric-card {
                    margin-bottom: 15px;
                }
                
                .dashboard-header {
                    padding: 20px;
                    margin-bottom: 20px;
                }
                
                .test-execution-container {
                    padding: 10px 0;
                }
                
                .test-card {
                    margin-bottom: 15px;
                }
                
                .execution-form {
                    margin-bottom: 15px;
                }
            }
            
            @media (max-width: 576px) {
                .col-lg-8, .col-lg-4 {
                    margin-bottom: 15px;
                }
                
                .result-buttons {
                    grid-template-columns: 1fr;
                    gap: 10px;
                }
                
                .timer-controls {
                    flex-direction: column;
                    gap: 5px;
                }
                
                .timer-btn {
                    padding: 6px 12px;
                    font-size: 0.8rem;
                }
            }
        `;
        document.head.appendChild(style);
    }

    enhanceTouchInteractions() {
        // Add touch feedback to buttons
        document.addEventListener('touchstart', (e) => {
            if (e.target.matches('.btn, .card, .floating-btn, .bulk-btn')) {
                e.target.style.transform = 'scale(0.95)';
            }
        });

        document.addEventListener('touchend', (e) => {
            if (e.target.matches('.btn, .card, .floating-btn, .bulk-btn')) {
                setTimeout(() => {
                    e.target.style.transform = '';
                }, 150);
            }
        });

        // Add swipe gestures
        this.addSwipeGestures();
    }

    addSwipeGestures() {
        let startX, startY, endX, endY;

        document.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
        });

        document.addEventListener('touchend', (e) => {
            endX = e.changedTouches[0].clientX;
            endY = e.changedTouches[0].clientY;
            
            const deltaX = endX - startX;
            const deltaY = endY - startY;
            
            // Swipe right - go back
            if (deltaX > 100 && Math.abs(deltaY) < 100) {
                if (window.history.length > 1) {
                    window.history.back();
                }
            }
            
            // Swipe left - refresh
            if (deltaX < -100 && Math.abs(deltaY) < 100) {
                this.refreshData();
            }
        });
    }

    addPullToRefresh() {
        let startY = 0;
        let currentY = 0;
        let isRefreshing = false;

        document.addEventListener('touchstart', (e) => {
            if (window.scrollY === 0) {
                startY = e.touches[0].clientY;
            }
        });

        document.addEventListener('touchmove', (e) => {
            if (window.scrollY === 0 && startY > 0) {
                currentY = e.touches[0].clientY;
                const deltaY = currentY - startY;
                
                if (deltaY > 0) {
                    e.preventDefault();
                    this.showPullToRefreshIndicator(deltaY);
                }
            }
        });

        document.addEventListener('touchend', (e) => {
            if (startY > 0) {
                const deltaY = currentY - startY;
                
                if (deltaY > 100 && !isRefreshing) {
                    this.triggerRefresh();
                } else {
                    this.hidePullToRefreshIndicator();
                }
                
                startY = 0;
                currentY = 0;
            }
        });
    }

    showPullToRefreshIndicator(deltaY) {
        let indicator = document.querySelector('.pull-to-refresh');
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.className = 'pull-to-refresh';
            indicator.innerHTML = `
                <div class="pull-indicator">
                    <i class="fas fa-arrow-down"></i>
                    <span>Pull to refresh</span>
                </div>
            `;
            document.body.insertBefore(indicator, document.body.firstChild);
        }
        
        const progress = Math.min(deltaY / 100, 1);
        indicator.style.transform = `translateY(${deltaY}px)`;
        indicator.style.opacity = progress;
    }

    hidePullToRefreshIndicator() {
        const indicator = document.querySelector('.pull-to-refresh');
        if (indicator) {
            indicator.style.transform = 'translateY(-100%)';
            indicator.style.opacity = '0';
        }
    }

    triggerRefresh() {
        const indicator = document.querySelector('.pull-to-refresh');
        if (indicator) {
            indicator.innerHTML = `
                <div class="pull-indicator">
                    <i class="fas fa-spinner fa-spin"></i>
                    <span>Refreshing...</span>
                </div>
            `;
        }
        
        this.refreshData().then(() => {
            setTimeout(() => {
                this.hidePullToRefreshIndicator();
            }, 1000);
        });
    }

    async refreshData() {
        // Refresh data from server
        try {
            const response = await fetch('/api/refresh-data');
            if (response.ok) {
                this.showToast('Data refreshed successfully', 'success');
            }
        } catch (error) {
            console.log('Refresh failed:', error);
        }
    }

    optimizeViewport() {
        // Add viewport meta tag if not present
        if (!document.querySelector('meta[name="viewport"]')) {
            const viewport = document.createElement('meta');
            viewport.name = 'viewport';
            viewport.content = 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no';
            document.head.appendChild(viewport);
        }

        // Prevent zoom on input focus (iOS)
        const inputs = document.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('focus', () => {
                if (window.innerWidth < 768) {
                    setTimeout(() => {
                        window.scrollTo(0, 0);
                    }, 300);
                }
            });
        });
    }

    setupPushNotifications() {
        if ('Notification' in window && 'serviceWorker' in navigator) {
            this.requestNotificationPermission();
        }
    }

    async requestNotificationPermission() {
        if (Notification.permission === 'default') {
            const permission = await Notification.requestPermission();
            if (permission === 'granted') {
                this.showToast('Notifications enabled', 'success');
            }
        }
    }

    showNotification(title, body, icon = '/static/icons/icon-192x192.png') {
        if (Notification.permission === 'granted') {
            new Notification(title, {
                body: body,
                icon: icon,
                badge: '/static/icons/icon-72x72.png',
                tag: 'validex-notification'
            });
        }
    }

    setupBackgroundSync() {
        if ('serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype) {
            navigator.serviceWorker.ready.then(registration => {
                // Register background sync for offline actions
                registration.sync.register('validex-sync');
            });
        }
    }

    syncOfflineData() {
        if (this.syncQueue.length > 0) {
            this.showToast('Syncing offline data...', 'info');
            
            // Process sync queue
            this.syncQueue.forEach(async (item) => {
                try {
                    await fetch(item.url, item.options);
                } catch (error) {
                    console.log('Sync failed for:', item.url);
                }
            });
            
            this.syncQueue = [];
            this.showToast('Offline data synced', 'success');
        }
    }

    addTouchGestures() {
        // Add touch gesture support for better mobile experience
        this.addLongPressGesture();
        this.addDoubleTapGesture();
    }

    addLongPressGesture() {
        let longPressTimer;
        
        document.addEventListener('touchstart', (e) => {
            longPressTimer = setTimeout(() => {
                this.handleLongPress(e);
            }, 500);
        });

        document.addEventListener('touchend', () => {
            clearTimeout(longPressTimer);
        });

        document.addEventListener('touchmove', () => {
            clearTimeout(longPressTimer);
        });
    }

    handleLongPress(e) {
        const target = e.target.closest('[data-long-press]');
        if (target) {
            const action = target.dataset.longPress;
            this.executeLongPressAction(action, target);
        }
    }

    executeLongPressAction(action, element) {
        switch (action) {
            case 'select':
                this.toggleSelection(element);
                break;
            case 'context-menu':
                this.showContextMenu(element);
                break;
        }
    }

    addDoubleTapGesture() {
        let lastTap = 0;
        
        document.addEventListener('touchend', (e) => {
            const currentTime = new Date().getTime();
            const tapLength = currentTime - lastTap;
            
            if (tapLength < 500 && tapLength > 0) {
                this.handleDoubleTap(e);
            }
            
            lastTap = currentTime;
        });
    }

    handleDoubleTap(e) {
        const target = e.target.closest('[data-double-tap]');
        if (target) {
            const action = target.dataset.doubleTap;
            this.executeDoubleTapAction(action, target);
        }
    }

    executeDoubleTapAction(action, element) {
        switch (action) {
            case 'zoom':
                this.toggleZoom(element);
                break;
            case 'favorite':
                this.toggleFavorite(element);
                break;
        }
    }

    optimizeForMobile() {
        // Add mobile-specific optimizations
        this.optimizeImages();
        this.optimizeTables();
        this.addMobileNavigation();
    }

    optimizeImages() {
        // Lazy load images
        const images = document.querySelectorAll('img[data-src]');
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    imageObserver.unobserve(img);
                }
            });
        });

        images.forEach(img => imageObserver.observe(img));
    }

    optimizeTables() {
        // Make tables more mobile-friendly
        const tables = document.querySelectorAll('table');
        tables.forEach(table => {
            if (window.innerWidth < 768) {
                table.classList.add('table-mobile');
            }
        });
    }

    addMobileNavigation() {
        // Add mobile navigation enhancements
        const navbar = document.querySelector('.navbar');
        if (navbar && window.innerWidth < 768) {
            navbar.classList.add('navbar-mobile');
        }
    }
}

// Initialize PWA enhancements when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.pwaEnhancements = new PWAEnhancements();
});

// Add mobile-specific styles
const mobileStyles = document.createElement('style');
mobileStyles.textContent = `
    .pull-to-refresh {
        position: fixed;
        top: -60px;
        left: 0;
        right: 0;
        height: 60px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
        transition: all 0.3s ease;
    }
    
    .pull-indicator {
        display: flex;
        align-items: center;
        gap: 10px;
        font-weight: 500;
    }
    
    .table-mobile {
        font-size: 0.9rem;
    }
    
    .table-mobile th,
    .table-mobile td {
        padding: 8px 4px;
    }
    
    .navbar-mobile .navbar-brand {
        font-size: 1.1rem;
    }
    
    .navbar-mobile .navbar-nav {
        flex-direction: column;
        width: 100%;
    }
    
    .navbar-mobile .nav-item {
        width: 100%;
        text-align: center;
        padding: 10px 0;
        border-bottom: 1px solid #dee2e6;
    }
`;
document.head.appendChild(mobileStyles);
