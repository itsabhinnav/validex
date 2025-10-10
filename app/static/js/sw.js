

const CACHE_NAME = 'validex-v1';
const STATIC_CACHE = 'validex-static-v1';
const DYNAMIC_CACHE = 'validex-dynamic-v1';

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

self.addEventListener('fetch', event => {
    const { request } = event;
    const url = new URL(request.url);

    if (request.method !== 'GET') {
        return;
    }

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
                        
                        if (!response || response.status !== 200 || response.type !== 'basic') {
                            return response;
                        }

                        const responseToCache = response.clone();

                        caches.open(DYNAMIC_CACHE)
                            .then(cache => {
                                cache.put(request, responseToCache);
                            });
                        
                        return response;
                    })
                    .catch(error => {
                        console.log('Network request failed:', request.url);

                        if (request.mode === 'navigate') {
                            return caches.match('/offline.html');
                        }

                        return caches.match(request);
                    });
            })
    );
});

self.addEventListener('sync', event => {
    console.log('Background sync triggered:', event.tag);
    
    if (event.tag === 'validex-sync') {
        event.waitUntil(
            syncOfflineData()
        );
    }
});

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

self.addEventListener('notificationclick', event => {
    console.log('Notification clicked:', event.action);
    
    event.notification.close();
    
    if (event.action === 'open') {
        event.waitUntil(
            clients.openWindow('/')
        );
    }
});

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

async function syncOfflineData() {
    try {
        console.log('Syncing offline data...');

        const offlineData = await getOfflineData();

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

async function getOfflineData() {

    return [];
}

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

if ('serviceWorker' in navigator && 'periodicSync' in window.ServiceWorkerRegistration.prototype) {
    self.addEventListener('periodicsync', event => {
        if (event.tag === 'validex-periodic-sync') {
            event.waitUntil(
                performPeriodicSync()
            );
        }
    });
}

async function performPeriodicSync() {
    try {
        console.log('Performing periodic sync...');

        const response = await fetch('/api/sync');
        if (response.ok) {
            console.log('Periodic sync completed');
        }
    } catch (error) {
        console.log('Periodic sync failed:', error);
    }
}
