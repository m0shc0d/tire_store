#!/usr/bin/env bash
# generate_env.sh – interactive ../.env generator
set -euo pipefail

OUT_FILE="../.env"
if [[ -e $OUT_FILE ]]; then
  echo "File $OUT_FILE already exists – aborting."
  exit 1
fi

ask(){
  local prompt="$1" default="$2"
  read -rp "$prompt [$default]: " val
  echo "${val:-$default}"
}

ask_yes_no(){
  local prompt="$1" default="${2:-y}"
  while true; do
    read -rp "$prompt (y/n) [$default]: " yn
    case "${yn:-$default}" in
      [Yy]*) return 0 ;;
      [Nn]*) return 1 ;;
      *) echo "Please enter y or n." ;;
    esac
  done
}

gen_pass(){
  openssl rand -hex 16
}

echo "=== ../.env generator ==="
echo

DOMAIN=$(ask "DOMAIN" "localhost")

BACKEND_HOST_DEFAULT="http://${DOMAIN}:5173"
if ask_yes_no "BACKEND_HOST = ${BACKEND_HOST_DEFAULT}"; then
  BACKEND_HOST="$BACKEND_HOST_DEFAULT"
else
  BACKEND_HOST=$(ask "Enter BACKEND_HOST" "$BACKEND_HOST_DEFAULT")
fi

FRONTEND_HOST_DEFAULT="http://${DOMAIN}:8000"
if ask_yes_no "FRONTEND_HOST = ${FRONTEND_HOST_DEFAULT}"; then
  FRONTEND_HOST="$FRONTEND_HOST_DEFAULT"
else
  FRONTEND_HOST=$(ask "Enter FRONTEND_HOST" "$FRONTEND_HOST_DEFAULT")
fi

API_ENDPOINT_DEFAULT="/api/v1"
if ask_yes_no "API_ENDPOINT = ${API_ENDPOINT_DEFAULT}"; then
  API_ENDPOINT="$API_ENDPOINT_DEFAULT"
else
  API_ENDPOINT=$(ask "Enter API_ENDPOINT" "$API_ENDPOINT_DEFAULT")
fi

ENVIRONMENT_DEFAULT=local
if ask_yes_no "ENVIRONMENT = ${ENVIRONMENT_DEFAULT}"; then
  ENVIRONMENT=$ENVIRONMENT_DEFAULT
else
  PS3="Select ENVIRONMENT: "
  select env in local staging production; do
    [[ -n $env ]] && { ENVIRONMENT=$env; break; }
  done
fi

PROJECT_NAME=$(ask "PROJECT_NAME" "Full Stack FastAPI Project")

STACK_NAME=$(ask "STACK_NAME" "full-stack-fastapi-project")

if [[ $DOMAIN == "localhost" ]]; then
  BACKEND_CORS_ORIGINS="http://${DOMAIN},http://${DOMAIN}:5173,https://${DOMAIN},https://${DOMAIN}:5173"
else
  BACKEND_CORS_ORIGINS="http://${DOMAIN},http://${DOMAIN}:5173,https://${DOMAIN},https://${DOMAIN}:5173,http://localhost.tiangolo.com"
fi

SECRET_KEY=$(openssl rand -hex 32)

echo "Example FIRST_SUPERUSER: admin@example.com"
FIRST_SUPERUSER=$(ask "FIRST_SUPERUSER" "admin@example.com")

if ask_yes_no "Generate FIRST_SUPERUSER_PASSWORD automatically"; then
  FIRST_SUPERUSER_PASSWORD=$(gen_pass)
  echo "Generated password: $FIRST_SUPERUSER_PASSWORD"
else
  read -rsp "Enter FIRST_SUPERUSER_PASSWORD: " FIRST_SUPERUSER_PASSWORD
  echo
fi

SMTP_HOST=""
SMTP_USER=""
SMTP_PASSWORD=""
EMAILS_FROM_EMAIL=""
SMTP_TLS="True"
SMTP_SSL="False"
SMTP_PORT="587"

