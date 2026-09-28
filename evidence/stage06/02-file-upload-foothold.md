# Stage 06 — Achado #4: Upload Inseguro → Webshell → RCE (Foothold na DMZ)

## Módulo
DVWA `vulnerabilities/upload/` (nível low — sem validação de extensão/MIME/magic bytes).

## Payload
`evidence/stage06/payloads/webshell.php` — PHP mínimo, executa comando via `$_GET['cmd']`
usando `system()`.

## Reprodução
1. Upload de `webshell.php` via o formulário do módulo — aceito sem qualquer validação.
2. Confirmação do DVWA: salvo em `../../hackable/uploads/webshell.php` (sem rename).
3. Acesso direto: `http://172.30.10.5:8080/hackable/uploads/webshell.php?cmd=whoami`
4. **Resposta: `www-data`** — confirma execução de comando arbitrário no container do DVWA.

## Evidência
```
GET /hackable/uploads/webshell.php?cmd=whoami
-> www-data
```

## Impacto
**RCE completo** no container do DVWA (DMZ). O atacante controla o processo do
webserver — pode ler arquivos, listar rede interna, e (próximo passo da cadeia)
usar esse acesso como pivô para alcançar a camada APP (regra F1: DMZ -> APP:8000).

## CVSS aprox.
**9.8 (Crítico)** — AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H. Execução remota de código
sem autenticação (no contexto do módulo), controle total do processo.

## Kill Chain — fases cobertas
- **Weaponization:** payload (`webshell.php`) preparado.
- **Delivery:** upload via formulário vulnerável.
- **Exploitation:** ausência de validação permite o upload do payload malicioso.
- **Installation:** webshell fica persistente em `hackable/uploads/`, acessível via HTTP.
- **Command & Control:** confirmado com `?cmd=whoami`.

## Próximo elo
Actions on Objectives: usar a webshell para `curl` na `app-api` (regra F1,
DMZ -> APP:8000), validando o movimento lateral e coletando a credencial exposta
em `/internal/db-config`. Ver `evidence/stage06/03-movimento-lateral.md`.
