-- init.sql — seed do Postgres (roda automático no 1º boot).
-- Dados "sensíveis" FICTÍCIOS, alvo da exfiltração da cadeia de ataque (Stage 6).

CREATE TABLE customers (
    id          SERIAL PRIMARY KEY,
    name        TEXT NOT NULL,
    email       TEXT NOT NULL,
    credit_card TEXT NOT NULL,   -- fictício
    ssn         TEXT NOT NULL    -- fictício
);

INSERT INTO customers (name, email, credit_card, ssn) VALUES
 ('Alice Silva', 'alice@corp.local', '4111 1111 1111 1111', '123-45-6789'),
 ('Bruno Costa', 'bruno@corp.local', '5500 0000 0000 0004', '987-65-4321'),
 ('Carla Souza', 'carla@corp.local', '3400 0000 0000 009',  '456-78-9012');

-- Tabela de produtos (usada pelo endpoint LEGÍTIMO da app-api).
CREATE TABLE products (
    id    SERIAL PRIMARY KEY,
    name  TEXT NOT NULL,
    price NUMERIC(10,2) NOT NULL
);
INSERT INTO products (name, price) VALUES
 ('Firewall Appliance', 4999.90),
 ('VPN License',        199.00),
 ('WAF Subscription',   899.50);
