-- ─────────────────────────────────────────────────────────────────────────────
-- Eight Sistemas — Estrutura de referência (SQLite)
-- O banco projeto.db é criado AUTOMATICAMENTE ao rodar python app.py
-- Este arquivo é apenas para consulta da estrutura das tabelas.
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS usuario (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    nome  VARCHAR(50)  NOT NULL,
    email VARCHAR(50)  UNIQUE,
    senha VARCHAR(100) NOT NULL,
    tipo  VARCHAR(10)  DEFAULT 'vendedor'  -- 'admin' ou 'vendedor'
);

CREATE TABLE IF NOT EXISTS fornecedores (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nome        VARCHAR(100) NOT NULL,
    contato     VARCHAR(50),
    email       VARCHAR(100),
    cnpj        VARCHAR(18),
    localizacao VARCHAR(200)
);

CREATE TABLE IF NOT EXISTS produtos (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    nome           VARCHAR(50),
    categoria      VARCHAR(50),
    quantidade     INTEGER DEFAULT 0,
    estoque_minimo INTEGER DEFAULT 5,
    preco_custo    DECIMAL(10,2),
    preco_venda    DECIMAL(10,2),
    fornecedor_id  INTEGER REFERENCES fornecedores(id),
    descricao      TEXT
);

CREATE TABLE IF NOT EXISTS movimentacoes_estoque (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_id         INTEGER REFERENCES produtos(id) ON DELETE CASCADE,
    tipo               VARCHAR(10) NOT NULL,   -- 'entrada' ou 'saida'
    quantidade         INTEGER     NOT NULL,
    origem             VARCHAR(10) NOT NULL,   -- 'compra', 'venda' ou 'ajuste'
    valor_unitario     DECIMAL(10,2),
    custo_unitario     DECIMAL(10,2),
    data_movimentacao  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS alertas (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_id   INTEGER REFERENCES produtos(id),
    mensagem     VARCHAR(255),
    data_alerta  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolvido    BOOLEAN DEFAULT 0
);

-- ─── Usuário padrão (criado automaticamente pelo app.py) ──────────────────────
-- login: admin | senha: admin123
INSERT OR IGNORE INTO usuario (nome, email, senha, tipo)
VALUES ('admin', 'admin@eightsistemas.com', 'admin123', 'admin');
