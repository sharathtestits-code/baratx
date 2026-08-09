#!/usr/bin/env bash
# Provision BarathX QA on Railway (API + SPA same-origin) + optional Cloudflare DNS.
#
# Required:
#   RAILWAY_API_TOKEN  — account/workspace token from https://railway.com/account/tokens
#                        (RAILWAY_TOKEN also accepted)
#
# Optional:
#   CLOUDFLARE_API_TOKEN  — DNS edit for qa.barathx.com
#   CLOUDFLARE_ZONE_ID    — zone id for barathx.com (auto-resolved if omitted)
#   QA_ADMIN_SECRET / QA_JWT_SECRET / QA_OFFICIAL_PASSWORD — generated if unset
#   RAILWAY_WORKSPACE     — workspace id/name (auto if only one)
#
# Usage:
#   export RAILWAY_API_TOKEN=...
#   ./scripts/provision-qa.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ -z "${RAILWAY_API_TOKEN:-}" && -n "${RAILWAY_TOKEN:-}" ]]; then
  export RAILWAY_API_TOKEN="$RAILWAY_TOKEN"
fi
if [[ -z "${RAILWAY_API_TOKEN:-}" ]]; then
  echo "Missing RAILWAY_API_TOKEN. Create one at https://railway.com/account/tokens" >&2
  exit 1
fi
# CLI accepts either; prefer account token via RAILWAY_API_TOKEN
export RAILWAY_TOKEN="${RAILWAY_TOKEN:-$RAILWAY_API_TOKEN}"

if ! command -v railway >/dev/null 2>&1; then
  curl -fsSL https://railway.com/install.sh | sh
  # shellcheck disable=SC1091
  source "${HOME}/.railway/env" 2>/dev/null || export PATH="${HOME}/.railway/bin:$PATH"
fi

need() { command -v "$1" >/dev/null 2>&1 || { echo "Need $1" >&2; exit 1; }; }
need jq
need curl
need openssl

PROJECT_NAME="${QA_RAILWAY_PROJECT:-baratx-qa}"
SERVICE_NAME="${QA_RAILWAY_SERVICE:-baratx}"
REPO="${QA_GITHUB_REPO:-sharathtestits-code/baratx}"
BRANCH="${QA_GITHUB_BRANCH:-main}"
CUSTOM_DOMAIN="${QA_CUSTOM_DOMAIN:-qa.barathx.com}"
SECRETS_DIR="${HOME}/.config/baratx"
SECRETS_FILE="${SECRETS_DIR}/qa.secrets.env"
mkdir -p "$SECRETS_DIR"
chmod 700 "$SECRETS_DIR"

gen_secret() { openssl rand -base64 48 | tr -d '\n=+/' | head -c 48; }

if [[ -f "$SECRETS_FILE" ]]; then
  # shellcheck disable=SC1090
  source "$SECRETS_FILE"
fi

QA_ADMIN_SECRET="${QA_ADMIN_SECRET:-$(gen_secret)}"
QA_JWT_SECRET="${QA_JWT_SECRET:-$(gen_secret)}"
QA_OFFICIAL_PASSWORD="${QA_OFFICIAL_PASSWORD:-$(gen_secret)}"

umask 077
cat >"$SECRETS_FILE" <<EOF
QA_ADMIN_SECRET=${QA_ADMIN_SECRET}
QA_JWT_SECRET=${QA_JWT_SECRET}
QA_OFFICIAL_PASSWORD=${QA_OFFICIAL_PASSWORD}
EOF
chmod 600 "$SECRETS_FILE"
echo "QA secrets cached at ${SECRETS_FILE} (not committed)"

echo "==> Auth check"
railway whoami --json | jq '{name: .name, email: .email, id: .id}'

