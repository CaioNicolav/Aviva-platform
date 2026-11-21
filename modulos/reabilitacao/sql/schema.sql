-- Esquema conceitual para evolução do AVIVA. Não executado pelo MVP atual.
CREATE TABLE municipio (
  codigo_ibge CHAR(7) PRIMARY KEY,
  uf CHAR(2) NOT NULL,
  nome VARCHAR(120) NOT NULL
);
CREATE TABLE estabelecimento (
  cnes VARCHAR(15) PRIMARY KEY,
  codigo_ibge CHAR(7),
  nome VARCHAR(200) NOT NULL,
  endereco VARCHAR(300),
  telefone VARCHAR(80),
  atende_sus BOOLEAN NOT NULL DEFAULT FALSE,
  fonte_url VARCHAR(500) NOT NULL,
  data_referencia DATE,
  status_verificacao VARCHAR(30) NOT NULL,
  FOREIGN KEY (codigo_ibge) REFERENCES municipio(codigo_ibge)
);
CREATE TABLE modalidade (id VARCHAR(30) PRIMARY KEY, nome VARCHAR(100) NOT NULL);
CREATE TABLE estabelecimento_modalidade (
  cnes VARCHAR(15) NOT NULL,
  modalidade_id VARCHAR(30) NOT NULL,
  PRIMARY KEY (cnes, modalidade_id),
  FOREIGN KEY (cnes) REFERENCES estabelecimento(cnes),
  FOREIGN KEY (modalidade_id) REFERENCES modalidade(id)
);
