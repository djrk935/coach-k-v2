# ---- Stage 1: build the React frontend ----
FROM node:22-slim AS frontend
WORKDIR /fe
COPY frontend/package*.json ./
RUN npm ci
COPY frontend .
RUN npm run build

# ---- Stage 2: Python runtime ----
FROM python:3.12-slim
WORKDIR /srv

# WeasyPrint system libs (pango/gobject) + fetch tooling
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 libpangoft2-1.0-0 libpangocairo-1.0-0 libharfbuzz0b \
    libffi8 libjpeg62-turbo zlib1g fonts-dejavu-core curl unzip \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Bake the local embedding model into the image (no cold-start download)
RUN python -c "from fastembed import TextEmbedding; TextEmbedding('BAAI/bge-base-en-v1.5')"

# Exercise form illustrations (self-hosted)
COPY scripts/fetch_exercise_media.sh scripts/
RUN bash scripts/fetch_exercise_media.sh

COPY app ./app
COPY migrations ./migrations
COPY --from=frontend /fe/dist ./frontend/dist

ENV PORT=8080
EXPOSE 8080
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
