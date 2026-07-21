# Deploying Coach K v2

Two supported paths. Both use the **Dockerfile** (WeasyPrint system libs, baked-in
embedding model, exercise media, and the built React UI).

**Always set `APP_PASSWORD`** — it gates the whole API. Without it, anyone who
finds the URL can spend your Anthropic credits.

**Migrations run automatically** when the app starts (`app/migrate.py`). You do
not need to hand-run `migrations/*.sql` on new databases (Docker Compose, App
Platform, or local `createdb`).

On **DigitalOcean Managed Postgres**, enable the **pgvector** extension once:
Databases → your cluster → Settings → Extensions → **vector** → Enable. The app
also runs `CREATE EXTENSION IF NOT EXISTS vector` on startup when permitted.

---

## Option A — DigitalOcean Droplet + Docker Compose (simplest)

1. Create a droplet from the **Docker on Ubuntu** marketplace image (≥ **2 GB RAM**).
2. On the droplet:

```bash
git clone https://github.com/djrk935/coach-k-v2.git && cd coach-k-v2
cat > .env <<'EOF'
POSTGRES_PASSWORD=<random-strong-password>
ANTHROPIC_API_KEY=sk-ant-...
APP_PASSWORD=<password for browser + iOS Settings>
EOF
docker compose up -d --build    # first build ~5–10 min
```

3. Open `http://<droplet-ip>` — enter `APP_PASSWORD` at the lock screen.

For HTTPS, put **Caddy** or nginx in front of the droplet, or use Option B.

### Move your library + logs from a Mac

```bash
# on the Mac
pg_dump -Fc coachk > coachk.dump
scp coachk.dump root@<droplet-ip>:~/coach-k-v2/

# on the droplet
cd coach-k-v2
docker compose exec -T db pg_restore -U coach -d coachk --clean --no-owner < coachk.dump
docker compose restart app
```

---

## Option B — DigitalOcean App Platform (HTTPS for iPhone)

Best if you want a stable **https://…ondigitalocean.app** URL for Safari and the
iOS app without managing TLS yourself.

1. Push this repo to GitHub (already at `djrk935/coach-k-v2`).
2. App Platform → **Create App** → GitHub → select **coach-k-v2**.
3. Use **Dockerfile** deploy (do **not** use the Python buildpack).
4. **Add a Dev Database** or managed Postgres cluster (PG 15+), link it as
   `DATABASE_URL` (App Platform injects `${db.DATABASE_URL}` — include SSL).
5. Enable **pgvector** on that cluster (see above).
6. Set **secrets**:
   - `ANTHROPIC_API_KEY`
   - `APP_PASSWORD` (same value you type in iOS Settings → App password)
7. Instance size: **≥ 2 GB RAM** (`apps-s-1vcpu-2gb` or larger).
8. Health check path: **`/api/health`** (returns `{"ok":true,"db":true}` when ready).

You can import the starter spec from [`.do/app.yaml`](.do/app.yaml) and adjust
region / repo / database name.

First deploy may take several minutes (image build + model bake). Watch **Runtime
Logs** for `migrations applied: …`.

---

## iPhone (personal device)

1. Install **Xcode**, then:

```bash
brew install xcodegen
cd ios && xcodegen generate && open CoachK.xcodeproj
```

2. **Signing**: Xcode → CoachK target → **Signing & Capabilities** → your Apple ID
   (Personal Team). Required for a real device; simulator can skip signing.
3. **Settings in the app** (on device):
   - **Server**: your App Platform URL, e.g. `https://coach-k-xxxxx.ondigitalocean.app`
     (must be **HTTPS** on a physical iPhone — HTTP only works on simulator / local LAN).
   - **App password**: same as `APP_PASSWORD` on the server.
   - Tap **Test Connection** — should show password accepted.
4. Same Wi‑Fi / cellular is fine; no VPN needed if the URL is public HTTPS.

Simulator defaults to `http://localhost:8000` with `./run.sh` on your Mac.

---

## Notes

- `/api/health` is unauthenticated — use it for probes; it also checks DB connectivity.
- Exercise images are public (open-source content; `<img>` tags cannot send auth headers).
- `LLAMA_CLOUD_API_KEY` is only needed to ingest **new** PDFs on the server; ingest
  locally and `pg_dump`/`restore` to avoid re-parsing.
- **Web push** (optional): generate VAPID keys (`python -m app.gen_vapid_keys`) and set
  `VAPID_*` env vars on the server.
- **iOS APNs** (optional): set `APNS_KEY_ID`, `APNS_TEAM_ID`, `APNS_AUTH_KEY` (.p8 PEM or
  path), and `APNS_BUNDLE_ID`. Tokens register via Settings → Enable remote push.
  Migration `008` creates `apns_devices` on startup.
