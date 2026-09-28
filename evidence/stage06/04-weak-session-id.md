# Stage 06 — Achado: Weak Session ID (identificador previsível)

## Módulo
DVWA `vulnerabilities/weak_id/` (nível low).

## Reprodução
16 cliques consecutivos em "Generate" retornaram a sequência exata:
```
1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16
```
Confirma geração via **contador global incremental** (+1 por chamada), sem
componente aleatório ou vinculação a usuário/sessão específica.

## Impacto
Se esse mecanismo fosse usado para tokens de sessão, reset de senha ou qualquer
identificador de acesso, um atacante que gerar o **próprio** ID pode **prever**
IDs vizinhos (N-1, N+1, ...) — muito provavelmente pertencentes a outros usuários
ativos — e sequestrar sessão/recurso sem roubar credencial nenhuma.
Classe de vulnerabilidade: **CWE-330 (Uso de valores insuficientemente
aleatórios)** / **CWE-340 (Previsibilidade)**.

## CVSS aprox.
**7.5 (Alto)** — AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (facilmente explorável,
alta confidencialidade comprometida se aplicado a sessão real; sem PoC de
sequestro de sessão de terceiro neste teste, pois o módulo é isolado/demonstrativo).

## Mitigação recomendada (referência para README/Stage 8)
IDs de sessão/token devem usar gerador criptograficamente seguro (CSPRNG),
nunca contador ou timestamp puro.
