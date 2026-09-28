# 00 — Overview & Escopo

> Fonte da verdade do projeto. Deriva do enunciado do case (PDF H&W) e do
> `CLAUDE.md`. Se algo aqui conflitar com o código, a spec ganha — ou a spec
> muda de propósito e explícito.

## Objetivo

Montar localmente, com **um comando**, uma rede segmentada e demonstrar as duas
faces do trabalho: **atacar** um alvo vulnerável dentro dela e **defender**
fechando cada brecha aberta. Saber proteger é consequência de saber atacar.

## Recorte

Modelo local de um recorte de infra multi-cloud/híbrida (AWS, OVH, Contabo,
Proxmox, Cloudflare). Não reproduz a nuvem inteira — modela o padrão:
borda VPN+firewall → DMZ (WAF+alvo) → APP (pivô) → DB (dados).

## Regras do jogo (viram regras de firewall — ver `02-firewall-spec.md`)

1. **DB** só é acessível pela camada **APP**. Nunca da DMZ, nunca da internet.
2. **APP** só recebe tráfego vindo do **WAF** na DMZ.
3. **Acesso administrativo** (SSH/painel) somente via **VPN**.
4. **Default-deny**: tudo que não for explicitamente permitido é negado (INPUT + FORWARD).

## Decisões travadas

| Decisão | Escolha | Motivo |
|---|---|---|
| Orquestração | `docker-compose`, host único | Reprodutível, `make up` |
| Borda | container `wg-gateway` (WireGuard + nftables, `NET_ADMIN`) | Fiel ao diagrama; firewall no FORWARD |
| Firewall | **nftables** default-deny | Sintaxe moderna, `conntrack` nativo |
| WAF | **ModSecurity + OWASP CRS** sobre Nginx | Pedido explícito do case |
| Alvo vulnerável | **DVWA** atrás do WAF | SQLi/XSS/upload inseguro num só app |
| Pivô lateral | `app-api` (Flask) com endpoint sem-auth que vaza cred do DB | Elo lateral proposital |
| DB | **Postgres** fechado, com dado sensível | Alvo de exfiltração |

## Cadeia de ataque que o lab PRECISA permitir (antes do hardening)

`recon` → `SQLi + XSS no DVWA` → `upload inseguro = webshell = foothold DMZ`
→ `curl do webshell na app-api (DMZ→APP)` → `endpoint interno sem-auth vaza cred Postgres`
→ `exfil do DB (APP→DB)`.

Cada elo tem mitigação clara na Parte 5 (ver `03-attack-chain.md`).

## Protocolo de trabalho (do CLAUDE.md)

- **Infra (Stages 1,2,3,4,9)** = MODO PROFESSOR: um comando por vez, explica, espera saída.
- **Ofensivo (Stages 5,6,7,8)** = COPILOTO: candidato pilota, revisão de payload/CVSS.
- Evidência religiosa em `evidence/stageNN/` (comando + saída, prints, pcap, logs).

## Bônus (agora no escopo — ver `05-bonus-and-deploy.md`)

Priorizados por custo/impacto pro prazo 4–5 dias. Ordem de ataque:
1. Suricata/Zeek detectando a própria cadeia (alto impacto, casa com evidência).
2. Script único que automatiza a cadeia de ponta a ponta.
3. Mapa da kill chain versionado + discussão de mapeamento pra nuvem real.
4. fail2ban/rate-limiting na borda; logs centralizados com alerta.
5. Escalada de privilégio no host comprometido.
6. IaC (Terraform/Ansible) — se sobrar tempo.

## Deploy explorável (Stage 10 — opcional)

Objetivo: entregar site explorável pra banca **sem** expor RCE cru na internet.
Padrão escolhido: **VPN-gated** (só `51820/udp` público; banca explora via peer
WireGuard). Alternativas: túnel efêmero com auth+allowlist, ou VPS gated.
Detalhe + risco em `05-bonus-and-deploy.md`. Não cria conta/credencial: o
candidato pilota hosting/DNS.

## Fora de escopo

- Reproduzir a nuvem inteira (só discussão de mapeamento no README).
- Prazo: 4–5 dias — bônus abaixo da linha de corte ficam documentados como "faria".

## Nota de segurança do código (app-api)

O repositório segue o padrão appsec de validação de input **exceto** por
vulnerabilidades **intencionais e comentadas** que são o objeto do teste
(endpoint sem-auth que vaza credencial, DVWA). Toda vuln proposital fica
marcada com `# VULN-INTENCIONAL:` no código e catalogada em `03-attack-chain.md`.
