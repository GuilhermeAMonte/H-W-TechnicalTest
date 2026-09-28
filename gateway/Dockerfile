# gateway/Dockerfile — wg-gateway: roteador + firewall (nftables) + entrada VPN (WireGuard)
FROM debian:bookworm-slim

# Ferramentas do papel do host:
#   nftables         -> firewall (escreve no netfilter; exige NET_ADMIN)
#   wireguard-tools  -> VPN (wg / wg-quick), Stage 2
#   iproute2         -> ip addr / ip route (inspecionar roteamento)
#   tcpdump          -> captura de pacote (evidência/pcap)
#   curl, netcat     -> testes de conectividade (provar allow/deny)
#   openssh-server   -> alvo de admin da Stage 2 (SSH só via VPN)
#   procps, iputils  -> sysctl/ps, ping
RUN apt-get update && apt-get install -y --no-install-recommends \
        nftables iptables wireguard-tools iproute2 tcpdump \
        curl netcat-openbsd openssh-server procps iputils-ping \
    && rm -rf /var/lib/apt/lists/*

# Entrypoint: carrega o nftables no boot e mantém o container vivo.
# (O ruleset.nft entra via bind-mount em /etc/nftables — ver docker-compose.yml.)
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