if ask_yes_no "Configure SMTP" "n"; then
  SMTP_HOST=$(ask "SMTP_HOST" "")
  SMTP_USER=$(ask "SMTP_USER" "")
  read -rsp "SMTP_PASSWORD: " SMTP_PASSWORD; echo
  EMAILS_FROM_EMAIL=$(ask "EMAILS_FROM_EMAIL" "")
  if ask_yes_no "SMTP_TLS = True" "y"; then SMTP_TLS="True"; else SMTP_TLS="False"; fi
  if ask_yes_no "SMTP_SSL = False" "y"; then SMTP_SSL="False"; else SMTP_SSL="True"; fi
  SMTP_PORT=$(ask "SMTP_PORT" "587")
fi

POSTGRES_SERVER=$(ask "POSTGRES_SERVER" "172.16.1.2")
POSTGRES_PORT=$(ask "POSTGRES_PORT" "5432")
POSTGRES_DB=$(ask "POSTGRES_DB" "app")

POSTGRES_USER_DEFAULT=postgres
if ask_yes_no "POSTGRES_USER = ${POSTGRES_USER_DEFAULT}"; then
  POSTGRES_USER=$POSTGRES_USER_DEFAULT
else
  echo "Strongly recommended to keep 'postgres' as the superuser."
  read -rp "Are you sure? (y/n) [n]: " sure
  [[ $sure == "y" ]] && POSTGRES_USER=$(ask "POSTGRES_USER" "$POSTGRES_USER_DEFAULT") || POSTGRES_USER=$POSTGRES_USER_DEFAULT
fi

if ask_yes_no "Generate POSTGRES_PASSWORD automatically"; then
  POSTGRES_PASSWORD=$(gen_pass)
  echo "Generated password: $POSTGRES_PASSWORD"
else
  read -rsp "Enter POSTGRES_PASSWORD: " POSTGRES_PASSWORD; echo
fi

SENTRY_DSN=""
DOCKER_IMAGE_BACKEND=$(ask "DOCKER_IMAGE_BACKEND" "backend")
DOCKER_IMAGE_FRONTEND=$(ask "DOCKER_IMAGE_FRONTEND" "frontend")
HELLO="World"

cat > "$OUT_FILE" <<EOF
# Domain
DOMAIN=$DOMAIN

# Used by the backend to generate links in emails to the frontend
BACKEND_HOST=$BACKEND_HOST

# In staging and production, set this env var to the frontend host, e.g.
FRONTEND_HOST=$FRONTEND_HOST
API_ENDPOINT=$API_ENDPOINT

# Environment: local, staging, production
ENVIRONMENT=$ENVIRONMENT

PROJECT_NAME=$PROJECT_NAME
STACK_NAME=$STACK_NAME

# Backend
BACKEND_CORS_ORIGINS="$BACKEND_CORS_ORIGINS"
SECRET_KEY=$SECRET_KEY
FIRST_SUPERUSER=$FIRST_SUPERUSER
FIRST_SUPERUSER_PASSWORD=$FIRST_SUPERUSER_PASSWORD

# Emails
SMTP_HOST=$SMTP_HOST
SMTP_USER=$SMTP_USER
SMTP_PASSWORD=$SMTP_PASSWORD
EMAILS_FROM_EMAIL=$EMAILS_FROM_EMAIL
SMTP_TLS=$SMTP_TLS
SMTP_SSL=$SMTP_SSL
SMTP_PORT=$SMTP_PORT

# Postgres
POSTGRES_SERVER=$POSTGRES_SERVER
POSTGRES_PORT=$POSTGRES_PORT
POSTGRES_DB=$POSTGRES_DB
POSTGRES_USER=$POSTGRES_USER
POSTGRES_PASSWORD=$POSTGRES_PASSWORD

SENTRY_DSN=$SENTRY_DSN

# Configure these with your own Docker registry images
DOCKER_IMAGE_BACKEND=$DOCKER_IMAGE_BACKEND
DOCKER_IMAGE_FRONTEND=$DOCKER_IMAGE_FRONTEND
HELLO=$HELLO
EOF

echo
echo "File $OUT_FILE created."
