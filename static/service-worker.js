
/* Archivo: static/service-worker.js */
const CACHE_NAME = 'plents-cache-v1';
const urlsToCache = [
  '/',
  '/home',
  '/plants',
  '/my_plants',
  '/static/style.css',
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request);
    })
  );
});

