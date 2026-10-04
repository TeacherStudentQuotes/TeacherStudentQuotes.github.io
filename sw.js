const CACHE = 'tsq-v91';
const CORE = [
  '.',
  'index.html',
  'quotes.js',
  'manifest.json',
  'fonts/STZHONGS.subset.woff2',
  'fonts/cmu.serif-roman.woff2',
  'img/favicon.ico',
  'img/cry.png',
];

self.addEventListener('message', (e) => {
  if (e.data && e.data.type === 'SKIP_WAITING') self.skipWaiting();
  if (e.data && e.data.type === 'GET_VERSION' && e.source) {
    e.source.postMessage({ type: 'VERSION', version: CACHE });
  }
});

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(CORE)));
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

// CDN 资源：缓存优先，后台更新
self.addEventListener('fetch', (e) => {
  const url = new URL(e.request.url);
  if (e.request.method !== 'GET') return;

  // 同源：网络优先（名言数据要及时），失败回缓存
  if (url.origin === location.origin) {
    e.respondWith(
      fetch(e.request)
        .then((res) => {
          // 只缓存完整响应（206 Range等partial response不支持put）
          if (res.status === 200 && (res.type === 'basic' || res.type === 'cors')) {
            const clone = res.clone();
            caches.open(CACHE).then((c) => c.put(e.request, clone)).catch(() => {});
          }
          return res;
        })
        .catch(() => caches.match(e.request))
    );
    return;
  }

  // 跨域 CDN（bootstrap-icons、KaTeX）：缓存优先
  e.respondWith(
    caches.match(e.request).then(
      (hit) =>
        hit ||
        fetch(e.request).then((res) => {
          if (res.ok) {
            const clone = res.clone();
            caches.open(CACHE).then((c) => c.put(e.request, clone));
          }
          return res;
        })
    )
  );
});
