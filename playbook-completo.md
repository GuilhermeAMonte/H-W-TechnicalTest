# PLAYBOOK — Prompts para o Claude Code (Stage 0 → 10)

> Como usar: cole o `CLAUDE.md` na raiz do repo primeiro. Depois cole cada bloco abaixo
> no Claude Code **na ordem, um por vez**. Não cole o próximo antes de fechar o anterior.
> Infra (2,3,4,9) = MODO PROFESSOR: ele explica, você roda, cola a saída, ele segue.
> Ofensivo (5,6,7,8) = você pilota, ele revisa. Os blocos ofensivos são TEMPLATES —
> adapte os payloads ao que o seu lab realmente expuser.

---

## ▶ STAGE 0 + 1 — Scaffold + Segmentação/Firewall

Leia o `CLAUDE.md` na raiz inteiro antes de responder. É o contrato do projeto.
Nas stages de infra você está em **MODO PROFESSOR**: um comando por vez, explica o que faz
e o impacto, e **espera eu rodar e colar a saída** antes de seguir. Não me entregue arquivos
prontos de uma vez — preciso aprender infra de rede fazendo. Vamos só Stage 0 e 1 nesta sessão.

**Stage 0 — Scaffold:** proponha a árvore do repo (compose, wireguard/, firewall/, waf/, targets/,
evidence/, scripts/, README), um `Makefile` com `make up`/`make down` (casca vazia), `.gitignore`
e `README.md` esqueleto com as seções que o case exige. Mostre a árvore antes de criar.

**Stage 1 — Segmentação + firewall default-deny (devagar):** 3 redes docker isoladas
(DMZ 172.30.10.0/24, APP 172.30.20.0/24, DB 172.30.30.0/24) + container `wg-gateway` roteando
com nftables em default-deny no FORWARD, liberando só DMZ→APP (porta da app) e APP→DB (5432).
Me ensine em blocos curtos, esperando minha saída a cada um:
1. Redes docker isoladas: por que não bastam sozinhas e por que preciso de um container-roteador.
2. O gateway: por que `NET_ADMIN` e `ip_forward=1`.
3. nftables base: table/chain/hook, policy `drop` no FORWARD, papel do `conntrack`.
4. Liberações DMZ→APP e APP→DB, uma por vez, provando o bloqueio entre cada uma.
A cada bloco: comando → o que faz → impacto → como verifico → você para. Salve as provas de
"caminho negado sendo negado" em `/evidence/stage01/`. Não avance pra Stage 2.

---

## ▶ STAGE 2 — WireGuard + acesso admin só via VPN (MODO PROFESSOR)

Continuamos. **MODO PROFESSOR**, um passo por vez, esperando minha saída.
Objetivo: subir WireGuard no `wg-gateway` com 1 peer (meu cliente), e fazer com que acesso
administrativo (SSH/painel) aos hosts só funcione vindo da VPN — negado sem, permitido com.
Me ensine em blocos:
1. Conceito: par de chaves pública/privada, o que `AllowedIPs` significa de cada lado, por que
   WireGuard é "roteamento", não "conexão".
2. Gere as chaves (servidor + peer) e me explique onde cada uma vai. Um comando por vez.
3. Config do servidor (`wg0.conf`) e do peer — trecho por vez, explicando cada linha.
4. Suba com `wg-quick`, me faça inspecionar com `wg show`.
5. Regra de firewall: SSH/gestão só a partir da sub-rede da VPN. Depois eu provo os dois casos:
   SSH negado sem túnel, SSH ok com túnel. Salve as duas evidências em `/evidence/stage02/`.
Não avance pra Stage 3.

---

## ▶ STAGE 3 — Deploy dos serviços respeitando o firewall (MODO PROFESSOR, mais leve)

Continuamos. Modo professor, mas pode agrupar um pouco mais — ainda explicando cada serviço.
Subir dentro dos segmentos, respeitando as regras já criadas:
1. **DVWA** na DMZ (alvo vulnerável). Explique como fica atrás do WAF depois.
2. **`app-api`** na APP: uma API interna mínima (Flask/Node) que guarda a credencial do Postgres
   e tem um endpoint interno **sem autenticação** que vaza essa credencial — esse é o meu pivô
   lateral de propósito. Deixe isso explícito e comentado no código.
3. **Postgres** na DB, fechado, com uma tabela e dados "sensíveis" pra eu exfiltrar depois.
Ao fim, me faça verificar que o roteamento respeita o firewall: DMZ alcança WAF; APP só é
alcançável da DMZ; DB só da APP. Salve as verificações em `/evidence/stage03/`.
Confirme que `make up` sobe o lab inteiro com um comando. Não avance pra Stage 4.

---

## ▶ STAGE 4 — WAF na frente em DetectionOnly (MODO PROFESSOR)

Continuamos. Modo professor.
Coloque Nginx + ModSecurity + OWASP CRS na frente do DVWA, mas em modo **DetectionOnly**
(detecta e loga, NÃO bloqueia ainda) — porque preciso que meus ataques da Stage 6 passem primeiro.
Me ensine:
1. O que é o OWASP CRS, o que é "paranoia level", diferença entre `DetectionOnly` e `On`.
2. Config do ModSecurity + inclusão do CRS — trecho por vez.
3. Onde ficam os logs de auditoria e como eu leio uma detecção.
Me faça mandar um SQLi trivial e confirmar que ele **passa** mas **aparece no log**.
Salve a evidência em `/evidence/stage04/`. Não avance pra Stage 5.

