"""
app-api — API interna (pivô lateral do lab).

Segura por padrão: queries PARAMETRIZADAS (nunca concatena input em SQL),
validação de tipo na rota, erros genéricos (sem stack trace ao cliente).

EXCEÇÃO PROPOSITAL: /internal/db-config vaza a credencial do banco SEM auth —
é o elo do pivô lateral que o teste exige (VULN-1). Ver specs/03-attack-chain.md.
"""
import os
from flask import Flask, jsonify, abort
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

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
    return jsonify(
        db_host=DB["host"],
        db_port=DB["port"],
        db_name=DB["dbname"],
        db_user=DB["user"],
        db_password=DB["password"],
    )


@app.errorhandler(500)
def internal_error(_e):
    # Erro genérico ao cliente, sem stack trace (appsec INPUT-017).
    return jsonify(error="internal error"), 500
