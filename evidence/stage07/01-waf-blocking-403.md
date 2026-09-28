# Stage 07 — WAF em blocking: SQLi bloqueado (403)

## Mudança
`MODSEC_RULE_ENGINE: DetectionOnly` → `On` (mesma regra que na Stage 4 só logava,
agora bloqueia). Reprodutível no compose.

## Antes (Stage 4, DetectionOnly) vs Depois (Stage 7, On)
Mesmo ataque SQLi:
```
GET /?id=1 UNION SELECT user FROM users
```
| | Stage 4 (DetectionOnly) | Stage 7 (On) |
|---|---|---|
| Resposta | 302 (passou) | **403 (bloqueado)** |
| Log | detectado, não bloqueado | detectado E bloqueado |

## Prova do bloqueio (cliente via VPN)
```
> try { (Invoke-WebRequest "http://172.30.10.5:8080/?id=1%20UNION%20SELECT%20user%20FROM%20users").StatusCode }
    catch { "BLOQUEADO -> " + $_.Exception.Response.StatusCode.value__ }
BLOQUEADO -> 403
```

## Log do WAF (audit)
```
"secrules_engine":"Enabled"
"message":"SQL Injection Attack Detected via libinjection"   ruleId 942100
"message":"Inbound Anomaly Score Exceeded (Total Score: 23)"  ruleId 949110  (threshold 5)
```
A regra 949110 (avaliação de bloqueio) agora aplica a ação disruptiva (deny/403),
porque `SecRuleEngine On`. O score de anomalia (23) passou do limite (5).

## Próximo
Tentar burlar o WAF (evasão) e depois corrigir a regra que fecha o bypass — `02-*`.