---

## ▶ STAGE 5 — Recon & Enumeração de 3 pontos (EU PILOTO, você revisa)

A partir daqui você é **COPILOTO**: eu proponho os comandos, você corrige/sugere alternativa,
não executa por mim. Reforce a disciplina de evidência.
Vou fazer recon de 3 pontos de vista: (a) host/internet, (b) de dentro da VPN, (c) de dentro da DMZ.
Para cada ponto: descoberta de hosts, portas, serviços e versões (`nmap`), e no alvo web
fingerprint + descoberta de diretórios/endpoints (`ffuf`/`gobuster`) e parâmetros interessantes.
Seu papel nesta stage:
- Revisar minhas flags de nmap e sugerir o que falta pra cada ponto de vista.
- Me ajudar a montar o **mapa da superfície de ataque**: o que está exposto de cada ponto e por quê.
Vou salvando tudo em `/evidence/stage05/`. Comece me perguntando qual ponto ataco primeiro e
revisando meu primeiro comando.

---

## ▶ STAGE 6 — Cadeia de ataque + relatório de pentest (EU PILOTO)

Copiloto. Eu conduzo a exploração; você revisa payload, explica impacto/CVSS e cuida do formato
do relatório. Cadeia de ponta a ponta que quero montar e comprovar:
1. Explorar ≥2 vulns reais no DVWA (SQLi, XSS, e/ou upload inseguro/path traversal).
2. **Foothold na DMZ**: upload inseguro → webshell → execução de comando.
3. **Lateral**: do webshell, `curl` na `app-api` (regra DMZ→APP) e puxar a credencial do endpoint sem auth.
4. Com a cred, alcançar o Postgres (regra APP→DB) e **exfiltrar** os dados sensíveis.
Para cada achado, me ajude a produzir a entrada do relatório estilo pentest:
passos de reprodução, evidência (comando + saída/print), impacto, severidade (CVSS aprox.).
Comece me pedindo minha primeira vuln e revisando meu payload. Evidências em `/evidence/stage06/`.

---

## ▶ STAGE 7 — WAF em blocking: 403 + bypass + fix (EU PILOTO)

Copiloto. Agora vire o WAF de `DetectionOnly` para **On** (blocking).
1. Prove que ele passa a bloquear os ataques da Stage 6 — no mínimo SQLi e XSS: me ajude a capturar
   o request, a resposta **403** e o **log** do WAF pra cada um.
2. Eu vou tentar **burlar meu próprio WAF** (encoding, ofuscação, técnicas de evasão). Seu papel:
   sugerir vetores de evasão pra eu testar e me ajudar a relatar o que ainda passou.
3. Para o bypass que funcionar: me ajude a ajustar a regra que fecha a brecha, e depois provo que
   um **request legítimo continua passando** (sem falso-positivo).
Evidências (request, 403, log, bypass, regra corrigida) em `/evidence/stage07/`.

---

## ▶ STAGE 8 — Contenção & Hardening por elo (EU PILOTO, você guia mitigação)

Copiloto, mas aqui puxe mais a mitigação de infra (é onde eu aprendo menos sozinho).
Para **cada elo** da cadeia da Stage 6, aplicar a mitigação e provar a mesma tentativa agora barrada:
1. Elo por elo: segmentação, regra de firewall, patch ou config. Antes/depois de cada um.
2. Reduzir superfície: portas, serviços, credenciais e tráfego de **saída** desnecessários.
3. Reforçar a segmentação pra conter o movimento lateral que funcionou (ex.: cortar DMZ→APP a
   endpoints específicos, egress-filtering na APP/DB).
Me explique cada mitigação de rede antes de aplicar. Evidências antes/depois em `/evidence/stage08/`.

---

## ▶ STAGE 9 — Mapeamento de portas / evidência final (MODO PROFESSOR)

Modo professor pra eu interpretar os resultados.
1. `nmap` **antes/depois** do hardening, a partir de pelo menos 2 pontos (ex.: internet e VPN).
2. Monte comigo a **tabela de mapeamento de portas**: host, porta, protocolo, quem pode acessar,
   justificativa.
3. Prove um caminho que **deveria** ser bloqueado sendo bloqueado (ex.: DMZ→DB recusado) — me faça
   rodar e ler a saída que confirma a recusa.
Evidências em `/evidence/stage09/`.

---

## ▶ STAGE 10 — README + Bônus

Copiloto. Fechar o entregável.
1. **README** completo: diagrama da topologia + explicação da segmentação; mapa da superfície (S5);
   relatório de pentest (S6); WAF bloqueio/bypass/correção (S7); hardening antes/depois (S8);
   tabela de portas (S9); como rodar localmente e reproduzir ataques/bloqueios/contenção;
   trade-offs, limitações e como eu escalaria pra infra real.
2. **Bônus** (escolher o que der tempo, em ordem de impacto):
   - Suricata/Zeek detectando minha própria cadeia de ataque durante a S6.
   - Script único que automatiza a cadeia de ponta a ponta.
   - Escalada de privilégio no host comprometido.
   - fail2ban/rate-limiting na borda; logs centralizados com alerta; IaC (Terraform/Ansible).
   - Mapa da kill chain versionado.
   - Discussão do mapeamento pra nuvem: Security Groups/NACL (AWS), Cloudflare na borda,
     Proxmox na virtualização.
Me ajude a priorizar os bônus pelo custo/impacto dado o tempo restante.
