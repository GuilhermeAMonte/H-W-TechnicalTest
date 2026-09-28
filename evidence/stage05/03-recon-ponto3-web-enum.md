# Stage 05 — Enumeração web completa (via VPN → WAF → DVWA)

## Ferramenta e alvo
`ffuf v2.3.0`, wordlist própria (`scripts/wordlists/common-web.txt`, ~130 entradas
DVWA-específicas + genéricas), alvo `http://172.30.10.5:8080/FUZZ` (através do WAF,
com VPN ativa).

## Fingerprint (headers)
```
$ curl.exe -I http://172.30.10.5:8080/login.php
Server: nginx
Set-Cookie: PHPSESSID=...            <- backend PHP
Set-Cookie: security=low             <- nível de segurança do DVWA exposto em cookie
Access-Control-Allow-Headers: *      <- CORS aberto
```
Sem `X-Powered-By` — o WAF/Nginx provavelmente remove o header (comportamento
hardened comum). O cookie `security=low` é notável: um atacante pode **manipular
esse cookie diretamente** para tentar mudar o nível de proteção do app (a validar).

## Resultado do ffuf (132 paths testados, 0 erros)

### Módulos vulneráveis mapeados (301 = diretório existe)
```
vulnerabilities/sqli          vulnerabilities/sqli_blind
vulnerabilities/xss_r/_s/_d   vulnerabilities/upload
vulnerabilities/exec          vulnerabilities/fi
vulnerabilities/csrf          vulnerabilities/brute
vulnerabilities/captcha       vulnerabilities/weak_id
hackable/uploads              <- destino do File Upload (alvo da Stage 6)
config/  docs/  external/
```
Mapa completo da superfície ofensiva do DVWA — confirma os vetores disponíveis
para a cadeia de ataque (Stage 6): SQLi, XSS, upload inseguro, command exec, LFI/RFI.

### Páginas acessíveis sem autenticação (200)
```
login.php  robots.txt  favicon.ico  about.php
setup.php        <- reseta o banco SEM login (exposição — qualquer um reinicializa os dados)
README.md        <- vaza versão exata do DVWA (fingerprint p/ CVE conhecida)
CHANGELOG.md      <- idem
instructions.php  <- conteúdo é o manual genérico de instalação, não vaza versão da instância rodando
```

### Achado lateral: endpoint de health do WAF
```
healthz  [200, 2 bytes]
```
Não pertence ao DVWA — é o healthcheck da própria imagem `owasp/modsecurity-crs`.
Confirma a tecnologia da borda por enumeração (não só por header).

### Hardening já presente por padrão (403)
```
.htaccess  .htpasswd  server-status
```
Nginx bloqueia esses arquivos "de fábrica" — não é algo que configuramos, é
comportamento padrão da imagem, mas vale registrar como controle já ativo.

### Ruído (404 real, ~130 paths)
Tamanho de resposta consistente (~278–292 bytes) confirma página de erro real do
DVWA — sem falso-positivo de redirect genérico (validado comparando com o baseline
antes de rodar o ffuf).

## Conclusão / mapa de superfície (Ponto 3 parcial)
A partir da VPN, através do WAF, um atacante já enumera:
- **11 módulos vulneráveis** conhecidos, prontos para exploração dirigida.
- **Destino exato do upload inseguro** (`hackable/uploads/`), útil para a entrega
  do payload na Fase "Delivery" da kill chain.
- **Versão do DVWA** via README/CHANGELOG (para checar CVEs específicas).
- **Reset de banco sem autenticação** (`setup.php`) — pequena exposição adicional.

O "Ponto 3" completo do recon (visão de **dentro da DMZ**, pós-foothold) só se
completa depois de obter execução de comando no container do DVWA — ver Stage 06.
Este documento cobre a enumeração **externa/pré-exploração** através do WAF.
