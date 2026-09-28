FROM postgres:16

# iproute2: pro entrypoint injetar a rota default via o gateway do DB.
RUN apt-get update && apt-get install -y --no-install-recommends iproute2 \
    && rm -rf /var/lib/apt/lists/*

# Wrapper: adiciona a rota e depois chama o entrypoint ORIGINAL do postgres.
COPY route-entrypoint.sh /route-entrypoint.sh
RUN chmod +x /route-entrypoint.sh
ENTRYPOINT ["/route-entrypoint.sh"]
CMD ["postgres"]
