#!/bin/bash

POD=$(kubectl get pod -n gitea -l app.kubernetes.io/name=gitea -o jsonpath="{.items[0].metadata.name}")
NAMESPACE="gitea"
PASSWORD="botpass123"
DOMAIN="example.com"

BOTS=("frontend-bot" "backend-bot" "devops-bot" "malicious-bot" "lazy-bot")

for BOT in "${BOTS[@]}"; do
  echo "Creando usuario: $BOT"
  kubectl exec -n "$NAMESPACE" "$POD" -- \
    gitea admin user create \
      --username "$BOT" \
      --password "$PASSWORD" \
      --email "${BOT}@${DOMAIN}" \
      || echo "⚠️  Usuario $BOT ya existe o ha fallado"
done
