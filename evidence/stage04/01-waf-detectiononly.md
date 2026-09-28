# Stage 04 — WAF em DetectionOnly (ataque passa, mas é logado)

## Setup
- Imagem: `owasp/modsecurity-crs:nginx` (Nginx + ModSecurity + OWASP CRS 4.29).
- `SecRuleEngine DetectionOnly`, `PARANOIA=1`, `BACKEND=http://dvwa:80`, `PORT=8080`.
- Audit log em `/dev/stdout` (JSON) → lê-se com `docker logs waf`.
- Nota: `PORT` tem de ser >1024 (imagem roda sem privilégio) — usamos 8080.

## Ataque: SQLi trivial através do WAF
```
$ curl -s -o /dev/null -w '%{http_code}' \
    'http://172.30.10.5:8080/?q=1 UNION SELECT user FROM users'
302
```
**HTTP 302 (redirect p/ login.php do DVWA) — NÃO 403.** O ataque PASSOU (DetectionOnly).

## Detecção registrada (audit log JSON, resumo)
```
secrules_engine: "DetectionOnly"
request.uri: /?q=1%20UNION%20SELECT%20user%20FROM%20users
messages:
  - ruleId 942100  "SQL Injection Attack Detected via libinjection"  (ARGS:q)
  - ruleId 942190  "Detects SQL code execution ... UNION SELECT"
  - ruleId 942270  "Looking for basic sql injection (union.*select.*from)"
  - ruleId 942360  "Concatenated basic SQL injection"
  - ruleId 949110  "Inbound Anomaly Score Exceeded (Total Score: 23)"  (threshold 5)
```

## Leitura
- O CRS **detectou** o SQLi por várias regras da família 942xxx e somou **anomaly
  score 23** (limite de bloqueio = 5).
- A regra `949110` é a que **bloquearia** em modo `On` (score >= 5). Em `DetectionOnly`
  ela apenas **loga** → o request seguiu pro backend (302).
- É exatamente esse botão que viramos na Stage 7 (`On`): aí o mesmo request vira 403.

Bônus: `920350` também disparou ("Host header is a numeric IP address") — porque
testamos por IP; via hostname legítimo não dispararia.
