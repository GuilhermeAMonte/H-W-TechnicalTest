# Stage 06 — Achados #1 e #2: SQL Injection (clássico) e SQL Injection (blind/time-based)

## Achado #1 — SQL Injection clássico (in-band)
- **Módulo:** DVWA `vulnerabilities/sqli/` (nível de segurança: low)
- **URL:** `http://172.30.10.5:8080/vulnerabilities/sqli/`
- **Payload:** `1' OR '1'='1`
- **Reprodução:** campo "User ID" aceita entrada não sanitizada, concatenada
  diretamente na query SQL (`WHERE user_id = '$id'`). O payload transforma a
  condição em sempre-verdadeira, retornando **todos** os registros da tabela
  de usuários em vez de apenas um.
- **Evidência:** [PENDENTE — colar aqui a lista de usuários/dados retornados
  na tela, print ou texto]
- **Impacto:** exposição total da tabela de usuários (dados de autenticação).
  Base para ataques subsequentes (credential stuffing, escalada).
- **CVSS aprox.:** 9.8 (Crítico) — AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (sem auth
  prévia no contexto do módulo, alta confidencialidade/integridade).

## Achado #2 — SQL Injection Blind (time-based)
- **Módulo:** DVWA `vulnerabilities/sqli_blind/` (nível de segurança: low)
- **URL:** `http://172.30.10.5:8080/vulnerabilities/sqli_blind/`
- **Payloads:**
  - Positivo: `1' AND SLEEP(5)-- -`
  - Controle (negativo): `1' AND 1=2 AND SLEEP(5)-- -`
- **Reprodução:** a aplicação não exibe dados diretamente (só "exists"/"missing"),
  mas o tempo de resposta prova a execução do SQL injetado:
  - Payload positivo: resposta demorou **>5 segundos** (SLEEP executado).
  - Payload de controle: resposta **imediata** (condição `1=2` é falsa, então
    `AND SLEEP(5)` nunca é avaliado — a curto-circuito do AND no MySQL).
  - Nota técnica: `SLEEP()` retorna `0` (falso) após dormir, então a mensagem
    da tela é sempre "MISSING" nos dois casos — a prova está no TEMPO, não no
    texto exibido.
- **Evidência:** delay >5s no payload 1 vs. resposta instantânea no payload 2
  (diferença consistente, reprodutível).
- **Impacto:** confirma injeção mesmo sem retorno visível de dados — permite
  exfiltração byte-a-byte via condições booleanas/temporais (ex.: `sqlmap
  --technique=T` automatizaria a extração completa).
- **CVSS aprox.:** 9.1 (Crítico) — mesma superfície do #1, mas exploração mais
  lenta (sem impacto direto de integridade imediato, então leve ajuste de I).

## Próximo
Achado #3: XSS refletido (`vulnerabilities/xss_r/`).
