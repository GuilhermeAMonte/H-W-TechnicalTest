#!/bin/sh
# entrypoint da app-api: injeta a rota default via o gateway da APP (172.30.20.254),
# pra alcançar o DB atravessando o firewall, e sobe a API.
set -e
ip route replace default via 172.30.20.254 || echo "[app-api] WARN: rota default não adicionada"
echo "[app-api] rota:"; ip route | grep default || true
exec gunicorn -b 0.0.0.0:8000 -w 2 app:app
