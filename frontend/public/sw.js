self.addEventListener('install', (event) => {
  event.waitUntil(self.skipWaiting());
});

self.addEventListener('activate', (event) => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', (event) => {
  if (event.request.mode === 'navigate') {
    event.respondWith(
      fetch(event.request).catch(() => {
        return new Response(
          '<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Ofertas Super + Menú Semanal IA</title></head><body><div id="root"></div><script type="module" src="/src/main.tsx"></script></body></html>',
          {
            headers: { 'Content-Type': 'text/html' }
          }
        );
      })
    );
  }
});