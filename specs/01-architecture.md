# 01 — Arquitetura & Topologia

## Diagrama lógico

```
                         Internet / Host
                               │
                        (WireGuard :51820/udp)
                               │
                    ┌──────────▼───────────┐
                    │      wg-gateway       │  NET_ADMIN, ip_forward=1
                    │  WireGuard + nftables │  ÚNICO roteador entre segmentos
                    │   default-deny FWD    │  policy drop em INPUT+FORWARD
                    └───┬───────┬───────┬───┘
             .254 (dmz) │  .254(app)│  .254(db)│      ← gateway tem IP em cada rede
                ┌───────▼──┐  ┌───▼─────┐  ┌───▼──────┐
      DMZ       │   waf    │  │ app-api │  │ postgres │
 172.30.10.0/24 │ Nginx +  │  │  Flask  │  │   5432   │
                │ ModSec + │─▶│ (pivô)  │─▶│ (fechado)│
                │  CRS     │  └─────────┘  └──────────┘
                │    │     │   APP           DB
                │    ▼     │  172.30.20.0/24 172.30.30.0/24
                │  dvwa    │
                │ (alvo)   │
                └──────────┘
```

## Segmentos

| Segmento | Rede docker | Subnet | Gateway IP | Hosts |
|---|---|---|---|---|
| DMZ | `lab_dmz` (internal) | 172.30.10.0/24 | 172.30.10.254 | `waf`, `dvwa` |
| APP | `lab_app` (internal) | 172.30.20.0/24 | 172.30.20.254 | `app-api` |
| DB  | `lab_db` (internal)  | 172.30.30.0/24 | 172.30.30.254 | `postgres` |

`.1` fica reservado pro bridge docker; hosts em `.10+`; gateway em `.254`.
(IPs exatos dos hosts fixados na Stage 3.)

## Por que um container-roteador (e não só redes docker)

Redes docker separadas **isolam L2**, mas o daemon habilita forward entre bridges
por padrão — dois containers em redes distintas podem se falar se houver rota.
`internal: true` corta a rota pra internet, mas não dá controle L3/L4 fino
(porta X sim, porta Y não; conntrack; log).

Solução fiel ao diagrama: **um container conectado às 3 redes** com `NET_ADMIN` e
`ip_forward=1`, rodando **nftables** em default-deny no `FORWARD`. Todo tráfego
inter-segmento passa por ele e só o explicitamente liberado atravessa. É o
análogo local de um Security Group / firewall de borda.

## Papéis dos hosts

- **wg-gateway** — borda. Termina o túnel WireGuard (entrada admin) e faz o
  roteamento+filtragem entre DMZ/APP/DB. Sem ele, sem comunicação inter-rede.
- **waf** — Nginx + ModSecurity + OWASP CRS. Reverse proxy na frente do DVWA.
  Único ponto que fala com a APP. Stage 4 sobe em `DetectionOnly`, Stage 7 vira `On`.
- **dvwa** — alvo vulnerável (SQLi, XSS, upload inseguro). Só alcançável via WAF.
- **app-api** — API interna (Flask). Guarda a cred do Postgres e expõe um endpoint
  **sem autenticação** que a vaza (pivô lateral proposital). Só recebe da DMZ.
- **postgres** — dados sensíveis. Só alcançável pela APP. Alvo da exfiltração.

## Fluxo de dados legítimo

```
cliente → (VPN) → gateway → waf(DMZ) → dvwa(DMZ)
                                   └──→ app-api(APP) → postgres(DB)
admin   → (VPN) → gateway → SSH/gestão dos hosts
```

## Mapeamento pra nuvem real (discussão — detalhar no README)

| Local | Nuvem |
|---|---|
| nftables no gateway | Security Groups / NACL (AWS), regras Proxmox |
| wg-gateway | VPN gateway gerenciado / bastion |
| redes docker /24 | subnets/VPCs por tier |
| WAF Nginx+ModSec | Cloudflare WAF / AWS WAF na borda |
| default-deny FORWARD | deny-all + regras explícitas de SG |
