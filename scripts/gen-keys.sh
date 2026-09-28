#!/usr/bin/env bash
# gen-keys.sh — gera os segredos do lab SE não existirem (idempotente).
# Chamado antes do 'make up'. Nada aqui vai pro git (ver .gitignore).
#
# Portável: gera as chaves WireGuard sem bind-mount (evita dor de path no Windows),
# capturando a saída do container e escrevendo os arquivos no host.
set -euo pipefail
cd "$(dirname "$0")/.."

WG=gateway/wireguard
SSHD=gateway/ssh
IMG=lab-gateway
ENDPOINT="${WG_ENDPOINT:-127.0.0.1:51820}"   # sobrescreva p/ deploy: WG_ENDPOINT=IP:51820

mkdir -p "$WG" "$SSHD"

# Garante a imagem (precisa do binário 'wg').
docker image inspect "$IMG" >/dev/null 2>&1 || docker build -t "$IMG" ./gateway >/dev/null

genkey() { docker run --rm --entrypoint wg "$IMG" genkey; }
pubkey() { docker run --rm -i --entrypoint wg "$IMG" pubkey; }

if [ ! -f "$WG/server_private.key" ]; then
    echo "[keys] WireGuard server..."
    sp=$(genkey); printf '%s\n' "$sp" > "$WG/server_private.key"
    printf '%s\n' "$sp" | pubkey > "$WG/server_public.key"
fi
if [ ! -f "$WG/peer_private.key" ]; then
    echo "[keys] WireGuard peer..."
    pp=$(genkey); printf '%s\n' "$pp" > "$WG/peer_private.key"
    printf '%s\n' "$pp" | pubkey > "$WG/peer_public.key"
fi
if [ ! -f "$WG/client.conf" ]; then
    echo "[keys] client.conf (endpoint $ENDPOINT)..."
    cat > "$WG/client.conf" <<EOF
[Interface]
PrivateKey = $(cat "$WG/peer_private.key")
Address = 10.13.13.2/32

[Peer]
PublicKey = $(cat "$WG/server_public.key")
Endpoint = $ENDPOINT
# 10.13.13.0/24 = rede VPN (gateway); 172.30.10.0/24 = DMZ (acesso ao WAF via túnel).
AllowedIPs = 10.13.13.0/24, 172.30.10.0/24
PersistentKeepalive = 25
EOF
fi
if [ ! -f "$SSHD/admin_ed25519" ]; then
    echo "[keys] admin SSH key..."
    ssh-keygen -t ed25519 -f "$SSHD/admin_ed25519" -N "" -C "lab-admin" >/dev/null
fi
cp "$SSHD/admin_ed25519.pub" "$SSHD/authorized_keys"
chmod 600 "$WG"/*.key "$WG/client.conf" "$SSHD/admin_ed25519" 2>/dev/null || true

# Senha do Postgres no .env (gitignored). Gera aleatória se ainda não existir.
if [ ! -f .env ] || ! grep -q '^DB_PASSWORD=' .env 2>/dev/null; then
    PW=$(LC_ALL=C tr -dc 'A-Za-z0-9' </dev/urandom | head -c 24)
    printf 'DB_PASSWORD=%s\n' "$PW" >> .env
    echo "[keys] DB_PASSWORD gerado em .env"
fi

echo "[keys] ok. Segredos em $WG e $SSHD (gitignored). Importe $WG/client.conf no cliente WireGuard."
