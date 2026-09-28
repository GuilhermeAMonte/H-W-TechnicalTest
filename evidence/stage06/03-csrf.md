# Stage 06 — Achado: CSRF (Change Password)

## Módulo
DVWA `vulnerabilities/csrf/` (nível low — sem token anti-CSRF).

## Payload
Página HTML local com link disfarçado, navegação de topo (não subresource):
```html
<a href="http://172.30.10.5:8080/vulnerabilities/csrf/?password_new=hacked123&password_conf=hacked123&Change=Change#">
  Clique aqui
</a>
```

## Nota técnica relevante
Primeira tentativa usou `<img src="...">` (carregamento automático) e **falhou**:
navegadores modernos aplicam `SameSite=Lax` por padrão nos cookies de sessão,
que bloqueia o envio do cookie em requisições "subresource" de terceiros (como
`<img>`), mas **permite** em navegação de topo (clique em link, redirect de página
inteira). Trocando para um `<a href>` clicável, o ataque funcionou — o cookie de
sessão foi enviado normalmente.

**Achado adicional para o relatório:** o `SameSite=Lax` do navegador é uma
mitigação parcial real (bloqueia o vetor `<img>`), mas não impede o ataque via
link clicável — o DVWA em si não implementa nenhuma defesa própria (token CSRF).

## Reprodução
1. Logado no DVWA como admin, sessão ativa.
2. Abrir página HTML local com o link forjado.
3. Clicar no link (simula vítima clicando em algo aparentemente inofensivo).
4. Senha do usuário alterada para `hacked123` sem o usuário ter usado o formulário real.

## Impacto
Comprometimento de conta via engenharia social mínima (1 clique). Em conjunto com
outras vulns (ex.: XSS armazenado), o vetor de entrega poderia ser automatizado
sem interação visível da vítima.

## CVSS aprox.
**8.8 (Alto)** — AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (requer interação do usuário,
mas sem outros pré-requisitos).
