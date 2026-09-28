# 03 — Cadeia de Ataque & Mitigação por Elo

> O coração da avaliação. Cada elo: o que explora, evidência esperada, e a
> mitigação que o fecha (Parte 5). Vulns intencionais marcadas `VULN-INTENCIONAL`.

## Visão da kill chain

```
[0] Recon 3 pontos ─▶ [1] SQLi/XSS DVWA ─▶ [2] Upload inseguro = webshell
        (foothold DMZ) ─▶ [3] webshell curl app-api (DMZ→APP)
        ─▶ [4] endpoint sem-auth vaza cred Postgres ─▶ [5] exfil DB (APP→DB)
```

## Elos

### Elo 0 — Reconhecimento (Parte 2)
- **De 3 pontos**: host/internet, dentro da VPN, dentro da DMZ.
- `nmap` (hosts/portas/versões), `ffuf`/`gobuster` (dirs/endpoints), fingerprint.
- **Saída**: mapa da superfície — o que cada ponto enxerga e por quê.
- **Evidência**: `evidence/stage05/`.

### Elo 1 — SQLi + XSS no DVWA (Parte 3)
- ≥2 vulns reais. DVWA nível low/medium.
- SQLi no módulo SQL Injection; XSS refletido/armazenado.
- **Evidência**: request + resposta, dump via `sqlmap`/manual, print do XSS.
- **CVSS aprox.**: SQLi ~9.8 (crít.), XSS ~6.1 (médio).
- **Mitigação (P5)**: WAF `On` bloqueia (P4); prepared statements/encoding no app real.

### Elo 2 — Upload inseguro → webshell → foothold DMZ
- Módulo File Upload do DVWA aceita `.php` → webshell → RCE no container DVWA.
- **Evidência**: upload aceito, `id`/`uname` via webshell.
- **CVSS aprox.**: ~9.8 (RCE).
- **Mitigação (P5)**: validar MIME/extensão/magic bytes, store fora do webroot,
  WAF regra de upload; conter egress do container DMZ.

### Elo 3 — Movimento lateral DMZ→APP
- Do webshell na DMZ, `curl http://app-api:8000/...` — permitido pela regra **F1**.
- Prova que a segmentação **permite** só o caminho previsto (não DMZ→DB direto).
- **Evidência**: `curl` do webshell alcançando a API; e `curl` na DB **falhando**.
- **Mitigação (P5)**: cortar DMZ→APP só aos endpoints necessários; egress-filter.

### Elo 4 — Endpoint interno sem-auth vaza credencial  `VULN-INTENCIONAL`
- `app-api` expõe rota (ex.: `/internal/db-config` ou `/debug/env`) que retorna a
  cred do Postgres **sem autenticação**. Comentada no código como proposital.
- **Evidência**: resposta HTTP com user/senha/host do DB.
- **CVSS aprox.**: ~9.1 (exposição de credencial → acesso ao DB).
- **Mitigação (P5)**: exigir auth/mTLS interno, remover endpoint de debug, secrets
  fora do código, network policy APP↔DB restrita.

### Elo 5 — Exfiltração do DB (APP→DB)
- Com a cred, conectar no Postgres (regra **F2**) e extrair a tabela sensível.
- **Evidência**: `psql`/cliente puxando linhas sensíveis; pcap opcional.
- **CVSS aprox.**: ~9.1 (confidencialidade total do DB).
- **Mitigação (P5)**: least-privilege no DB (role read-only por app), egress-filter,
  cred rotacionada/secret manager, sem exposição da porta além do necessário.

## Tabela resumo elo → mitigação (Parte 5, antes/depois)

| Elo | Vuln | Mitigação principal | Prova de barrado |
|---|---|---|---|
| 1 | SQLi/XSS | WAF `On` + input handling | 403 + log WAF |
| 2 | Upload→RCE | validação upload + WAF | upload rejeitado |
| 3 | Lateral DMZ→APP | firewall p/ endpoints específicos | curl negado |
| 4 | Cred exposta | auth interno + remover debug | 401/404 no endpoint |
| 5 | Exfil DB | least-priv + egress-filter | conexão/egress negado |

## WAF: bloqueio → bypass → correção (Parte 4)
1. Vira `DetectionOnly`→`On`; captura request/403/log de SQLi e XSS.
2. Tenta evasão (encoding, ofuscação, comentários SQL, case) — relata o que passou.
3. Ajusta regra que fecha o bypass; prova request legítimo ainda passando (sem FP).

## Catálogo de vulns intencionais (rastreio)

| ID | Onde | Descrição | Removida em |
|---|---|---|---|
| VULN-1 | app-api | endpoint `/internal/db-config` sem-auth vaza cred DB | Parte 5 / Elo 3 |
| VULN-2 | dvwa | app deliberadamente vulnerável (SQLi/XSS/upload) | mitigado por WAF, não removido |
| VULN-3 | postgres | cred estática + role sem least-privilege (appuser superuser) | Parte 5 / Elo 5 |
| VULN-4 | app-api | `/internal/net-check` command injection (RCE na APP) — pivô p/ reusar a cred no DB | Parte 5 / Elo 5 |
