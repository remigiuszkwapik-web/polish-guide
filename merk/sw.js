// Merk Service Worker: App offline verfügbar machen.
// Bei jeder Änderung an merk/index.html o. Ä. VERSION hochzählen, damit Geräte die neue Fassung laden.
// Alle Caches beginnen mit "merk-", damit sie sich nicht mit Kroks Caches (krok-…) in die Quere kommen.
const VERSION = "merk-v1";
const EXTERN = "merk-extern"; // Schriften und KaTeX
const SHELL = [
  "./",
  "./index.html",
  "./manifest.webmanifest",
  "./icons/icon.svg",
  "./icons/icon-192.png",
  "./icons/icon-512.png",
  "./icons/apple-touch-icon.png"
];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(VERSION).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k.startsWith("merk-") && k !== VERSION && k !== EXTERN).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);

  // Google Fonts und KaTeX: einmal laden, dann aus dem Cache
  if (["fonts.googleapis.com", "fonts.gstatic.com", "cdnjs.cloudflare.com"].includes(url.hostname)) {
    e.respondWith(
      caches.open(EXTERN).then(async (c) => {
        const hit = await c.match(req);
        if (hit) return hit;
        const res = await fetch(req);
        if (res.ok || res.type === "opaque") c.put(req, res.clone());
        return res;
      })
    );
    return;
  }

  if (url.origin !== location.origin) return;

  // Seite selbst: erst Netz (frische Version), offline aus dem Cache
  if (req.mode === "navigate") {
    e.respondWith(
      fetch(req)
        .then((res) => {
          const copy = res.clone();
          caches.open(VERSION).then((c) => c.put("./index.html", copy));
          return res;
        })
        .catch(() => caches.match("./index.html"))
    );
    return;
  }

  e.respondWith(caches.match(req).then((hit) => hit || fetch(req)));
});
