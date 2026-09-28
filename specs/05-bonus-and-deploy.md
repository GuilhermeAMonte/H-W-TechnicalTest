# 05 — Bônus & Deploy Explorável

> Bônus do case, priorizados por custo/impacto (prazo 4–5 dias), e o plano de
> deploy pra entregar um site explorável à banca sem abrir RCE na internet crua.

## Bônus — priorização

| # | Bônus | Impacto | Custo | Quando | Nota |
|---|---|---|---|---|---|
| 1 | **IDS Suricata/Zeek** detectando a própria cadeia (Parte 3) | Alto | Médio | pós-Stage 6 | Sniffa a rede DMZ/gateway; alerta bate com a kill chain. Prova blue forte. |
| 2 | **Script único** automatiza a cadeia ponta a ponta | Alto | Baixo | pós-Stage 6 | `scripts/attack-chain.sh` reproduz recon→exfil. Reprodutibilidade = nota. |
| 3 | **Mapa da kill chain versionado** | Médio | Baixo | Stage 10 | Diagrama MITRE-ish em `specs/diagrams/`. |
| 4 | **Mapeamento pra nuvem real** | Médio | Baixo | Stage 10 | AWS SG/NACL, Cloudflare borda, Proxmox. Já esboçado em `01`. |
| 5 | **fail2ban / rate-limiting** na borda | Médio | Baixo | Stage 8 | No gateway/WAF; casa com hardening. |
| 6 | **Logs centralizados + alerta** | Médio | Médio | Stage 8/10 | Agrega WAF+nft+suricata; alerta simples. |
| 7 | **Escalada de privilégio** no host comprometido | Médio | Médio | pós-Stage 6 | Do container DVWA; documenta caminho. |
| 8 | **IaC (Terraform/Ansible)** | Baixo* | Alto | se sobrar | *Alto pra "escala real", mas caro no prazo. Documentar como "faria". |

Linha de corte provável no prazo: **1, 2, 3, 4, 5**. O resto vira seção "como eu
faria" no README (ainda pontua em maturidade).

## Deploy explorável — objetivo e risco

**Objetivo**: banca acessa o alvo e explora, sem clonar o repo.

**Risco central**: DVWA = SQLi/XSS/**upload→webshell→RCE**. Exposto na internet
crua, é comprometido por bots em horas e o host vira trampolim. Portanto: **nunca**
expor DVWA/DB/webshell diretamente. Só a entrada controlada fica pública.

**Restrições operacionais**:
- Não criar conta de hosting nem inserir credencial do candidato (VPS/DNS = candidato pilota).
- Publicar serviço vulnerável é ação outward-facing → confirmar antes de ligar.
- Derrubar (`make down`) ao fim da janela de avaliação.

## Opções de deploy

### A) VPN-gated (DECIDIDO ✓ — reusa o WireGuard da Stage 2)
- Público: só `51820/udp` (WireGuard). Todo o resto fechado pelo nftables.
- Banca recebe peer config → sobe túnel → explora DVWA via WAF de dentro.
- **Prós**: casa com "admin só via VPN"; prova a segmentação; zero RCE aberto.
- **Contras**: banca precisa subir o túnel (doc no README resolve).

### B) Túnel efêmero (Cloudflare Tunnel / ngrok)
- Expõe só o WAF via túnel, com **basic-auth + IP allowlist**, ligado na janela.
- **Prós**: link clicável, sem VPS. **Contras**: some ao desligar; auth extra.

### C) VPS gated (Contabo/OVH/Proxmox)
- Lab inteiro num VPS; firewall público só WireGuard + WAF (com allowlist).
- **Prós**: vira demo do bônus "nuvem real". **Contras**: custo, superfície, o candidato provisiona.

## Critério de aceite (deploy)
- [ ] Nenhum serviço vulnerável acessível sem gate (VPN/auth/allowlist).
- [ ] DB e webshell **nunca** públicos (confirma com `nmap` externo).
- [ ] README com passo-a-passo de acesso da banca.
- [ ] Procedimento de teardown documentado.
