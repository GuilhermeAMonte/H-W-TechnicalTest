#!/bin/sh
# docker-user-fix.sh — roda no netns do HOST (network_mode: host, privileged).
#
# PROBLEMA: o firewall do próprio Docker (cadeia FORWARD + isolação entre redes)
# derruba o tráfego inter-segmento ANTES de chegar no wg-gateway, porque o destino
# está fora da subnet de origem. Sem isso liberado, o nosso nftables nunca vê o pacote.
#
# SOLUÇÃO: liberar SÓ o trânsito inter-lab (172.30.0.0/16 <-> 172.30.0.0/16) na cadeia
# DOCKER-USER, que o Docker avalia ANTES da isolação dele. Não abre bypass: redes
# diferentes não têm caminho L2 direto — só passam pelo wg-gateway, que aplica F1/F2/deny.
#
# Detecta o backend do iptables (Docker Desktop usa legacy; Linux nativo pode usar nft).
# Idempotente: usa -C antes de -I pra não duplicar a cada 'up'.
set -e

LAB=172.30.0.0/16

for IPT in iptables-legacy iptables-nft iptables; do
    if "$IPT" -S DOCKER-USER >/dev/null 2>&1; then
        "$IPT" -C DOCKER-USER -s "$LAB" -d "$LAB" -j ACCEPT 2>/dev/null \
            || "$IPT" -I DOCKER-USER -s "$LAB" -d "$LAB" -j ACCEPT
        echo "[docker-user-fix] regra garantida via $IPT (lab $LAB)"
        exit 0
    fi
done

echo "[docker-user-fix] AVISO: cadeia DOCKER-USER não encontrada em nenhum backend." >&2
echo "[docker-user-fix] o roteamento inter-segmento pode não funcionar." >&2
exit 0
