# Stage 02 — WireGuard server + SSH admin só via VPN

## Servidor WireGuard no ar (wg-gateway, no boot)
```
$ docker exec wg-gateway wg show
interface: wg0
  public key: SFXf1wunqZ7iL+45iqy2EK2JxqbxKZLHUv4ais/A/HU=
  private key: (hidden)
  listening port: 51820

peer: MJVeP5Yp+vs/2OI6A0sTpyBeUVAvDvY3xyTj9Zv85is=
  allowed ips: 10.13.13.2/32
```
- wg0 escutando 51820/udp; peer (notebook) registrado com AllowedIPs 10.13.13.2/32.
- Config renderizada no boot a partir do template + chaves (`.key` fora do git).

## Regras de firewall relevantes (chain input)
```
udp dport 51820 accept                       # I1: entrada do WireGuard
ip saddr 10.13.13.0/24 tcp dport 22 accept   # I2: SSH só da sub-rede VPN
ip saddr 10.13.13.0/24 icmp echo-request accept  # ping admin via VPN
# I3 (implícito): qualquer outra origem em :22 cai no policy drop = negado
```

## PROVA — SSH ao gateway SEM VPN é negado (origem fora de 10.13.13.0/24)
A partir de um host na DMZ (origem 172.30.10.x), tentando o SSH do gateway:
```
$ nc -zv -w3 172.30.10.254 22
nc: connect to 172.30.10.254 port 22 (tcp) timed out: Operation now in progress
```
Timeout (não "refused") = o pacote bateu no INPUT, não casou I2 (origem errada) e
caiu no default-deny. sshd está no ar (escuta :22), mas o firewall só deixa passar
origem da VPN. **SSH negado sem VPN, comprovado.**

## Correção: interface de borda (edge)

O gateway só estava em redes `internal: true` → o Docker não entrega porta publicada
(51820/udp) a container sem interface externa. tcpdump no gateway = 0 pacotes.
Adicionada a rede `lab_edge` (não-internal, 172.31.0.0/24, gateway 172.31.0.2) como a
interface "internet-facing". Os 3 segmentos seguem internal. Após isso:

```
$ docker exec wg-gateway wg show
peer: MJVeP5Yp+vs/2OI6A0sTpyBeUVAvDvY3xyTj9Zv85is=
  endpoint: 172.31.0.1:54992
  allowed ips: 10.13.13.2/32
  latest handshake: 9 seconds ago
  transfer: 180 B received, 92 B sent
```

## PROVA — SSH/ICMP COM VPN (cliente Windows real)

Túnel ligado (WireGuard app: handshake ok, bytes recebidos > 0):
```
> ping 10.13.13.1
Resposta de 10.13.13.1: bytes=32 tempo=4ms TTL=64   (4/4, 0% perda)

> ssh -o ConnectTimeout=5 root@10.13.13.1
The authenticity of host '10.13.13.1' can't be established.
ED25519 key fingerprint is SHA256:e7T+DtVZE39bxLuEYFLklG/u6VIa40Qs4MVFaJaIqL8.
Are you sure you want to continue connecting? yes
root@10.13.13.1's password:            <- ALCANÇOU o sshd = permitido via VPN
```

## Conclusão (antes/depois)
| | Sem VPN | Com VPN |
|---|---|---|
| ping 10.13.13.1 | timeout (100% perda) | 4/4 respostas |
| ssh root@10.13.13.1 | Connection timed out | chega no prompt de senha |

Admin (SSH) **negado sem túnel, permitido com túnel** — regra I2 (`ip saddr 10.13.13.0/24
tcp dport 22 accept`). Com o túnel, os pacotes do cliente carregam origem 10.13.13.2,
que casa I2; sem túnel, não há sequer rota até 10.13.13.1.

## DIFERENCIAL — login admin SÓ por chave (sem senha)

sshd endurecido (`gateway/ssh/sshd_hardening.conf`): `PasswordAuthentication no`,
`PermitRootLogin prohibit-password`. Chave autorizada instalada no boot pelo entrypoint.
```
$ sshd -T | grep -E 'passwordauthentication|permitrootlogin|pubkeyauthentication'
permitrootlogin without-password
pubkeyauthentication yes
passwordauthentication no
```
Login real via VPN, com a chave do admin:
```
> ssh -i gateway/ssh/admin_ed25519 root@10.13.13.1
Linux wg-gateway 6.18.x-microsoft-standard-WSL2 ...
root@wg-gateway:~# hostname
wg-gateway
```
Sem túnel: timeout (I2/default-deny). Com túnel + chave: login direto, zero senha.
Camadas: rede (só via VPN) + autenticação (só por chave) = defesa em profundidade.


