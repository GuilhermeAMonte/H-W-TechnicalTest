# Topologia — Diagrama

> Mermaid (renderiza no GitHub) + ASCII de fallback. Reusar no README (Parte 1).

## Mermaid

```mermaid
flowchart TD
    NET["Internet / Host"]
    subgraph EDGE["Borda"]
        GW["wg-gateway<br/>WireGuard + nftables<br/>default-deny FORWARD/INPUT"]
    end
    subgraph DMZ["DMZ · 172.30.10.0/24 (internal)"]
        WAF["waf<br/>Nginx + ModSecurity + CRS"]
        DVWA["dvwa<br/>alvo vulnerável"]
    end
    subgraph APP["APP · 172.30.20.0/24 (internal)"]
        API["app-api (Flask)<br/>pivô · vaza cred DB"]
    end
    subgraph DB["DB · 172.30.30.0/24 (internal)"]
        PG["postgres<br/>dados sensíveis"]
    end

    NET -->|"51820/udp WireGuard"| GW
    NET -.->|"admin SSH só via VPN"| GW
    GW --> WAF
    WAF --> DVWA
    WAF -->|"F1: tcp/8000"| API
    API -->|"F2: tcp/5432"| PG

    WAF -. "F4: DMZ→DB NEGADO" .-x PG
    NET -. "F5: internet→APP/DB NEGADO" .-x API
```

## ASCII (fallback)

```
                 Internet / Host
                        │  51820/udp (WireGuard)
                 ┌──────▼──────┐
                 │  wg-gateway │  nftables default-deny (FWD+INPUT)
                 └──┬────┬───┬─┘
        ┌───────────┘    │   └───────────┐
   ┌────▼─────┐     ┌────▼────┐     ┌────▼─────┐
   │   DMZ    │     │   APP   │     │    DB    │
   │ waf→dvwa │────▶│ app-api │────▶│ postgres │
   │ .10.0/24 │ F1  │ .20.0/24│ F2  │ .30.0/24 │
   └──────────┘8000 └─────────┘5432 └──────────┘
        └────────── F4: DMZ→DB NEGADO ─────────X
```

## Legenda
- **F1/F2/F4/F5** = regras da matriz em `../02-firewall-spec.md`.
- Linha cheia = fluxo permitido. Linha tracejada com X = fluxo negado (prova de segmentação).
- `internal: true` = rede sem rota pra internet; só o gateway conecta segmentos.
