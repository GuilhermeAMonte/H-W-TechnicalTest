#!/bin/sh
# Entrypoint do wg-gateway.
# Carrega o firewall nftables no boot e mantém o container vivo.
# (WireGuard/SSH entram aqui na Stage 2.)
set -e

RULESET=/etc/nftables/ruleset.nft

echo "[gateway] carregando nftables de $RULESET ..."
nft -f "$RULESET"
echo "[gateway] ruleset ativo (resumo):"
nft list ruleset | grep -E 'chain (input|forward|output)|policy' || true

echo "[gateway] pronto — roteando + filtrando. Mantendo container vivo."
exec sleep infinity
