FROM python:3.12-slim

# iproute2: rota default via gateway da APP (entrypoint).
# iputils-ping: comando usado pelo endpoint de diagnóstico interno.
# postgresql-client: cliente psql (a app "guarda" a cred; um host de app real
#   costuma ter um cliente de DB instalado).
RUN apt-get update && apt-get install -y --no-install-recommends \
        iproute2 iputils-ping postgresql-client \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir flask gunicorn psycopg2-binary

WORKDIR /app
COPY app.py .
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
