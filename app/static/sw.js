

const CACHE_NAME = 'validex-v1.0.0';
const STATIC_CACHE_NAME = 'validex-static-v1.0.0';
const DYNAMIC_CACHE_NAME = 'validex-dynamic-v1.0.0';

const STATIC_FILES = [
  '/',
  '/static/css/main.css',
  '/static/js/main.js',
  '/static/js/text-config.js',
  '/static/manifest.json',
  '/static/icons/icon-192x192.png',
  '/static/icons/icon-512x512.png'
];

const API_ENDPOINTS = [
  '/api/test-cases',
  '/api/reports',
  '/api/dashboard'
];

self.addEventListener('install', event => {
  console.log('Service Worker: Installing...');
  
  event.waitUntil(
    caches.open(STATIC_CACHE_NAME)
      .then(cache => {
        console.log('Service Worker: Caching static files');
        return cache.addAll(STATIC_FILES);
      })
      .then(() => {
        console.log('Service Worker: Static files cached successfully');
        return self.skipWaiting();
      })
      .catch(error => {
        console.error('Service Worker: Error caching static files', error);
      })
  );
});

self.addEventListener('activate', event => {
  console.log('Service Worker: Activating...');
  
  event.waitUntil(
    caches.keys()
      .then(cacheNames => {
        return Promise.all(
          cacheNames.map(cacheName => {
            if (cacheName !== STATIC_CACHE_NAME && cacheName !== DYNAMIC_CACHE_NAME) {
              console.log('Service Worker: Deleting old cache', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        console.log('Service Worker: Activated successfully');
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

  if (url.pathname.startsWith('/static/')) {
    
    event.respondWith(cacheFirst(request));
  } else if (url.pathname.startsWith('/api/')) {
    
    event.respondWith(networkFirst(request));
  } else if (url.pathname === '/' || url.pathname.startsWith('/dashboard') || 
             url.pathname.startsWith('/test_cases') || url.pathname.startsWith('/reports')) {
    
    event.respondWith(cacheFirst(request));
  } else {
    
    event.respondWith(networkFirst(request));
  }
});

async function cacheFirst(request) {
  try {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      console.log('Service Worker: Serving from cache', request.url);
      return cachedResponse;
    }
    
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(STATIC_CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.error('Service Worker: Cache first error', error);
    return new Response('Offline - Content not available', {
      status: 503,
      statusText: 'Service Unavailable'
    });
  }
}

async function networkFirst(request) {
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(DYNAMIC_CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    console.log('Service Worker: Network failed, trying cache', request.url);
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }

    if (request.mode === 'navigate') {
      return caches.match('/') || new Response('Offline - App not available', {
        status: 503,
        statusText: 'Service Unavailable'
      });
    }
    
    throw error;
  }
}

self.addEventListener('sync', event => {
  console.log('Service Worker: Background sync', event.tag);
  
  if (event.tag === 'test-execution') {
    event.waitUntil(syncTestExecutions());
  }
});

self.addEventListener('push', event => {
  console.log('Service Worker: Push notification received');
  
  const options = {
    body: event.data ? event.data.text() : 'New notification from Validex',
    icon: '/static/icons/icon-192x192.png',
    badge: '/static/icons/icon-72x72.png',
    vibrate: [200, 100, 200],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: 'View Details',
        icon: '/static/icons/icon-96x96.png'
      },
      {
        action: 'close',
        title: 'Close',
        icon: '/static/icons/icon-96x96.png'
      }
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification('Validex', options)
  );
});

self.addEventListener('notificationclick', event => {
  console.log('Service Worker: Notification clicked');
  
  event.notification.close();
  
  if (event.action === 'explore') {
    event.waitUntil(
      clients.openWindow('/dashboard')
    );
  }
});

async function syncTestExecutions() {
  try {
    
    console.log('Service Worker: Syncing test executions');
    
  } catch (error) {
    console.error('Service Worker: Error syncing test executions', error);
  }
}

self.addEventListener('message', event => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  
  if (event.data && event.data.type === 'GET_VERSION') {
    event.ports[0].postMessage({ version: CACHE_NAME });
  }
});
