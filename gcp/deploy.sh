#!/usr/bin/env bash
# Deploy da biblioteca no Google Cloud Run (back + front).
#
# Uso (na raiz do repositório):
#   DATABASE_URL='postgresql://...' ./gcp/deploy.sh     # primeira vez: grava o link do banco no Secret Manager
#   ./gcp/deploy.sh                                       # próximas vezes: só reconstrói e publica
#
# Cria (só se não existir) no projeto, sempre com o prefixo "biblioteca-":
#   - secret  biblioteca-database-url   link do Postgres (Neon) usado pela API
#   - conta   biblioteca-api            identidade da API, só lê o secret acima
#   - Cloud Run biblioteca-api (pasta api/) e biblioteca-web (pasta web/)
#
# Se mudar PROJETO ou REGIAO, atualize também web/.env.production com a nova URL da API.
set -euo pipefail

PROJETO="${PROJETO:-casa-de-leiloes}"
REGIAO="${REGIAO:-southamerica-east1}"
SECRET="biblioteca-database-url"
CONTA="biblioteca-api@${PROJETO}.iam.gserviceaccount.com"
export CLOUDSDK_CORE_PROJECT="$PROJETO"

NUMERO=$(gcloud projects describe "$PROJETO" --format='value(projectNumber)')
URL_API="https://biblioteca-api-${NUMERO}.${REGIAO}.run.app"
URL_WEB="https://biblioteca-web-${NUMERO}.${REGIAO}.run.app"

cd "$(dirname "$0")/.."

echo "==> Secret do banco"
if ! gcloud secrets describe "$SECRET" >/dev/null 2>&1; then
  : "${DATABASE_URL:?Na primeira vez, passe DATABASE_URL='postgresql://...'}"
  printf '%s' "$DATABASE_URL" | gcloud secrets create "$SECRET" --replication-policy=automatic --data-file=-
elif [ -n "${DATABASE_URL:-}" ]; then
  printf '%s' "$DATABASE_URL" | gcloud secrets versions add "$SECRET" --data-file=-
fi

echo "==> Conta de serviço da API"
if ! gcloud iam service-accounts describe "$CONTA" >/dev/null 2>&1; then
  gcloud iam service-accounts create biblioteca-api --display-name="Biblioteca API (Cloud Run)"
fi
gcloud secrets add-iam-policy-binding "$SECRET" \
  --member="serviceAccount:${CONTA}" --role=roles/secretmanager.secretAccessor >/dev/null

if ! grep -q "VITE_API_URL=${URL_API}" web/.env.production; then
  echo "web/.env.production não aponta para ${URL_API}; ajuste antes do deploy." >&2
  exit 1
fi

echo "==> Deploy da API e do front (em paralelo)"
gcloud run deploy biblioteca-api --source api --region "$REGIAO" --quiet \
  --allow-unauthenticated --service-account "$CONTA" \
  --set-secrets "DATABASE_URL=${SECRET}:latest" \
  --set-env-vars "CRIAR_TABELAS=false,CORS_ORIGINS=${URL_WEB}" \
  --memory 512Mi --max-instances 2 &
API=$!
gcloud run deploy biblioteca-web --source web --region "$REGIAO" --quiet \
  --allow-unauthenticated --memory 256Mi --max-instances 2 &
WEB=$!
wait $API
wait $WEB

echo
echo "API:   ${URL_API}/docs"
echo "Front: ${URL_WEB}"
