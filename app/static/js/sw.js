/**
 * Service Worker for Validex PWA
 * Provides offline support and caching
 */

const CACHE_NAME = 'validex-v1';
const STATIC_CACHE = 'validex-static-v1';
const DYNAMIC_CACHE = 'validex-dynamic-v1';

// Files to cache immediately
const STATIC_FILES = [
    '/',
    '/static/css/main.css',
    '/static/js/main.js',
    '/static/js/charts.js',
    '/static/js/bulk-operations.js',
    '/static/js/advanced-search.js',
    '/static/js/pwa-enhancements.js',
    '/static/manifest.json',
    '/static/icons/icon-192x192.png',
    '/static/icons/icon-512x512.png'
];

// Install event - cache static files
self.addEventListener('install', event => {
    console.log('Service Worker installing...');
    
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then(cache => {
                console.log('Caching static files...');
                return cache.addAll(STATIC_FILES);
            })
            .then(() => {
                console.log('Static files cached successfully');
                return self.skipWaiting();
            })
            .catch(error => {
                console.error('Failed to cache static files:', error);
            })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
    console.log('Service Worker activating...');
    
    event.waitUntil(
        caches.keys()
            .then(cacheNames => {
                return Promise.all(
                    cacheNames.map(cacheName => {
                        if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
                            console.log('Deleting old cache:', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            })
            .then(() => {
                console.log('Service Worker activated');
                return self.clients.claim();
            })
    );
});

// Fetch event - serve from cache or network
self.addEventListener('fetch', event => {
    const { request } = event;
    const url = new URL(request.url);
    
    // Skip non-GET requests
    if (request.method !== 'GET') {
        return;
    }
    
    // Skip external requests
    if (url.origin !== location.origin) {
        return;
    }
    
    event.respondWith(
        caches.match(request)
            .then(cachedResponse => {
                if (cachedResponse) {
                    console.log('Serving from cache:', request.url);
                    return cachedResponse;
                }
                
                return fetch(request)
                    .then(response => {
                        // Don't cache non-successful responses
                        if (!response || response.status !== 200 || response.type !== 'basic') {
                            return response;
                        }
                        
                        // Clone the response
                        const responseToCache = response.clone();
                        
                        // Cache dynamic content
                        caches.open(DYNAMIC_CACHE)
                            .then(cache => {
                                cache.put(request, responseToCache);
                            });
                        
                        return response;
                    })
                    .catch(error => {
                        console.log('Network request failed:', request.url);
                        
                        // Return offline page for navigation requests
                        if (request.mode === 'navigate') {
                            return caches.match('/offline.html');
                        }
                        
                        // Return cached version for other requests
                        return caches.match(request);
                    });
            })
    );
});

// Background sync event
self.addEventListener('sync', event => {
    console.log('Background sync triggered:', event.tag);
    
    if (event.tag === 'validex-sync') {
        event.waitUntil(
            syncOfflineData()
        );
    }
});

// Push notification event
self.addEventListener('push', event => {
    console.log('Push notification received');
    
    const options = {
        body: event.data ? event.data.text() : 'New notification from Validex',
        icon: '/static/icons/icon-192x192.png',
        badge: '/static/icons/icon-72x72.png',
        tag: 'validex-notification',
        actions: [
            {
                action: 'open',
                title: 'Open App'
            },
            {
                action: 'close',
                title: 'Close'
            }
        ]
    };
    
    event.waitUntil(
        self.registration.showNotification('Validex', options)
    );
});

// Notification click event
self.addEventListener('notificationclick', event => {
    console.log('Notification clicked:', event.action);
    
    event.notification.close();
    
    if (event.action === 'open') {
        event.waitUntil(
            clients.openWindow('/')
        );
    }
});

// Message event - handle messages from main thread
self.addEventListener('message', event => {
    console.log('Message received in service worker:', event.data);
    
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
    
    if (event.data && event.data.type === 'CACHE_URLS') {
        event.waitUntil(
            cacheUrls(event.data.urls)
        );
    }
});

// Helper function to sync offline data
async function syncOfflineData() {
    try {
        console.log('Syncing offline data...');
        
        // Get offline data from IndexedDB or localStorage
        const offlineData = await getOfflineData();
        
        // Sync each item
        for (const item of offlineData) {
            try {
                await fetch(item.url, item.options);
                console.log('Synced:', item.url);
            } catch (error) {
                console.log('Sync failed for:', item.url);
            }
        }
        
        console.log('Offline data sync completed');
    } catch (error) {
        console.error('Offline sync failed:', error);
    }
}

// Helper function to get offline data
async function getOfflineData() {
    // This would typically get data from IndexedDB
    // For now, return empty array
    return [];
}

// Helper function to cache URLs
async function cacheUrls(urls) {
    const cache = await caches.open(DYNAMIC_CACHE);
    
    for (const url of urls) {
        try {
            const response = await fetch(url);
            if (response.ok) {
                await cache.put(url, response);
                console.log('Cached:', url);
            }
        } catch (error) {
            console.log('Failed to cache:', url);
        }
    }
}

// Periodic background sync (if supported)
if ('serviceWorker' in navigator && 'periodicSync' in window.ServiceWorkerRegistration.prototype) {
    self.addEventListener('periodicsync', event => {
        if (event.tag === 'validex-periodic-sync') {
            event.waitUntil(
                performPeriodicSync()
            );
        }
    });
}

// Helper function for periodic sync
async function performPeriodicSync() {
    try {
        console.log('Performing periodic sync...');
        
        // Sync data with server
        const response = await fetch('/api/sync');
        if (response.ok) {
            console.log('Periodic sync completed');
        }
    } catch (error) {
        console.log('Periodic sync failed:', error);
    }
}
