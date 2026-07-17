#!/usr/bin/env bash
# Download the free-exercise-db catalog + images (~100MB) for form illustrations.
# Self-hosted: nothing leaves the machine at runtime. Idempotent.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p exercise_media
cd exercise_media

[ -f exercises.json ] || curl -sL -o exercises.json \
  https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/dist/exercises.json

if [ ! -d images ]; then
  curl -sL -o repo.zip https://github.com/yuhonas/free-exercise-db/archive/refs/heads/main.zip
  unzip -q repo.zip "free-exercise-db-main/exercises/*"
  mv free-exercise-db-main/exercises images
  rm -rf free-exercise-db-main repo.zip
fi

echo "exercise media ready: $(ls images | wc -l | tr -d ' ') exercises"
