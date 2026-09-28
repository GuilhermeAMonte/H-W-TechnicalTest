FROM python:3.12-slim

# iproute2: pra o entrypoint injetar a rota default via o gateway da APP.
RUN apt-get update && apt-get install -y --no-install-recommends iproute2 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir flask gunicorn psycopg2-binary

WORKDIR /app
COPY app.py .
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
