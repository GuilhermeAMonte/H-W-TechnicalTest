# Stage 01 — Setup do gateway (evidência)

## Baseline: redes docker antes do lab
```
$ docker network ls
NETWORK ID     NAME                                 DRIVER    SCOPE
322eef68efa1   bridge                               bridge    local
16f70634be35   host                                 host      local
990d39a053f2   none                                 null      local
c538c2f9e85b   supabase_network_purple-paw-finder   bridge    local
```
Nenhuma rede `lab_*` — ambiente limpo.

## Subida do gateway + criação das 3 redes segmentadas
```
$ docker compose up -d --build
 ✔ Network lab_app       Created
 ✔ Network lab_db        Created
 ✔ Network lab_dmz       Created
 ✔ Container wg-gateway  Started
```

## Verificação: ip_forward + multi-homed (roteador nas 3 redes)
```
$ docker exec wg-gateway sh -c "sysctl net.ipv4.ip_forward; ip -brief addr"
net.ipv4.ip_forward = 1
lo               UNKNOWN        127.0.0.1/8 ::1/128
eth0@if236       UP             172.30.20.254/24   # APP
eth1@if238       UP             172.30.30.254/24   # DB
eth2@if240       UP             172.30.10.254/24   # DMZ
```

**Conclusões:**
- `ip_forward = 1` → kernel do gateway roteia entre segmentos.
- Gateway tem IP `.254` em cada uma das 3 redes (multi-homed) = é o roteador de cada segmento.
- Ordem `ethN` NÃO é estável → regras nftables casam por subnet, não por interface.
- Neste ponto ainda NÃO há nftables → gateway roteia tudo (inseguro, fechado no próximo bloco).
