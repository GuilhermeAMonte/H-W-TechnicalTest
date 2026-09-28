# Stage 07 — Fix do bypass (CSP) + request legítimo continua passando

## Problema
O DOM XSS via fragmento (#) não é visível ao WAF (o payload nunca vai ao servidor),
então NÃO existe regra de ModSecurity que o bloqueie. Precisa de outra camada.

## Fix aplicado (defesa em profundidade no WAF/proxy)
O WAF passa a injetar um header `Content-Security-Policy` na resposta. Ele não
depende de inspecionar o payload — manda o NAVEGADOR recusar executar script inline.

Implementação: build de imagem própria do WAF (`waf/Dockerfile`) que substitui o
template `cors.conf.template` por uma versão com:
```
more_set_headers "Content-Security-Policy: default-src 'self'; script-src 'self'; object-src 'none'";
```
(Build no root evita o erro de permissão de montar por cima do `includes/` em runtime,
já que o container roda como usuário não-root.)

## Provas

### Header presente + página legítima passa (sem falso-positivo)
```
$ curl -D - http://172.30.10.5:8080/login.php
HTTP/1.1 200 OK
Content-Security-Policy: default-src 'self'; script-src 'self'; object-src 'none'
```

### SQLi continua bloqueado (não quebrou a proteção anterior)
```
GET /?id=1 UNION SELECT user   -> 403
```

### DOM XSS via fragmento: request passa, mas script NÃO executa
```
/vulnerabilities/xss_d/?default=x#<script>alert(document.domain)</script>
-> página abre (sem 403), MAS o alert não dispara
-> Console: "Refused to execute inline script because it violates the
   following Content-Security-Policy directive: script-src 'self'"
```

## Resultado
- Ataque que o WAF NÃO conseguia ver: neutralizado por outra camada (CSP no cliente).
- Requisição legítima: continua passando (200, sem falso-positivo).
- Proteções anteriores (SQLi/XSS na query): intactas (403).

## Trade-off documentado (maturidade)
`script-src 'self'` bloqueia TODO script inline, inclusive o inline legítimo do
próprio DVWA — em uma app real usaríamos nonces/hashes por script para permitir os
legítimos e barrar os injetados. Aqui, como o DVWA é o alvo proposital e não o
modificamos, o CSP estrito demonstra o conceito com o trade-off explícito.

## Fix primário (app-level, referência)
A causa raiz é o JS do módulo usando `document.write` sobre input não confiável.
Correção definitiva: `textContent`/encoding de saída no código cliente.
