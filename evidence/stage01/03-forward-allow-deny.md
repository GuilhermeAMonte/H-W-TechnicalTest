# Stage 01 — FORWARD: liberação F1 e prova de bloqueio (F4)

## Achado: a camada de firewall do Docker fica NA FRENTE do nosso gateway

Ao testar DMZ→APP, o pacote dava timeout e os counters do nosso nftables ficavam
em ZERO — o pacote nem chegava no FORWARD do gateway. Diagnóstico com tcpdump:

- No **cliente** (DMZ): o SYN é transmitido (3 retransmissões), sem resposta.
- No **gateway**: só o ARP chega; o SYN **não**.

Conclusão: o firewall do próprio Docker (cadeia `FORWARD` + isolação entre redes,
agravado por `internal: true`) descarta o tráfego cujo destino está fora da subnet
de origem — ANTES de entregar ao wg-gateway.

Detalhe: a primeira tentativa de inserir a regra falhou com
`iptables: No chain/target/match by that name`, porque a imagem usa `iptables-nft`
mas o Docker Desktop cria as regras no `iptables-legacy` (backends diferentes;
o nft não enxerga a cadeia legacy).

## Correção reproduzível

`DOCKER-USER` (avaliado pelo Docker antes da isolação dele) recebe um ACCEPT só pro
range do lab. Automatizado no `make up` pelo serviço one-shot `netfix`
(`gateway/docker-user-fix.sh`, detecta o backend):

```
$ docker logs netfix
[docker-user-fix] regra garantida via iptables-legacy (lab 172.30.0.0/16)

$ iptables-legacy -S DOCKER-USER
-N DOCKER-USER
-A DOCKER-USER -s 172.30.0.0/16 -d 172.30.0.0/16 -j ACCEPT
-A DOCKER-USER -j RETURN
```

O Docker só para de derrubar; o filtro fino continua no nftables do gateway.
Não há bypass: redes diferentes não têm caminho L2 direto — só transitam pelo gateway.

## Prova (após `docker compose up -d --build`, sem passo manual)

```
# F1 — DMZ -> APP:8000 (permitido)
$ nc -zv -w3 172.30.20.10 8000
Connection to 172.30.20.10 8000 port [tcp/*] succeeded!

# F4 — DMZ -> DB:5432 (negado pelo default-deny; NÃO existe regra p/ esse caminho)
$ nc -zv -w3 172.30.30.10 5432
nc: connect to 172.30.30.10 port 5432 (tcp) timed out: Operation now in progress
```

Counters do `chain forward` confirmam QUEM decidiu:
```
ct state established,related  counter packets 5 ... accept
F1 (DMZ->APP:8000)            counter packets 1 ... accept   <- nossa regra liberou
F2 (APP->DB:5432)             counter packets 0 ... accept
forward default-drop          counter packets 3 ... drop     <- os 3 SYN do F4 barrados
```

**Conclusão:** a segmentação é aplicada pelo nftables do wg-gateway (default-deny +
F1/F2 explícitas). O timeout (não "refused") é a assinatura do pacote descartado pelo
firewall. Mapeamento pra nuvem: a camada de rede do provedor (SG/NACL) precisa permitir
o trânsito até o appliance; o appliance aplica a política fina.
