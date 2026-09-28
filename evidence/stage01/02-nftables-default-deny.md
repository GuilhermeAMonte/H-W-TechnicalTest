# Stage 01 — nftables default-deny (evidência)

## Ruleset carregado no gateway
```
$ docker exec wg-gateway sh -c "nft -f /etc/nftables/ruleset.nft && nft list ruleset"
table inet filter {
        chain input {
                type filter hook input priority filter; policy drop;
                ct state established,related accept comment "respostas de conexões já abertas"
                ct state invalid drop comment "pacote fora de estado"
                iif "lo" accept comment "loopback local"
                limit rate 5/minute log prefix "nft-input-drop: " comment "amostra do que caiu no INPUT"
        }
        chain forward {
                type filter hook forward priority filter; policy drop;
                ct state established,related accept comment "sentido de volta do fluxo já liberado"
                ct state invalid drop
                limit rate 5/minute log prefix "nft-forward-drop: " comment "prova de caminho negado"
        }
        chain output {
                type filter hook output priority filter; policy accept;
        }
}
```

**Conclusão:** default-deny ativo em INPUT e FORWARD. Nenhuma liberação inter-segmento
ainda → todo tráfego que atravessa o gateway é negado. Liberações F1/F2 no próximo passo.
