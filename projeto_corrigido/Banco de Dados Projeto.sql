CREATE DATABASE IF NOT EXISTS projeto;
USE projeto;

CREATE TABLE usuario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(50),
    email VARCHAR(50) UNIQUE,
    senha VARCHAR(100) NOT NULL,
    tipo ENUM('admin', 'vendedor')
);

CREATE TABLE fornecedores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    contato VARCHAR(50),
    email VARCHAR(100),
    cnpj VARCHAR(18),
    localizacao VARCHAR(200)
);

CREATE TABLE produtos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(50),
    categoria VARCHAR(50),
    quantidade INT DEFAULT 0,
    estoque_minimo INT DEFAULT 5,
    preco_custo DECIMAL(10,2),
    preco_venda DECIMAL(10,2),
    fornecedor_id INT,
    descricao TEXT,
    FOREIGN KEY(fornecedor_id) REFERENCES fornecedores(id)
);

CREATE TABLE movimentacoes_estoque (
    id INT AUTO_INCREMENT PRIMARY KEY,
    produto_id INT,
    tipo ENUM('entrada', 'saida') NOT NULL,
    quantidade INT NOT NULL,
    origem ENUM('compra', 'venda', 'ajuste') NOT NULL,
    valor_unitario DECIMAL(10, 2),
    custo_unitario DECIMAL(10, 2),
    data_movimentacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(produto_id) REFERENCES produtos(id) ON DELETE CASCADE
);

CREATE TABLE alertas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    produto_id INT,
    mensagem VARCHAR(255),
    data_alerta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolvido BOOLEAN DEFAULT FALSE,
    FOREIGN KEY(produto_id) REFERENCES produtos(id)
);

-- Se o banco já existe e você quer só adicionar as novas colunas, use:
-- ALTER TABLE fornecedores ADD COLUMN email VARCHAR(100);
-- ALTER TABLE fornecedores ADD COLUMN cnpj VARCHAR(18);
-- ALTER TABLE fornecedores ADD COLUMN localizacao VARCHAR(200);
