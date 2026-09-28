# Stage 07 — Bypass do WAF: DOM XSS via fragmento (#)

## Tentativas de evasão testadas

### Codificação dupla — FALHOU (WAF segurou)
```
GET /?id=1%2520UNION%2520SELECT%2520user   -> 403
```
O CRS aplica transformações (`t:urlDecodeUni`) que decodificam ANTES de analisar,
então "desfaz" a codificação dupla e detecta o SQLi. Evasão por encoding é derrotada
por um WAF bem configurado. (Achado: controle robusto contra evasão básica.)

### DOM XSS via fragmento — SUCESSO (bypass real)
Contraste com o mesmo payload:
```
# na QUERY (servidor recebe -> WAF vê -> bloqueia):
/vulnerabilities/xss_d/?default=<script>alert(document.domain)</script>   -> 403

# no FRAGMENTO (servidor NÃO recebe -> WAF não vê -> passa):
/vulnerabilities/xss_d/?default=x#<script>alert(document.domain)</script>  -> SEM 403, alert dispara
```

## Por que funciona
Tudo após o `#` (fragmento) **nunca é enviado ao servidor** — fica só no navegador.
O servidor recebeu apenas `?default=x` (inofensivo). O JS do módulo DOM lê o href
completo (incluindo o fragmento), extrai o que vem após `default=` e escreve na página
via `document.write` -> o `<script>` executa no cliente.

## Lição (estrutural, não é "truque")
Um WAF de rede inspeciona **requisições**. Ataque 100% client-side (DOM XSS via
fragmento) **não trafega pelo servidor** -> o WAF é estruturalmente cego a ele.
Não existe REGRA de ModSecurity que feche isso, porque o payload nunca chega até ele.

## Correção correta (ver 03-*)
- **App-level (fix real):** o JS vulnerável usa `document.write` sobre input não
  confiável; correção = `textContent`/encoding de saída (não modificamos o DVWA por
  ser o alvo proposital, mas documentamos).
- **Defense-in-depth (WAF/proxy):** injetar header `Content-Security-Policy` na
  resposta, que bloqueia execução de script inline -> neutraliza o DOM XSS mesmo o
  WAF não "vendo" o payload.
