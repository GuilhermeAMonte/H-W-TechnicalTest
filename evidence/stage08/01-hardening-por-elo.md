# Stage 08 — Contenção & Hardening (mitigação por elo, antes/depois)

Cada elo da cadeia da Stage 6 recebe uma mitigação, provada com a mesma tentativa
agora barrada. Filosofia: defesa em camadas — rede E aplicação, não uma só.

## Elo 2 — Movimento lateral DMZ→APP (mitigação de REDE, a principal)
**Antes:** F1 aceitava a subnet DMZ inteira (`172.30.10.0/24`) → o DVWA comprometido
(172.30.10.10) alcançava a app-api. (provado na Stage 6)
**Fix:** restringir F1 a aceitar SÓ o WAF (`172.30.10.5` → `172.30.20.10:8000`).
**Depois:**
```
DVWA (172.30.10.10) -> app-api:8000   -> TIMEOUT (bloqueado)   ← lateral contido
WAF  (172.30.10.5)  -> app-api:8000   -> succeeded              ← legítimo preservado
```
Impacto: uma regra de rede mata a cadeia inteira a partir do Elo 2. O host de entrada
comprometido não tem mais rota para a camada de aplicação.

## Elo 3 — Vazamento de credencial (mitigação de APP)
**Antes:** `GET /internal/db-config` (sem auth) devolvia a cred do DB.
**Fix:** endpoint de debug removido no modo HARDENED (reduz superfície).
**Depois:**
```
GET /internal/db-config  -> 404 NOT FOUND
```

## Elo 5 — RCE via command injection (mitigação de APP)
**Antes:** `GET /internal/net-check?host=127.0.0.1; <cmd>` concatenava no shell → RCE.
**Fix:** allowlist estrita do input (`[A-Za-z0-9._-]`) + `subprocess.run([...])` SEM
shell (lista de argumentos, sem interpretação de metacaracteres).
**Depois:**
```
GET /internal/net-check?host=127.0.0.1; id   -> 400 BAD REQUEST   ← injeção rejeitada
GET /internal/net-check?host=127.0.0.1       -> 200 (ping normal)  ← legítimo funciona
```

## Redução de superfície — Egress filtering
O default-deny no FORWARD já impede os segmentos de iniciarem conexão pra fora.
Prova (contém reverse shell e exfil externa):
```
app-api (APP) -> 8.8.8.8:53   -> TIMEOUT (bloqueado)
DVWA   (DMZ)  -> 8.8.8.8:53   -> TIMEOUT (bloqueado)
```
Nenhum segmento fala com a internet — só os fluxos internos explícitos (F1/F2).

## Elo 4 — DB inacessível da DMZ (já era defesa, mantido)
F2 continua permitindo só APP→DB; DMZ→DB segue negado (provado na Stage 6, Elo 4).

## Recomendação adicional (least-privilege no DB) — documentado
O `appuser` do Postgres é superuser (default da imagem). Hardening real: criar um
role dedicado com SELECT apenas nas tabelas necessárias (sem superuser, sem acesso a
`customers` se a app não precisa). Reduz o impacto de um SQLi/RCE que reuse a conta.
Não implementado neste ciclo por escopo de tempo; fica como recomendação priorizada.

## Resumo da contenção
| Elo | Vetor | Mitigação | Prova |
|---|---|---|---|
| 2 | lateral DMZ→APP | F1 só p/ o WAF | DVWA→app-api timeout |
| 3 | cred exposta | remover endpoint debug | 404 |
| 5 | RCE (cmd injection) | allowlist + no-shell | 400 |
| — | egress | default-deny FORWARD | internet timeout |
| 4 | DMZ→DB | segmentação (F2) | já barrado |
