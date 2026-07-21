// Coach K service worker — installability, web push, and offline app shell.
// Authenticated /api traffic stays network-only (except public exercise images).

const SHELL = "coachk-shell-v3";
const ASSETS = "coachk-assets-v3";
const MEDIA = "coachk-media-v3";

const PRECACHE = [
  "/",
  "/index.html",
  "/manifest.json",
  "/icons/icon-192.png",
  "/icons/icon-512.png",
  "/icons/icon-maskable-512.png",
  "/icons/apple-touch-icon.png",
  "/images/hero-barbell.jpg",
  "/images/training-floor.jpg",
  "/images/chalk-hands.jpg",
  "/images/atmosphere-kettle.jpg",
  "/images/atmosphere-rack.jpg",
  "/images/rack-focus.jpg",
  "/images/coach-dayan.jpg",
  "/images/coach-dayan-speaking.jpg",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(SHELL).then((cache) => cache.addAll(PRECACHE)).then(() => self.skipWaiting()),
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((k) => k !== SHELL && k !== ASSETS && k !== MEDIA)
          .map((k) => caches.delete(k)),
      ),
    ).then(() => self.clients.claim()),
  );
});

async function cacheFirst(request, cacheName) {
  const cached = await caches.match(request);
  if (cached) return cached;
  const res = await fetch(request);
  if (res.ok) {
    const cache = await caches.open(cacheName);
    cache.put(request, res.clone());
  }
  return res;
}

async function networkFirstNavigation(request) {
  try {
    const res = await fetch(request);
    if (res.ok) {
      const cache = await caches.open(SHELL);
      cache.put("/index.html", res.clone());
      // Also keep "/" warm for older clients
      cache.put("/", res.clone());
    }
    return res;
  } catch {
    return (
      (await caches.match("/index.html")) ||
      (await caches.match("/")) ||
      new Response("Coach K is offline. Reconnect to sync your training.", {
        status: 503,
        headers: { "Content-Type": "text/plain; charset=utf-8" },
      })
    );
  }
}

function isNavigation(request) {
  return (
    request.mode === "navigate" ||
    (request.method === "GET" &&
      (request.headers.get("accept") || "").includes("text/html"))
  );
}

self.addEventListener("fetch", (event) => {
  const req = event.request;
  if (req.method !== "GET") return;

  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;

  // Always fetch a fresh SW — never pin updates behind a cache.
  if (url.pathname === "/sw.js") return;

  if (url.pathname.startsWith("/api/")) {
    // Public exercise illustrations — safe to cache aggressively.
    if (url.pathname.startsWith("/api/exercise-images/")) {
      event.respondWith(cacheFirst(req, MEDIA));
    }
    // Everything else (auth, today, chat, progress) — network only.
    return;
  }

  if (url.pathname.startsWith("/assets/")) {
    event.respondWith(cacheFirst(req, ASSETS));
    return;
  }

  if (isNavigation(req)) {
    event.respondWith(networkFirstNavigation(req));
    return;
  }

  // Icons, images, manifest, and other same-origin static files.
  if (
    url.pathname.startsWith("/icons/") ||
    url.pathname.startsWith("/images/") ||
    url.pathname === "/manifest.json"
  ) {
    event.respondWith(cacheFirst(req, SHELL));
  }
});

self.addEventListener("push", (event) => {
  let data = { title: "Coach K", body: "New message", url: "/" };
  try {
    data = { ...data, ...event.data.json() };
  } catch {
    // non-JSON payload — keep defaults
  }
  event.waitUntil(
    self.registration.showNotification(data.title, {
      body: data.body,
      icon: "/icons/icon-192.png",
      badge: "/icons/icon-192.png",
      data: { url: data.url },
    }),
  );
});

self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  const url = event.notification.data?.url || "/";
  event.waitUntil(
    self.clients.matchAll({ type: "window" }).then((clients) => {
      for (const c of clients) {
        if (c.url.includes(self.location.origin) && "focus" in c) return c.focus();
      }
      return self.clients.openWindow(url);
    }),
  );
});
