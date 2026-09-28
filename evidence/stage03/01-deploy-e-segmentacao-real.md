# Stage 03 — Deploy dos serviços + segmentação com tráfego REAL

## Serviços no ar
```
$ docker compose ps
wg-gateway   Up      (roteador/firewall/VPN)
postgres     Up      (DB fechado, seedado)  + postgres-route (sidecar rota)
app-api      Up      (pivô lateral)
dvwa         Up      (alvo vulnerável)
```

## Roteamento pelo gateway (peça central)
Cada serviço em rede `internal` recebe rota default via o `.254` do seu segmento:
- app-api: `default via 172.30.20.254` (entrypoint próprio).
- postgres: `default via 172.30.30.254` (sidecar compartilhando o netns — imagem oficial não tem `ip`).
```
$ docker logs app-api | grep default
default via 172.30.20.254 dev eth0
$ docker logs postgres-route
[route] postgres default via 172.30.30.254
```

## F2 REAL — app-api -> postgres (query atravessa o firewall)
```
$ curl http://app-api:8000/api/products     (de dentro da app)
[{"id":1,"name":"Firewall Appliance",...}, ...]

# counter da regra F2 no gateway confirma que passou pela borda:
F2 (APP->DB:5432)  counter packets 1 accept
```

## F1 REAL + preview do pivô — DMZ -> app-api, puxando a cred sem auth
```
# de um host na DMZ (origem 172.30.10.x), atravessando o gateway:
$ curl http://172.30.20.10:8000/internal/db-config
{"db_host":"172.30.30.10","db_name":"labdb","db_password":"S3nh4_D0_Lab_2026",
 "db_port":5432,"db_user":"appuser"}

# counter F1 confirma o trânsito DMZ->APP:8000:
F1 (DMZ->APP:8000)  counter packets 1 accept
```
Isso é o elo do pivô (VULN-1): quem tem foothold na DMZ pega a cred do DB via app-api.

## F4 — DMZ -> DB negado (segmentação segura)
```
$ nc -zv -w3 172.30.30.10 5432
nc: connect to 172.30.30.10 port 5432 (tcp) timed out
```
DB só é alcançável pela APP (F2). Da DMZ, negado (default-deny).

## dvwa acessível intra-DMZ (ficará atrás do WAF na Stage 4)
```
$ curl -o /dev/null -w '%{http_code}' http://172.30.10.10/login.php   -> 200
```

## Conclusão
Segmentação comprovada com serviços reais: DMZ->APP e APP->DB permitidos só nas portas
certas; DMZ->DB negado. Pivô lateral (cred exposta) posicionado de propósito para a Stage 6.
Nenhum serviço exposto ao host (sem `ports`, exceto 51820/udp do WireGuard).
