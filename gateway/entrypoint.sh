#!/bin/sh
# Entrypoint do wg-gateway: firewall + SSH admin + WireGuard, tudo no boot.
set -e

RULESET=/etc/nftables/ruleset.nft
WG_SRC=/etc/wireguard-src          # bind-mount de gateway/wireguard (chaves + template)
WG_CONF=/etc/wireguard/wg0.conf

echo "[gateway] 1/3 carregando nftables ..."
nft -f "$RULESET"

echo "[gateway] 2/3 subindo sshd (admin, key-only) ..."
# Instala a chave autorizada do admin + hardening (login só por chave, sem senha).
SSH_SRC=/etc/gateway-ssh
if [ -f "$SSH_SRC/authorized_keys" ]; then
    mkdir -p /root/.ssh && chmod 700 /root/.ssh
    cp "$SSH_SRC/authorized_keys" /root/.ssh/authorized_keys
    chmod 600 /root/.ssh/authorized_keys
fi
[ -f "$SSH_SRC/sshd_hardening.conf" ] && cp "$SSH_SRC/sshd_hardening.conf" /etc/ssh/sshd_config.d/99-lab.conf
ssh-keygen -A >/dev/null 2>&1 || true
mkdir -p /run/sshd
/usr/sbin/sshd

echo "[gateway] 3/3 subindo WireGuard ..."
if [ -f "$WG_SRC/wg0.conf.template" ] && [ -f "$WG_SRC/server_private.key" ]; then
    mkdir -p /etc/wireguard
    SPRIV=$(cat "$WG_SRC/server_private.key")
    PPUB=$(cat "$WG_SRC/peer_public.key")
    # '|' como delimitador do sed: chaves base64 têm '/' e '+', mas nunca '|'.
    sed -e "s|__SERVER_PRIVATE__|$SPRIV|" -e "s|__PEER_PUBLIC__|$PPUB|" \
        "$WG_SRC/wg0.conf.template" > "$WG_CONF"
    chmod 600 "$WG_CONF"
    wg-quick up wg0 && echo "[gateway] WireGuard no ar (wg0)." \
        || echo "[gateway] WARN: wg-quick falhou (ver kernel module wireguard)."
else
    echo "[gateway] WARN: chaves/template do WireGuard ausentes — pulei o wg."
fi

echo "[gateway] pronto — firewall + sshd + wg. Mantendo container vivo."
exec sleep infinity
