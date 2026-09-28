#!/bin/sh
# Injeta a rota default via o gateway do DB (172.30.30.254) e chama o entrypoint
# ORIGINAL do postgres. Auto-roteia no boot e sobrevive a restart (sem sidecar).
ip route replace default via 172.30.30.254 || echo "[postgres] WARN: rota default não adicionada"
exec docker-entrypoint.sh "$@"
