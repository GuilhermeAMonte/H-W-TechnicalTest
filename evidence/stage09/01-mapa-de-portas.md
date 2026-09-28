# Stage 09 — Mapa de portas & evidência final

## Tabela de mapeamento de portas

| Host | Porta | Proto | Quem pode acessar | Justificativa |
|---|---|---|---|---|
| wg-gateway (edge) | 51820 | UDP | qualquer (internet/host) | Entrada da VPN (WireGuard) — único ponto público |
| wg-gateway | 22 | TCP | só sub-rede VPN (10.13.13.0/24) | Admin SSH só via VPN (I2); key-only |
| waf | 8080 | TCP | só via VPN (F-VPN: 10.13.13.0/24) | Ponto de entrada web; reverse proxy p/ DVWA |
| dvwa | 80 | TCP | só o WAF (mesmo segmento DMZ) | Alvo atrás do WAF; nunca acessado direto |
| app-api | 8000 | TCP | **só o WAF** (F1 hardened: 172.30.10.5) | API interna; DVWA NÃO alcança mais (contenção) |
| postgres | 5432 | TCP | **só a APP** (F2: 172.30.20.0/24) | Banco fechado; DMZ/internet nunca |

Nenhuma porta de dvwa/app-api/postgres é publicada no host (`ports:` só no gateway/WAF).

## nmap externo (host, sem VPN) — superfície mínima
```
TCP top-1000: nenhuma porta do lab (só 135/445 do Windows)
UDP: 51820/udp open|filtered (WireGuard, silencioso)
```
(detalhe em stage05/01) — de fora, nada do lab é enumerável.

## Antes/Depois do hardening — ponto de vista DMZ (host comprometido)
| Caminho | Antes (Stage 6) | Depois (Stage 8) |
|---|---|---|
| DMZ (DVWA) -> app-api:8000 | ABERTO (F1 = subnet toda) | **FILTRADO (timeout)** — F1 só p/ WAF |
| DMZ (DVWA) -> postgres:5432 | filtrado (F2) | filtrado (F2) |
| DMZ (DVWA) -> internet | filtrado | filtrado (egress default-deny) |

Prova (depois):
```
DVWA -> 172.30.20.10:8000  -> timeout (FILTRADO)   ← lateral contido pelo hardening
DVWA -> 172.30.30.10:5432  -> timeout (FILTRADO)
```

## Caminho que DEVE ser bloqueado, bloqueado (requisito do case)
```
# DMZ -> DB (deve ser sempre negado)
DVWA (172.30.10.10) -> postgres:5432   -> TIMEOUT (recusado)
```
vs. o caminho legítimo:
```
# APP -> DB (permitido, F2)
app-api (172.30.20.10) -> postgres:5432 -> ABERTO
```

## Leitura (interpretação dos resultados)
- **Timeout (filtered)** = firewall descartando em silêncio (default-deny), não "porta
  fechada". É a assinatura de segmentação ativa.
- O hardening (Elo 2) mudou o resultado do scan DMZ->APP de aberto para filtrado —
  o firewall passou a ser a diferença, não a topologia.
- Cada porta aberta tem um "quem pode" restrito por regra explícita; todo o resto
  cai no default-deny.
