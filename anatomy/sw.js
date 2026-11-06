// 人體圖離線：網頁、部位清單、說明與 three.js 先上網拿最新的，沒有網路時改用上次存下的。部位模型由網頁自己存（Cache Storage: anat-parts-*）。
const C = 'anat-shell-1';
self.addEventListener('install', e => self.skipWaiting());
self.addEventListener('activate', e => e.waitUntil(self.clients.claim()));
self.addEventListener('fetch', e => {
  const r = e.request, u = new URL(r.url);
  if (r.method !== 'GET' || r.headers.has('range')) return;
  const mine = u.origin === location.origin && u.pathname.includes('/anatomy/') && !u.pathname.includes('/data/pack/') && !u.pathname.includes('/data/hd/');
  const lib = u.hostname === 'cdn.jsdelivr.net' && u.pathname.includes('/three@0.160.0/');
  if (!mine && !lib) return;
  e.respondWith(fetch(r).then(res => { if (res.ok) { const cp = res.clone(); caches.open(C).then(c => c.put(r, cp)); } return res; })
    .catch(() => caches.match(r, { ignoreSearch: !lib }).then(x => x || Response.error())));
});
