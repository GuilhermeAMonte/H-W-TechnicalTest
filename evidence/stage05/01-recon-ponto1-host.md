# Stage 05 — Recon Ponto 1: Host / Internet (sem VPN)

## Objetivo
Mapear o que um atacante externo (sem acesso à VPN) enxerga do laboratório.
VPN confirmada **desligada** (WireGuard client: Inativo) antes de escanear.

## TCP — top 1000 portas
```
$ nmap 127.0.0.1
PORT     STATE SERVICE
135/tcp  open  msrpc
445/tcp  open  microsoft-ds
1042/tcp open  afrog
1043/tcp open  boinc
```
Nenhuma porta pertence ao lab (135/445 = Windows nativo/SMB-RPC; 1042/1043 =
outro processo local do host, não relacionado). **Zero superfície TCP do lab exposta.**

## UDP — porta da VPN + sanity check (1-100)
```
$ nmap -sU -p 51820,1-100 --max-retries 1 --host-timeout 2m 127.0.0.1
PORT      STATE         SERVICE
51820/udp open|filtered unknown
```
`open|filtered` é o resultado ESPERADO para WireGuard: o protocolo nunca responde
a pacote UDP inválido/sem handshake válido, então o nmap não consegue confirmar
"open" por resposta direta (diferente de TCP, onde SYN-ACK confirma). Isso é uma
característica de design do WireGuard (superfície "silenciosa") — não um erro do scan.
As demais 100 portas UDP testadas vieram `closed`.

## Incidente durante o scan
Docker Desktop reiniciou nesse intervalo (containers do lab saíram com exit 255).
Primeira rodada de UDP scan (antes do restart) deu falso "all closed" — não havia
nada escutando, não era resultado de rede. Lab religado (`docker compose up -d`)
antes de repetir o teste. Lição de robustez: adicionar `restart: unless-stopped`
em todos os serviços (hoje só o `waf-route` tem) — item para hardening (Stage 8).

## Conclusão
Do ponto de vista externo, a superfície do lab se resume a **uma única porta UDP
ambígua** (51820, WireGuard). Nenhum serviço da DMZ/APP/DB é visível ou
identificável. A segmentação e o modelo VPN-gated cumprem o objetivo antes mesmo
de qualquer autenticação — não há o que enumerar de fora.
