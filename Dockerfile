# Monorepo production image: API + built Square SPA (same origin).
# Cloudflare Pages can keep serving barathx.com; Railway also serves the latest UI.

FROM node:22-alpine AS frontend
WORKDIR /fe
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
COPY VERSION /VERSION
# Same-origin API when the SPA is served from this container.
ARG VITE_API_BASE=
ARG VITE_GOOGLE_CLIENT_ID=682923055091-imk39450dk207psnoetvhnvseslvq0qp.apps.googleusercontent.com
ARG VITE_MVP_VERSION=
ARG VITE_TURNSTILE_SITE_KEY=
ENV VITE_API_BASE=$VITE_API_BASE \
    VITE_GOOGLE_CLIENT_ID=$VITE_GOOGLE_CLIENT_ID \
    VITE_TURNSTILE_SITE_KEY=$VITE_TURNSTILE_SITE_KEY
RUN if [ -z "$VITE_MVP_VERSION" ]; then export VITE_MVP_VERSION="$(tr -d '[:space:]' </VERSION)"; fi \
    && export VITE_MVP_VERSION \
    && npm run build

FROM python:3.13-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app ./app
COPY VERSION /app/VERSION
COPY --from=frontend /fe/dist ./frontend_dist

EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
