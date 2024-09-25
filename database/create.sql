CREATE TABLE produtos (
    id SERIAL PRIMARY KEY,
    nome_produto VARCHAR(255),
    codigo VARCHAR(50),
    preco NUMERIC(10, 2),
    quantidade INT,
    data_validade DATE,
    fornecedor VARCHAR(255)
);

CREATE TABLE usuarios (
    nome VARCHAR(255),
    nickname VARCHAR(50) PRIMARY KEY,
    senha VARCHAR(255)
);