echo "==> Resolve / create project ${PROJECT_NAME}"
PROJECTS_JSON="$(railway list --json 2>/dev/null || echo '[]')"
PROJECT_ID="$(echo "$PROJECTS_JSON" | jq -r --arg n "$PROJECT_NAME" '
  if type=="array" then
    (map(select(.name==$n)) | .[0].id // empty)
  else
    (.. | objects | select(.name?==$n) | .id) // empty
  end
' | head -n1)"

if [[ -z "$PROJECT_ID" || "$PROJECT_ID" == "null" ]]; then
  INIT_ARGS=(init --name "$PROJECT_NAME" --json)
  if [[ -n "${RAILWAY_WORKSPACE:-}" ]]; then
    INIT_ARGS+=(--workspace "$RAILWAY_WORKSPACE")
  fi
  INIT_OUT="$(railway "${INIT_ARGS[@]}")"
  echo "$INIT_OUT" | jq . || echo "$INIT_OUT"
  PROJECT_ID="$(echo "$INIT_OUT" | jq -r '.id // .project.id // empty')"
  if [[ -z "$PROJECT_ID" ]]; then
    # init links cwd; status has id
    PROJECT_ID="$(railway status --json | jq -r '.project.id // .id // empty')"
  fi
else
  echo "Project exists: $PROJECT_ID"
  railway link --project "$PROJECT_ID" --json >/dev/null || railway link -p "$PROJECT_ID"
fi

STATUS="$(railway status --json)"
ENV_ID="$(echo "$STATUS" | jq -r '.environment.id // .environmentId // empty')"
ENV_NAME="$(echo "$STATUS" | jq -r '.environment.name // "production"')"
echo "Linked project=$PROJECT_ID environment=$ENV_NAME ($ENV_ID)"

echo "==> Ensure Postgres"
SERVICES="$(railway service list --json 2>/dev/null || echo '[]')"
HAS_PG="$(echo "$SERVICES" | jq -r '
  if type=="array" then
    any(.[]; (.name|ascii_downcase|test("postgres|postgresql")) or (.serviceType?=="postgresql"))
  else false end
')"
if [[ "$HAS_PG" != "true" ]]; then
  railway add --database postgres --json
else
  echo "Postgres already present"
fi

# Discover postgres service name for variable reference
SERVICES="$(railway service list --json)"
PG_NAME="$(echo "$SERVICES" | jq -r '
  if type=="array" then
    (map(select((.name|ascii_downcase|test("postgres|postgresql")))) | .[0].name // "Postgres")
  else "Postgres" end
')"
echo "Postgres service name: $PG_NAME"

echo "==> Ensure app service ${SERVICE_NAME} from GitHub ${REPO}@${BRANCH}"
HAS_APP="$(echo "$SERVICES" | jq -r --arg n "$SERVICE_NAME" '
  if type=="array" then any(.[]; .name==$n) else false end
')"
if [[ "$HAS_APP" != "true" ]]; then
  # Prefer creating from repo so GitHub auto-deploys keep working
  railway add \
    --repo "$REPO" \
    --branch "$BRANCH" \
    --service "$SERVICE_NAME" \
    --json \
    --variables "ENVIRONMENT=qa" \
    --variables "JWT_SECRET=${QA_JWT_SECRET}" \
    --variables "ADMIN_SECRET=${QA_ADMIN_SECRET}" \
    --variables "OFFICIAL_ACCOUNT_PASSWORD=${QA_OFFICIAL_PASSWORD}" \
    --variables "FRONTEND_URL=https://${CUSTOM_DOMAIN}" \
    --variables "CORS_ORIGINS=https://${CUSTOM_DOMAIN},https://baratx-qa.up.railway.app" \
    --variables "EMAIL_FROM=BarathX QA <hello@barathx.com>" \
    --variables "MEDIA_BACKEND=auto" \
    --variables "GOOGLE_CLIENT_ID=682923055091-imk39450dk207psnoetvhnvseslvq0qp.apps.googleusercontent.com" \
    || railway add --service "$SERVICE_NAME" --repo "$REPO" --branch "$BRANCH" --json
else
  echo "Service ${SERVICE_NAME} already present"
fi

railway service link "$SERVICE_NAME" >/dev/null 2>&1 || true

echo "==> Set / refresh QA variables (skip deploy storm)"
railway variable set \
  --service "$SERVICE_NAME" \
  --skip-deploys \
  "ENVIRONMENT=qa" \
  "JWT_SECRET=${QA_JWT_SECRET}" \
  "ADMIN_SECRET=${QA_ADMIN_SECRET}" \
  "OFFICIAL_ACCOUNT_PASSWORD=${QA_OFFICIAL_PASSWORD}" \
  "FRONTEND_URL=https://${CUSTOM_DOMAIN}" \
  "CORS_ORIGINS=https://${CUSTOM_DOMAIN},https://baratx-qa.up.railway.app" \
  "EMAIL_FROM=BarathX QA <hello@barathx.com>" \
  "MEDIA_BACKEND=auto" \
  "GOOGLE_CLIENT_ID=682923055091-imk39450dk207psnoetvhnvseslvq0qp.apps.googleusercontent.com" \
  "DATABASE_URL=\${{${PG_NAME}.DATABASE_URL}}"

echo "==> Ensure public Railway domain"
DOMAINS="$(railway domain list --service "$SERVICE_NAME" --json 2>/dev/null || echo '[]')"
RAIL_DOMAIN="$(echo "$DOMAINS" | jq -r '
  if type=="array" then
    (map(select(.domain != null)) | .[0].domain // .[0].serviceDomains[0].domain // empty)
  elif type=="object" then
    (.serviceDomains[0].domain // .domains[0].domain // empty)
  else empty end
')"
if [[ -z "$RAIL_DOMAIN" || "$RAIL_DOMAIN" == "null" ]]; then
  DOM_OUT="$(railway domain --service "$SERVICE_NAME" --json 2>/dev/null || railway domain --service "$SERVICE_NAME")"
  echo "$DOM_OUT"
  RAIL_DOMAIN="$(echo "$DOM_OUT" | jq -r '.domain // .serviceDomain.domain // empty' 2>/dev/null || true)"
fi
# Fallback guess used in docs
if [[ -z "$RAIL_DOMAIN" || "$RAIL_DOMAIN" == "null" ]]; then
  RAIL_DOMAIN="baratx-qa.up.railway.app"
  echo "WARN: could not parse generated domain; expecting ${RAIL_DOMAIN}"
fi
echo "Railway domain: https://${RAIL_DOMAIN}"

# Refresh CORS with actual railway domain
railway variable set \
  --service "$SERVICE_NAME" \
  --skip-deploys \
  "CORS_ORIGINS=https://${CUSTOM_DOMAIN},https://${RAIL_DOMAIN}" \
  "FRONTEND_URL=https://${CUSTOM_DOMAIN}"

echo "==> Custom domain ${CUSTOM_DOMAIN} on Railway"
if echo "$DOMAINS" | jq -e --arg d "$CUSTOM_DOMAIN" '
  .. | strings | select(.==$d)
' >/dev/null 2>&1; then
  echo "Custom domain already attached"
else
  railway domain "$CUSTOM_DOMAIN" --service "$SERVICE_NAME" --json || \
    railway domain "$CUSTOM_DOMAIN" --service "$SERVICE_NAME" || true
fi

echo "==> Redeploy app"
railway service redeploy --service "$SERVICE_NAME" --yes --json 2>/dev/null \
  || railway redeploy --service "$SERVICE_NAME" --yes 2>/dev/null \
  || true

# Optional Cloudflare DNS: CNAME qa -> railway domain; remove conflicting records
if [[ -n "${CLOUDFLARE_API_TOKEN:-}" ]]; then
  echo "==> Cloudflare DNS for ${CUSTOM_DOMAIN}"
  CF_AUTH=( -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" -H "Content-Type: application/json" )
  if [[ -z "${CLOUDFLARE_ZONE_ID:-}" ]]; then
    CLOUDFLARE_ZONE_ID="$(curl -fsS "${CF_AUTH[@]}" \
      "https://api.cloudflare.com/client/v4/zones?name=barathx.com" \
      | jq -r '.result[0].id // empty')"
  fi
  if [[ -z "$CLOUDFLARE_ZONE_ID" ]]; then
    echo "WARN: could not resolve Cloudflare zone for barathx.com" >&2
  else
    EXISTING="$(curl -fsS "${CF_AUTH[@]}" \
      "https://api.cloudflare.com/client/v4/zones/${CLOUDFLARE_ZONE_ID}/dns_records?name=${CUSTOM_DOMAIN}")"
    echo "$EXISTING" | jq -r '.result[].id' | while read -r rid; do
      [[ -n "$rid" ]] || continue
      curl -fsS -X DELETE "${CF_AUTH[@]}" \
        "https://api.cloudflare.com/client/v4/zones/${CLOUDFLARE_ZONE_ID}/dns_records/${rid}" >/dev/null
      echo "Deleted DNS record $rid"
    done
    # Prefer CNAME to Railway service domain (proxied)
    TARGET="${RAIL_DOMAIN}"
    curl -fsS -X POST "${CF_AUTH[@]}" \
      "https://api.cloudflare.com/client/v4/zones/${CLOUDFLARE_ZONE_ID}/dns_records" \
      --data "$(jq -n --arg name "$CUSTOM_DOMAIN" --arg content "$TARGET" \
        '{type:"CNAME",name:$name,content:$content,ttl:1,proxied:true}')" \
      | jq '{success, errors, result: {id: .result.id, name: .result.name, content: .result.content}}'
    echo "Also disable any Cloudflare Redirect Rule / Bulk Redirect that sends ${CUSTOM_DOMAIN} → l.ink"
  fi
else
  echo "Skip Cloudflare DNS (set CLOUDFLARE_API_TOKEN to auto-point ${CUSTOM_DOMAIN})"
fi

echo
echo "======== QA provision summary ========"
echo "Railway project:  ${PROJECT_NAME} (${PROJECT_ID})"
echo "App service:      ${SERVICE_NAME}"
echo "Interim URL:      https://${RAIL_DOMAIN}"
echo "Custom URL:       https://${CUSTOM_DOMAIN}  (after DNS)"
echo "Admin:            https://${CUSTOM_DOMAIN}/admin  (secret in ${SECRETS_FILE})"
echo "Official login:   username baratx + QA_OFFICIAL_PASSWORD from secrets file"
echo "Health check:     curl -sS https://${RAIL_DOMAIN}/health"
echo "====================================="
