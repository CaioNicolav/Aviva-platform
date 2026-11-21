-- AVIVA Global Solution 2026.2 | MySQL 8.0+ | ESQUEMA ACADÊMICO
-- Não contém dados de pacientes nem identifica usuários. Não é o banco ativo do site.
CREATE DATABASE IF NOT EXISTS aviva_gs_2026 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE aviva_gs_2026;
SET NAMES utf8mb4;

CREATE TABLE IF NOT EXISTS fonte_dado (
 id_fonte SMALLINT UNSIGNED PRIMARY KEY,
 nome VARCHAR(160) NOT NULL,
 tipo ENUM('OFICIAL','OFICIAL_HISTORICA','SIMULADO','PROTOTIPO') NOT NULL,
 url VARCHAR(600) NULL,
 observacao VARCHAR(500) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS municipio (
 codigo_ibge CHAR(6) PRIMARY KEY,
 nome VARCHAR(120) NOT NULL,
 uf CHAR(2) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS categoria_servico (
 id_categoria VARCHAR(20) PRIMARY KEY,
 descricao VARCHAR(160) NOT NULL,
 criterio VARCHAR(300) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS estabelecimento_saude (
 cnes VARCHAR(15) PRIMARY KEY,
 codigo_ibge CHAR(6) NOT NULL,
 id_categoria VARCHAR(20) NOT NULL,
 nome VARCHAR(255) NOT NULL,
 endereco_cnes VARCHAR(300) NULL,
 bairro_cnes VARCHAR(160) NULL,
 cep_cnes VARCHAR(10) NULL,
 telefone VARCHAR(100) NULL,
 ambulatorial_sus_informado ENUM('SIM','NAO','NAO_INFORMADO') NOT NULL DEFAULT 'NAO_INFORMADO',
 latitude_cnes DECIMAL(11,7) NULL,
 longitude_cnes DECIMAL(11,7) NULL,
 id_fonte_cadastro SMALLINT UNSIGNED NOT NULL,
 CONSTRAINT fk_est_municipio FOREIGN KEY (codigo_ibge) REFERENCES municipio(codigo_ibge),
 CONSTRAINT fk_est_categoria FOREIGN KEY (id_categoria) REFERENCES categoria_servico(id_categoria),
 CONSTRAINT fk_est_fonte FOREIGN KEY (id_fonte_cadastro) REFERENCES fonte_dado(id_fonte),
 INDEX idx_est_categoria_bairro(id_categoria, bairro_cnes),
 INDEX idx_est_nome(nome)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS validacao_localizacao (
 cnes VARCHAR(15) PRIMARY KEY,
 status_auditoria VARCHAR(100) NOT NULL,
 metodo_correspondencia VARCHAR(160) NULL,
 latitude_referencia DECIMAL(11,7) NULL,
 longitude_referencia DECIMAL(11,7) NULL,
 latitude_pin_verificado DECIMAL(11,7) NULL,
 longitude_pin_verificado DECIMAL(11,7) NULL,
 posicao_verificada BOOLEAN NOT NULL DEFAULT FALSE,
 observacoes TEXT NULL,
 id_fonte_referencia SMALLINT UNSIGNED NULL,
 CONSTRAINT fk_val_est FOREIGN KEY(cnes) REFERENCES estabelecimento_saude(cnes),
 CONSTRAINT fk_val_fonte FOREIGN KEY(id_fonte_referencia) REFERENCES fonte_dado(id_fonte),
 CONSTRAINT chk_val_pares CHECK ((latitude_pin_verificado IS NULL AND longitude_pin_verificado IS NULL) OR (latitude_pin_verificado IS NOT NULL AND longitude_pin_verificado IS NOT NULL))
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS area_abrangencia_ubs (
 cnes VARCHAR(15) PRIMARY KEY,
 nome_area VARCHAR(255) NOT NULL,
 regiao_area VARCHAR(100) NULL,
 area_km2_declarada DECIMAL(12,6) NULL,
 id_fonte SMALLINT UNSIGNED NOT NULL,
 CONSTRAINT fk_area_est FOREIGN KEY(cnes) REFERENCES estabelecimento_saude(cnes),
 CONSTRAINT fk_area_fonte FOREIGN KEY(id_fonte) REFERENCES fonte_dado(id_fonte)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS modalidade_reabilitacao (
 id_modalidade VARCHAR(30) PRIMARY KEY,
 descricao VARCHAR(160) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS estabelecimento_modalidade (
 cnes VARCHAR(15) NOT NULL,
 id_modalidade VARCHAR(30) NOT NULL,
 id_fonte_comprovacao SMALLINT UNSIGNED NOT NULL,
 observacao VARCHAR(300) NULL,
 PRIMARY KEY (cnes,id_modalidade),
 CONSTRAINT fk_em_est FOREIGN KEY(cnes) REFERENCES estabelecimento_saude(cnes),
 CONSTRAINT fk_em_mod FOREIGN KEY(id_modalidade) REFERENCES modalidade_reabilitacao(id_modalidade),
 CONSTRAINT fk_em_fonte FOREIGN KEY(id_fonte_comprovacao) REFERENCES fonte_dado(id_fonte)
) ENGINE=InnoDB;
-- A tabela ponte está vazia de propósito: nome/CNES isolados não comprovam habilitação em modalidade.

CREATE TABLE IF NOT EXISTS estacao_meteorologica (
 codigo_estacao VARCHAR(20) PRIMARY KEY,
 id_fonte SMALLINT UNSIGNED NOT NULL,
 observacao VARCHAR(300) NOT NULL,
 CONSTRAINT fk_estacao_fonte FOREIGN KEY(id_fonte) REFERENCES fonte_dado(id_fonte)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS clima_diario (
 id_clima BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
 codigo_estacao VARCHAR(20) NOT NULL,
 data_observacao DATE NOT NULL,
 chuva_dia_mm DECIMAL(12,4) NULL,
 chuva_max_hora_mm DECIMAL(12,4) NULL,
 horas_com_chuva SMALLINT UNSIGNED NULL,
 pressao_media_hpa DECIMAL(12,4) NULL,
 pressao_amplitude_hpa DECIMAL(12,4) NULL,
 temperatura_media_c DECIMAL(10,4) NULL,
 temperatura_max_c DECIMAL(10,4) NULL,
 temperatura_min_c DECIMAL(10,4) NULL,
 umidade_media_pct DECIMAL(10,4) NULL,
 umidade_min_pct DECIMAL(10,4) NULL,
 vento_medio_ms DECIMAL(10,4) NULL,
 rajada_maxima_ms DECIMAL(10,4) NULL,
 horas_faltantes SMALLINT UNSIGNED NULL,
 chuva_dia_mm_d1 DECIMAL(12,4) NULL,
 umidade_media_pct_d1 DECIMAL(10,4) NULL,
 pressao_media_hpa_d1 DECIMAL(12,4) NULL,
 chuva_dia_mm_d2 DECIMAL(12,4) NULL,
 umidade_media_pct_d2 DECIMAL(10,4) NULL,
 pressao_media_hpa_d2 DECIMAL(12,4) NULL,
 pressao_media_variacao_d1_d DECIMAL(12,4) NULL,
 chuva_amanha_alvo_historico_mm DECIMAL(12,4) NULL,
 UNIQUE KEY uq_clima_estacao_data(codigo_estacao,data_observacao),
 CONSTRAINT fk_clima_estacao FOREIGN KEY(codigo_estacao) REFERENCES estacao_meteorologica(codigo_estacao)
) ENGINE=InnoDB;
-- chuva_amanha_alvo_historico_mm é alvo tabular do dataset, NÃO previsão ao vivo.

CREATE TABLE IF NOT EXISTS evento_comunitario (
 id_evento CHAR(36) PRIMARY KEY,
 tipo VARCHAR(50) NOT NULL,
 distrito_codigo VARCHAR(20) NOT NULL,
 data_hora DATETIME NOT NULL,
 status_evento VARCHAR(45) NOT NULL,
 origem ENUM('SIMULADO','OFICIAL','USUARIO') NOT NULL,
 id_fonte SMALLINT UNSIGNED NOT NULL,
 CONSTRAINT fk_evento_fonte FOREIGN KEY(id_fonte) REFERENCES fonte_dado(id_fonte),
 INDEX idx_evento_distrito_hora(distrito_codigo,data_hora)
) ENGINE=InnoDB;
-- Todos os eventos carregados nesta entrega são SIMULADOS (não são denúncias reais).

CREATE TABLE IF NOT EXISTS dispositivo_iot (
 id_dispositivo VARCHAR(50) PRIMARY KEY,
 modelo VARCHAR(80) NOT NULL,
 descricao VARCHAR(255) NOT NULL,
 origem ENUM('SIMULADOR','FISICO') NOT NULL,
 id_fonte SMALLINT UNSIGNED NOT NULL,
 CONSTRAINT fk_iot_fonte FOREIGN KEY(id_fonte) REFERENCES fonte_dado(id_fonte)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS leitura_iot (
 id_leitura BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
 id_dispositivo VARCHAR(50) NOT NULL,
 data_hora DATETIME NOT NULL,
 nivel_agua_cm DECIMAL(10,3) NULL,
 chuva_simulada_mm_h DECIMAL(10,3) NULL,
 umidade_dht22_pct DECIMAL(10,3) NULL,
 situacao ENUM('NORMAL','ATENCAO','CRITICO','INDETERMINADO') NOT NULL,
 falha_sensor VARCHAR(120) NULL,
 natureza ENUM('EXEMPLO_DIDATICO','LEITURA_EXPORTADA') NOT NULL,
 CONSTRAINT fk_leitura_dispositivo FOREIGN KEY(id_dispositivo) REFERENCES dispositivo_iot(id_dispositivo),
 INDEX idx_leitura_hora(id_dispositivo,data_hora)
) ENGINE=InnoDB;
-- As 3 leituras inseridas são EXEMPLOS DIDÁTICOS, não registros reais capturados do Wokwi.

CREATE TABLE IF NOT EXISTS alerta_iot (
 id_alerta BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
 id_leitura BIGINT UNSIGNED NOT NULL UNIQUE,
 nivel ENUM('NORMAL','ATENCAO','CRITICO','INDETERMINADO') NOT NULL,
 orientacao VARCHAR(350) NOT NULL,
 gerado_em DATETIME NOT NULL,
 CONSTRAINT fk_alerta_leitura FOREIGN KEY(id_leitura) REFERENCES leitura_iot(id_leitura)
) ENGINE=InnoDB;

-- Interfaces de leitura para futura API. Não implicam integração com AVIVA em produção.
CREATE OR REPLACE VIEW vw_servicos_mapa AS
SELECT e.cnes,e.nome,e.id_categoria,e.endereco_cnes,e.bairro_cnes,
       COALESCE(v.latitude_pin_verificado,e.latitude_cnes) AS latitude_exibicao,
       COALESCE(v.longitude_pin_verificado,e.longitude_cnes) AS longitude_exibicao,
       CASE WHEN v.posicao_verificada=1 THEN 'POSICAO_CONFERIDA' ELSE 'POSICAO_NAO_VERIFICADA' END AS selo_mapa,
       CASE WHEN v.posicao_verificada=1 THEN 'Ponto cruzado com referencia municipal; confirme funcionamento antes de ir.'
            ELSE 'Endereco e/ou coordenadas sem verificacao independente; confirme antes de se deslocar.' END AS aviso,
       e.ambulatorial_sus_informado,v.status_auditoria
FROM estabelecimento_saude e LEFT JOIN validacao_localizacao v ON v.cnes=e.cnes
WHERE COALESCE(v.latitude_pin_verificado,e.latitude_cnes) IS NOT NULL
  AND COALESCE(v.longitude_pin_verificado,e.longitude_cnes) IS NOT NULL;

CREATE OR REPLACE VIEW vw_leituras_alertas AS
SELECT d.id_dispositivo,l.id_leitura,l.data_hora,l.nivel_agua_cm,l.chuva_simulada_mm_h,l.umidade_dht22_pct,
 l.situacao,l.natureza,a.orientacao
FROM dispositivo_iot d JOIN leitura_iot l ON l.id_dispositivo=d.id_dispositivo
LEFT JOIN alerta_iot a ON a.id_leitura=l.id_leitura;
