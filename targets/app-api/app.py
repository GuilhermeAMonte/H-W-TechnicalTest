"""
app-api — API interna (pivô lateral do lab).

Segura por padrão: queries PARAMETRIZADAS (nunca concatena input em SQL),
validação de tipo na rota, erros genéricos (sem stack trace ao cliente).

EXCEÇÃO PROPOSITAL: /internal/db-config vaza a credencial do banco SEM auth —
é o elo do pivô lateral que o teste exige (VULN-1). Ver specs/03-attack-chain.md.
"""
import os
import re
import subprocess
from flask import Flask, jsonify, abort, request
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

# HARDENED=1 (Stage 8) fecha as vulns intencionais. Default 0 = estado da Stage 6.
HARDENED = os.environ.get("HARDENED", "0") == "1"

# Credenciais do banco vêm do ambiente (a app "guarda" a cred do DB).
DB = dict(
    host=os.environ["DB_HOST"],
    port=int(os.environ.get("DB_PORT", "5432")),
    user=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
    dbname=os.environ["DB_NAME"],
)


def get_conn():
    return psycopg2.connect(**DB, connect_timeout=5)


@app.get("/")
def health():
    return jsonify(status="ok", service="app-api")


@app.get("/api/products")
def products():
    # Query parametrizada, sem concatenar input (appsec INPUT-006).
    with get_conn() as c, c.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT id, name, price FROM products ORDER BY id;")
        return jsonify(cur.fetchall())


@app.get("/api/products/<int:pid>")
def product(pid):
    # <int:pid> valida o tipo na rota (INPUT-003); query parametrizada (INPUT-006).
    with get_conn() as c, c.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT id, name, price FROM products WHERE id = %s;", (pid,))
        row = cur.fetchone()
        if row is None:
            abort(404)
        return jsonify(row)


# ============================================================================
# VULN-INTENCIONAL (VULN-1) — pivô lateral do case.
# Endpoint interno SEM AUTENTICAÇÃO que devolve a credencial do Postgres.
# NÃO é descuido: é o objeto do teste (Stage 6). O atacante, já com foothold
# na DMZ, faz curl aqui (regra F1 DMZ->APP) e pega a cred pra alcançar o DB.
# Mitigação (exigir auth / remover endpoint de debug / secrets manager): Stage 8.
# ============================================================================
@app.get("/internal/db-config")
def db_config():
    if HARDENED:
        # Stage 8: endpoint de debug REMOVIDO (reduz superfície). Não vaza cred.
        abort(404)
    return jsonify(
        db_host=DB["host"],
        db_port=DB["port"],
        db_name=DB["dbname"],
        db_user=DB["user"],
        db_password=DB["password"],
    )


# ============================================================================
# VULN-INTENCIONAL (VULN-4) — Command Injection num "diagnóstico de rede" interno.
# Endpoint sem auth (ferramenta interna) que roda um ping com o host informado,
# CONCATENANDO o input direto no shell. É o elo que dá EXECUÇÃO DE COMANDO na
# camada APP: o atacante com foothold na DMZ chama este endpoint (via F1), ganha
# shell na app-api e, DA APP, usa a credencial roubada com o cliente psql para
# alcançar o Postgres (via F2) e exfiltrar. Mitigação (validar/parametrizar,
# remover exec de shell): Stage 8.
# ============================================================================
@app.get("/internal/net-check")
def net_check():
    host = request.args.get("host", "127.0.0.1")
    if HARDENED:
        # Stage 8: allowlist estrita (só IP/hostname válido, sem metacaracteres de
        # shell) + subprocess SEM shell (lista de args). Fecha o command injection.
        if not re.fullmatch(r"[A-Za-z0-9._-]{1,253}", host):
            abort(400)
        out = subprocess.run(["ping", "-c", "1", "-W", "1", host],
                             capture_output=True, text=True, timeout=5).stdout
        return jsonify(output=out)
    # Estado Stage 6 (vulnerável): concatena no shell.
    out = os.popen("ping -c 1 -W 1 " + host).read()
    return jsonify(cmd="ping -c 1 -W 1 " + host, output=out)


@app.errorhandler(500)
def internal_error(_e):
    # Erro genérico ao cliente, sem stack trace (appsec INPUT-017).
    return jsonify(error="internal error"), 500
