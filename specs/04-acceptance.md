# 04 — Critérios de Aceite (testável por stage)

> Cada stage só "fecha" quando os checks passam e a evidência está salva.
> Formato: comando/ação → resultado esperado → onde grava a prova.

## Stage 0 — Scaffold
- [ ] Árvore do repo criada (specs, gateway, waf, targets, scripts, evidence).
- [ ] `make help` lista alvos; `make up`/`down` existem (casca).
- [ ] `.gitignore` ignora chaves/segredos.
- [ ] 6 specs presentes e coerentes com CLAUDE.md + PDF.

## Stage 1 — Segmentação + firewall default-deny
- [ ] 3 redes docker isoladas (`lab_dmz/app/db`, internal).
- [ ] `wg-gateway` sobe com `NET_ADMIN` e `ip_forward=1` (`sysctl` confirma).
- [ ] nftables policy `drop` em INPUT e FORWARD (`nft list ruleset`).
- [ ] **F1**: `waf → app-api:8000` responde. Prova em `evidence/stage01/`.
- [ ] **F2**: `app-api → postgres:5432` conecta.
- [ ] **F4**: `waf → postgres:5432` **recusado/timeout**. ← print-chave.
- [ ] **F5**: host → app-api/postgres **recusado**.
- [ ] Cada regra ALLOW tem comentário no `.nft`.

## Stage 2 — WireGuard + admin só via VPN
- [ ] `wg show` mostra o peer com handshake.
- [ ] `ping`/rota do peer alcança o gateway pela sub-rede VPN.
- [ ] **I3**: SSH ao gateway **sem** túnel → negado (prova).
- [ ] **I2**: SSH **com** túnel → OK (prova). Ambas em `evidence/stage02/`.
- [ ] Chave privada NÃO versionada (confere `.gitignore`).

## Stage 3 — Deploy dos serviços
- [ ] `make up` sobe dvwa + app-api + postgres respeitando o firewall.
- [ ] DVWA acessível **via WAF** (não direto).
- [ ] app-api tem endpoint sem-auth marcado `VULN-INTENCIONAL` que vaza cred.
- [ ] Postgres com tabela + dado sensível (seed).
- [ ] Re-verifica F1/F2/F4 com os serviços reais no ar. `evidence/stage03/`.

## Stage 4 — WAF em DetectionOnly
- [ ] Nginx+ModSec+CRS na frente do DVWA.
- [ ] Modo `DetectionOnly` confirmado na config.
- [ ] SQLi trivial **passa** mas **aparece no audit log**. `evidence/stage04/`.
- [ ] Sei ler uma detecção no log (rule id, msg).

## Stage 5 — Recon (Parte 2)
- [ ] `nmap` dos 3 pontos (host, VPN, DMZ) salvo.
- [ ] `ffuf`/`gobuster` no alvo web.
- [ ] Mapa da superfície escrito (o que cada ponto vê + por quê). `evidence/stage05/`.

## Stage 6 — Cadeia de ataque (Parte 3)
- [ ] ≥2 vulns exploradas no DVWA (evidência de cada).
- [ ] Webshell → RCE na DMZ.
- [ ] Lateral: webshell → app-api (F1); DMZ→DB direto falha.
- [ ] Cred obtida do endpoint sem-auth.
- [ ] Exfil do Postgres (F2).
- [ ] Relatório pentest: reprodução/evidência/impacto/CVSS por achado. `evidence/stage06/`.

## Stage 7 — WAF blocking (Parte 4)
- [ ] WAF `On`: SQLi e XSS → **403** + log (request+resp+log salvos).
- [ ] ≥1 tentativa de bypass documentada (passou ou não).
- [ ] Regra corrigida p/ o bypass; request legítimo ainda passa (sem FP). `evidence/stage07/`.

## Stage 8 — Contenção & Hardening (Parte 5)
- [ ] Cada elo da cadeia: mitigação aplicada + mesma tentativa **barrada** (antes/depois).
- [ ] Superfície reduzida (portas/serviços/cred/egress).
- [ ] Segmentação reforçada contra o lateral que funcionou. `evidence/stage08/`.

## Stage 9 — Mapeamento de portas (Parte 6)
- [ ] `nmap` antes/depois de ≥2 pontos.
- [ ] Tabela: host, porta, protocolo, quem acessa, justificativa.
- [ ] Caminho que deveria ser bloqueado, bloqueado (DMZ→DB). `evidence/stage09/`.

## Stage 10 — README + bônus
- [ ] README com todas as seções obrigatórias do case.
- [ ] `make up` reproduz o lab do zero.
- [ ] Bônus priorizados por custo/impacto (o que der tempo).

## Definição de "pronto" global (o que a banca vê)
- Um comando sobe tudo. Evidência em `/evidence`. README completo.
- Ciclo atacar→entender→conter comprovado elo a elo.
