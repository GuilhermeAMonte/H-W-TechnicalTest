# Stage 05 — Recon Ponto 2: Dentro da VPN

## Objetivo
Mapear o que um usuário autenticado na VPN (mas sem foothold na DMZ) alcança do lab.
Túnel WireGuard ativo (`client.conf`, AllowedIPs inclui 172.30.10.0/24).

## Nota técnica: nmap + WireGuard no Windows
`nmap` (host discovery padrão) falha com `dnet: Failed to open device eth0` em
interfaces WinTun/WireGuard — bug conhecido do Npcap/Nmap 7.80 no Windows. Contorno:
sempre usar `-Pn` (pula o ping de descoberta via pacote bruto) ao escanear através
do túnel.

## Scan no WAF (172.30.10.5) — fast scan, top 100 portas
```
$ nmap -Pn -sT -F --max-retries 1 --host-timeout 30s 172.30.10.5
Not shown: 99 filtered ports
PORT     STATE SERVICE
8080/tcp open  http-proxy
```
Confirma a regra F-VPN: só a porta do WAF está acessível. As demais 99 portas
testadas ficaram `filtered` — o firewall (`policy drop`) descarta em silêncio,
sem resposta (diferente de "closed", que exigiria RST/ICMP).

## Scan no DVWA direto (172.30.10.10) — tentando pular o WAF
```
$ nmap -Pn -sT -p 80 --max-retries 1 --host-timeout 30s 172.30.10.10
PORT   STATE    SERVICE
80/tcp filtered http
```
**Confirmado:** mesmo dentro da VPN (rede autorizada pela F-VPN), o DVWA **não** é
alcançável diretamente. Não existe regra `VPN -> DVWA`, só `VPN -> WAF`. O WAF é o
único caminho de entrada — exatamente o desenho pretendido (WAF na frente de tudo).

## Conclusão
Do ponto de vista de um usuário VPN: superfície = **uma única porta HTTP no WAF**
(8080). Nenhum outro serviço do lab (DVWA direto, app-api, postgres) é alcançável
a partir daqui. Para ir além, é necessário comprometer o próprio WAF/DVWA e obter
execução de comando **dentro** da rede DMZ — não basta estar "na VPN".
