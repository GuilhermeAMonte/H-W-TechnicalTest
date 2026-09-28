# Lab Red+Blue — Teste Técnico H&W (Segurança Ofensiva & Redes)

Ambiente de rede segmentado que sobe **com um comando** e serve para demonstrar o
ciclo completo: **atacar → entender → conter**, com evidência em cada passo.

> Status: **em construção** (scaffold Stage 0). As seções abaixo são preenchidas
> conforme as stages avançam — ver [`playbook-completo.md`](playbook-completo.md)
> e [`specs/`](specs/) para o plano dirigido por spec.

---

## Sumário (entregáveis do case)

| Parte | Tema | Seção | Evidência |
|---|---|---|---|
| 1 | Infra: VPN + Segmentação + Firewall | [Topologia](#topologia--segmentação) | `evidence/stage01`, `stage02` |
| 2 | Recon & Enumeração | [Superfície de ataque](#superfície-de-ataque-parte-2) | `evidence/stage05` |
| 3 | Exploração & Cadeia de ataque | [Relatório de pentest](#relatório-de-pentest-parte-3) | `evidence/stage06` |
| 4 | WAF & Bloqueio | [WAF](#waf-bloqueio-bypass-correção-parte-4) | `evidence/stage04`, `stage07` |
| 5 | Contenção & Hardening | [Hardening](#hardening-antesdepois-parte-5) | `evidence/stage08` |
| 6 | Mapeamento de portas | [Tabela de portas](#tabela-de-mapeamento-de-portas-parte-6) | `evidence/stage09` |

---

## Como rodar

Pré-requisitos: Docker + docker compose; cliente [WireGuard](https://www.wireguard.com/install/)
para o acesso admin; `ssh` (OpenSSH). Os segredos (chaves WireGuard/SSH) **não** vão no
git — são gerados localmente no primeiro `up`.

**Com `make`** (Linux/mac/WSL):
```bash
make up      # gera segredos se faltarem + sobe o lab inteiro
make ps      # estado dos containers
make down    # derruba (mantém dados)
make nuke    # derruba + apaga volumes
```

**Sem `make`** (Windows/PowerShell):
```bash
bash scripts/gen-keys.sh          # gera chaves WireGuard + SSH admin (idempotente)
docker compose up -d --build      # sobe o lab
```

### Acesso admin (VPN + SSH por chave)
1. Importe `gateway/wireguard/client.conf` no app WireGuard e **Ative**.
2. `ssh -i gateway/ssh/admin_ed25519 root@10.13.13.1` (login só por chave; senha desabilitada).
   Sem o túnel, o SSH é negado pelo firewall (admin só via VPN).

_(Reprodução de ataques/bloqueios/contenção: a preencher nas próximas stages.)_

---

## Topologia & Segmentação
_(Parte 1 — diagrama + explicação. A preencher. Fonte: [`specs/01-architecture.md`](specs/01-architecture.md).)_

## Superfície de ataque (Parte 2)
_(A preencher — mapa do que está exposto de cada ponto de vista.)_

## Relatório de pentest (Parte 3)
_(A preencher — cada achado: reprodução, evidência, impacto, CVSS aprox.)_

## WAF: bloqueio, bypass, correção (Parte 4)
_(A preencher — request, 403, log, tentativa de evasão, regra corrigida.)_

## Hardening antes/depois (Parte 5)
_(A preencher — mitigação por elo da cadeia, com prova de barrado.)_

## Tabela de mapeamento de portas (Parte 6)
_(A preencher — host, porta, protocolo, quem acessa, justificativa.)_

## Trade-offs, limitações e escala pra nuvem real
_(A preencher — mapeamento pra AWS SG/NACL, Cloudflare na borda, Proxmox.)_

---

## Estrutura do repositório

```
specs/       Especificação dirigida (fonte da verdade por stage)
gateway/     wg-gateway: WireGuard + nftables (roteador/firewall)
waf/         Nginx + ModSecurity + OWASP CRS
targets/     dvwa (alvo) · app-api (pivô) · postgres (dados)
scripts/     helpers de recon/ataque
evidence/    provas por stage (stageNN)
```
