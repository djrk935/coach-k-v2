# Deploying Coach K v2

Two supported paths. Both use the Dockerfile (which bundles WeasyPrint's system
libs, the local embedding model, exercise media, and the built frontend — none
of which a default buildpack provides).

**Always set `APP_PASSWORD`** — it gates the whole API. Without it, anyone who
finds the URL can chat on your Anthropic credits.

## Option A — DigitalOcean Droplet with docker compose (recommended, simplest)

1. Create a droplet from the **Docker on Ubuntu** marketplace image
   (≥ 2 GB RAM — the embedding model + agent need it).
2. On the droplet:

```bash
git clone https://github.com/djrk935/coach-k-v2.git && cd coach-k-v2
cat > .env <<'EOF'
POSTGRES_PASSWORD=<random-strong-password>
ANTHROPIC_API_KEY=sk-ant-...
APP_PASSWORD=<the password you'll type in the browser>
EOF
docker compose up -d --build     # first build ~5-10 min
```

3. Open `http://<droplet-ip>` — enter `APP_PASSWORD` at the lock screen. Done.

Postgres runs the schema migration automatically on first boot
(`migrations/001_init.sql` is mounted into initdb.d).

### Bring your data (books, logs, programs) from your Mac

```bash
# on the Mac
pg_dump -Fc coachk > coachk.dump
scp coachk.dump root@<droplet-ip>:~/coach-k-v2/

# on the droplet
cd coach-k-v2
docker compose exec -T db pg_restore -U coach -d coachk --clean --no-owner < coachk.dump
docker compose restart app
```

This carries the full 7k-chunk library — no re-parsing, no LlamaParse credits.

## Option B — DigitalOcean App Platform

1. App Platform → Create App → your GitHub repo. It detects the **Dockerfile**
   (do not let it use a Python buildpack).
2. Instance: ≥ 1 GB RAM.
3. Add a **managed Postgres** (v15+) and enable the `vector` extension
   (Databases → your cluster → Settings → Extensions → pgvector), then run
   `migrations/001_init.sql` against it once (`psql $DATABASE_URL -f ...`).
4. App-level env vars:
   - `DATABASE_URL` — the connection string **with `?sslmode=require`**
   - `ANTHROPIC_API_KEY`, `APP_PASSWORD`
5. The app listens on `$PORT` (App Platform sets it automatically).

## Notes

- `/api/health` is unauthenticated — use it as the health-check endpoint.
- Exercise images are public by design (open-source content; `<img>` can't send
  auth headers).
- `LLAMA_CLOUD_API_KEY` is only needed if you ingest new books *from the server*;
  you can also ingest locally and re-run the pg_dump/restore.
- HTTPS: put the droplet behind a domain + Caddy/nginx, or let App Platform
  terminate TLS for you (automatic).
