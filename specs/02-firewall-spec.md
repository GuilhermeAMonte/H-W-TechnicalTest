# 02 — Especificação de Firewall (nftables)

> Traduz as "regras do jogo" numa matriz testável. Cada linha ALLOW vira uma
> regra nftables comentada; tudo o mais cai no default-deny. Toda regra tem
> um teste de aceite em `04-acceptance.md`.

## Princípios

- **policy `drop`** nas chains `input` e `forward` da tabela `inet filter`.
- **conntrack** primeiro: `ct state established,related accept` (respostas voltam
  sem regra explícita por sentido). Só o **primeiro pacote** (new) é avaliado
  contra a matriz.
- Regras por **sentido** (origem→destino), na direção que INICIA a conexão.
- Loopback liberado; o resto negado e (amostra) logado antes do drop.

## Matriz de fluxo (FORWARD — entre segmentos)

| # | Origem | Destino | Proto/Porta | Ação | Justificativa |
|---|---|---|---|---|---|
| F1 | DMZ `waf` | APP `app-api` | tcp/8000 | **ALLOW** | WAF encaminha p/ API. Só a porta da app. |
| F2 | APP `app-api` | DB `postgres` | tcp/5432 | **ALLOW** | API lê o banco. Só a porta do Postgres. |
| F3 | qualquer | estabelecido | — | **ALLOW** | Respostas via conntrack. |
| F4 | DMZ | DB | * | **DENY** | Banco nunca da DMZ (regra 1). |
| F5 | internet/host | APP, DB | * | **DENY** | Só a borda entra; back-tiers fechados. |
| F6 | APP | internet (egress) | * | **DENY*** | Sem saída desnecessária (hardening St.8). |
| F7 | DMZ→DMZ, etc. | — | — | default | Não listado = negado. |

\* F6 nasce permissivo e é fechado na Parte 5 (egress-filtering), com prova antes/depois.

## Matriz INPUT (tráfego PRA o próprio gateway)

| # | Origem | Porta | Ação | Justificativa |
|---|---|---|---|---|
| I1 | host/internet | udp/51820 | **ALLOW** | Handshake WireGuard (entrada VPN). |
| I2 | rede VPN (`10.13.13.0/24`) | tcp/22 | **ALLOW** | Admin SSH só via túnel (regra 3). |
| I3 | qualquer | tcp/22 (fora da VPN) | **DENY** | SSH negado sem túnel. |
| I4 | lo | * | **ALLOW** | Loopback. |
| I5 | resto | * | **DENY** | Default-deny INPUT. |

(Sub-rede VPN provisória `10.13.13.0/24`; fixada na Stage 2.)

## Ordem de avaliação (importa)

```
1. ct established,related  → accept   (barato, cobre respostas)
2. iif lo                  → accept
3. regras ALLOW específicas (F1, F2, I1, I2 …)
4. log rate-limited "DROP:"           (amostra pra evidência)
5. policy drop                         (implícito, tudo o resto)
```

Estabelecido antes das regras específicas = performance + evita liberar o
sentido de volta manualmente. Log antes do drop = prova de "negado sendo negado".

## Provas obrigatórias (evidence/stage01, stage09)

- `waf → app-api:8000` **OK** (F1).
- `app-api → postgres:5432` **OK** (F2).
- `waf → postgres:5432` **RECUSADO** (F4) — o print-chave DMZ→DB negado.
- `host → app-api` / `host → postgres` **RECUSADO** (F5).
- SSH ao gateway **sem** túnel → negado; **com** túnel → OK (I2/I3).

## Anti-padrões proibidos

- Nada de `accept` largo por conveniência ("libera tudo e vê depois").
- Sem `flush ruleset` em produção do lab sem explicar impacto + confirmar.
- Regra sem comentário = regra proibida (o case exige liberações comentadas).
