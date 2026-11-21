"""Valida a preparação dos dados e a separação entre fontes reais e simuladas.

Confere agregações, formatos e restrições usadas no conjunto de testes."""

import csv
import uuid

import pandas as pd
import pytest

from aviva.apresentacao import proteger_valor_ranking
from scripts.gerar_eventos_simulados import CAMPOS, gerar_eventos
from scripts.montar_dataset import montar_dataset
from scripts import ingestao_chuva


CAMPOS_PESSOAIS = {
    "nome",
    "telefone",
    "endereco",
    "latitude",
    "longitude",
    "coordenada",
}


def test_gerador_e_reprodutivel_com_mesma_semente():
    primeiro = gerar_eventos(semente=73, quantidade=20)
    segundo = gerar_eventos(semente=73, quantidade=20)

    assert [
        {chave: valor for chave, valor in evento.items() if chave != "id_evento"}
        for evento in primeiro
    ] == [
        {chave: valor for chave, valor in evento.items() if chave != "id_evento"}
        for evento in segundo
    ]


def test_eventos_tem_colunas_origem_ids_unicos_e_sem_dados_pessoais():
    eventos = gerar_eventos(semente=19, quantidade=50)

    assert set(eventos[0]) == set(CAMPOS)
    assert all(evento["origem"] == "simulado" for evento in eventos)
    assert len({evento["id_evento"] for evento in eventos}) == len(eventos)
    assert all(uuid.UUID(evento["id_evento"]).version == 4 for evento in eventos)
    assert not CAMPOS_PESSOAIS.intersection(eventos[0])
    assert all(evento["distrito"].startswith("D") for evento in eventos)


@pytest.mark.parametrize(
    "quantidade,esperado",
    [(0, "dados insuficientes"), (4, "dados insuficientes"), (5, 42)],
)
def test_ranking_protege_grupos_com_menos_de_k_eventos(quantidade, esperado):
    assert proteger_valor_ranking(42, quantidade) == esperado


def test_montagem_inclui_origem_real_e_simulada(tmp_path):
    (tmp_path / "chuva_semanal.csv").write_text(
        "distrito,semana,chuva_mm\nCODIGO_REAL_TESTE,2025-W01,12.5\n",
        encoding="utf-8",
    )
    (tmp_path / "eventos_violencia_simulados.csv").write_text(
        "id_evento,tipo,distrito,data_hora,status,origem\n"
        "id1,alerta,D01,2025-01-01T22:00:00,atendido,simulado\n",
        encoding="utf-8",
    )

    saida = montar_dataset(tmp_path)

    with saida.open(newline="", encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)
        linhas = list(leitor)

    assert "origem_ambiental" in leitor.fieldnames
    assert "origem_vulnerabilidade" not in leitor.fieldnames
    assert "origem_violencia" in leitor.fieldnames
    assert linhas == [
        {
            "distrito": "CODIGO_REAL_TESTE",
            "semana": "2025-W01",
            "chuva_mm": "12.5",
            "origem_ambiental": "real",
            "total_alertas": "",
            "total_denuncias": "",
            "alertas_atendidos": "",
            "alertas_cancelados": "",
            "alertas_em_aberto": "",
            "denuncias_atendidas": "",
            "denuncias_canceladas": "",
            "denuncias_em_aberto": "",
            "origem_violencia": "",
        },
        {
            "distrito": "D01",
            "semana": "2025-W01",
            "chuva_mm": "",
            "origem_ambiental": "",
            "total_alertas": "1",
            "total_denuncias": "0",
            "alertas_atendidos": "1",
            "alertas_cancelados": "0",
            "alertas_em_aberto": "0",
            "denuncias_atendidas": "0",
            "denuncias_canceladas": "0",
            "denuncias_em_aberto": "0",
            "origem_violencia": "simulado",
        }
    ]


def test_montagem_avisa_e_omite_fonte_real_ausente(tmp_path, capsys):
    saida = montar_dataset(tmp_path)

    assert saida.is_file()
    assert "fonte real chuva ausente" in capsys.readouterr().out
    with saida.open(newline="", encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)
        assert leitor.fieldnames == ["distrito", "semana"]


def test_ingestao_falha_claramente_sem_arquivo_real(tmp_path):
    caminho = tmp_path / "inmet_chuva.csv"

    with pytest.raises(FileNotFoundError, match="Baixe o arquivo"):
        ingestao_chuva.ingestir(caminho)


def test_ingestao_chuva_converte_fuso_e_descarta_coluna_extra(tmp_path):
    arquivo = tmp_path / "A701.CSV"
    arquivo.write_text(
        "REGIAO:;SE\n"
        "UF:;SP\n"
        "ESTACAO:;SAO PAULO - MIRANTE\n"
        "CODIGO (WMO):;A701\n"
        "LATITUDE:;-23,5\n"
        "LONGITUDE:;-46,6\n"
        "ALTITUDE:;785\n"
        "DATA DE FUNDACAO:;25/07/06\n"
        "Data;Hora UTC;PRECIPITAÇÃO TOTAL, HORÁRIO (mm);PRESSAO ATMOSFERICA AO NIVEL DA ESTACAO, HORARIA (mB);TEMPERATURA DO AR - BULBO SECO, HORARIA (°C);UMIDADE RELATIVA DO AR, HORARIA (%);VENTO, VELOCIDADE HORARIA (m/s);\n"
        "2026/01/01;0000 UTC;0;924,7;25,1;58;2,6;\n"
        "2026/01/01;0100 UTC;0,4;923,9;24,4;59;1,2;\n"
        "2026/01/02;0000 UTC;1,2;921,0;23,1;80;3,4;\n",
        encoding="latin-1",
    )

    df = ingestao_chuva._carregar_estacao(arquivo)

    assert "precipitacao_mm" in df.columns
    assert "vento_velocidade_ms" in df.columns
    assert "horas_faltantes" in df.columns
    assert df.loc[0, "data"] == "2025-12-31"
    assert df.loc[0, "hora_utc"] == "21:00:00"
    assert df.loc[0, "pressao_hpa"] == 924.7
    assert df.loc[1, "precipitacao_mm"] == 0.4
    assert df.loc[0, "data_local"].tzinfo is not None


def test_ingestao_chuva_agrupa_mensuracoes_e_nao_preenche_ausentes_em_zero(tmp_path):
    arquivo = tmp_path / "A771.CSV"
    arquivo.write_text(
        "REGIAO:;SE\n"
        "UF:;SP\n"
        "ESTACAO:;SAO PAULO - INTERLAGOS\n"
        "CODIGO (WMO):;A771\n"
        "LATITUDE:;-23,7\n"
        "LONGITUDE:;-46,6\n"
        "ALTITUDE:;771\n"
        "DATA DE FUNDACAO:;14/03/18\n"
        "Data;Hora UTC;PRECIPITAÇÃO TOTAL, HORÁRIO (mm);PRESSAO ATMOSFERICA AO NIVEL DA ESTACAO, HORARIA (mB);TEMPERATURA DO AR - BULBO SECO, HORARIA (°C);UMIDADE RELATIVA DO AR, HORARIA (%);VENTO, VELOCIDADE HORARIA (m/s);\n"
        "2026/01/01;0000 UTC;0;924,7;25,1;58;2,6;\n"
        "2026/01/01;0100 UTC;;923,8;24,4;59;1,2;\n"
        "2026/01/02;0000 UTC;1,2;921,0;23,1;80;3,4;\n",
        encoding="latin-1",
    )

    diaria = ingestao_chuva.agregar_chuva_diaria(arquivo)

    assert diaria["data"].tolist() == ["2025-12-31", "2026-01-01"]
    assert diaria.loc[0, "chuva_dia_mm"] == 0.0
    assert diaria.loc[0, "horas_faltantes"] == 2
    assert diaria.loc[1, "chuva_dia_mm"] == 1.2


def test_montar_dataset_clima_gera_defasagens_sem_vazamento_de_d_mais_um(tmp_path):
    arquivo_a = tmp_path / "A701.CSV"
    arquivo_b = tmp_path / "A771.CSV"
    for codigo, linha1, linha2, linha3 in [
        ("A701", "2026/01/01;0000 UTC;0;920,0;25;80;2,0;", "2026/01/02;0000 UTC;3;919,0;24;79;1,5;", "2026/01/03;0000 UTC;0;918,0;22;75;1,0;"),
        ("A771", "2026/01/01;0000 UTC;1;930,0;26;70;2,5;", "2026/01/02;0000 UTC;4;929,0;25;72;2,0;", "2026/01/03;0000 UTC;2;928,0;24;73;1,5;"),
    ]:
        arquivo = arquivo_a if codigo == "A701" else arquivo_b
        arquivo.write_text(
            "REGIAO:;SE\n"
            "UF:;SP\n"
            "ESTACAO:;TESTE\n"
            "CODIGO (WMO):;" + codigo + "\n"
            "LATITUDE:;-23,0\n"
            "LONGITUDE:;-46,0\n"
            "ALTITUDE:;100\n"
            "DATA DE FUNDACAO:;01/01/18\n"
            "Data;Hora UTC;PRECIPITAÇÃO TOTAL, HORÁRIO (mm);PRESSAO ATMOSFERICA AO NIVEL DA ESTACAO, HORARIA (mB);TEMPERATURA DO AR - BULBO SECO, HORARIA (°C);UMIDADE RELATIVA DO AR, HORARIA (%);VENTO, VELOCIDADE HORARIA (m/s);\n"
            f"{linha1}\n{linha2}\n{linha3}\n",
            encoding="latin-1",
        )

    saida = tmp_path / "aviva_clima_diario.csv"
    caminho = ingestao_chuva.montar_aviva_clima_diario(tmp_path, saida)

    assert caminho.exists()
    df = __import__("pandas").read_csv(caminho)
    assert {"estacao", "data", "chuva_amanha_mm"}.issubset(df.columns)
    assert df["chuva_amanha_mm"].notna().any()
    assert df["chuva_dia_mm_d1"].isna().sum() >= 1
    assert df["chuva_dia_mm_d2"].isna().sum() >= 2


def test_gerador_eventos_tem_distritos_neutros_e_nao_abre_antigos(tmp_path):
    eventos = gerar_eventos(semente=73, quantidade=80)

    assert {evento["distrito"] for evento in eventos} <= {f"D{i:02d}" for i in range(1, 21)}
    assert all(evento["origem"] == "simulado" for evento in eventos)
    assert all("em_aberto" != evento["status"] for evento in eventos)
    assert all(len(evento["id_evento"]) > 0 for evento in eventos)


def test_horas_faltantes_ignora_radiacao_e_variaveis_nao_usadas(tmp_path):
    arquivo = tmp_path / "A701.CSV"
    colunas = ingestao_chuva.COLUNAS_PADRAO
    cabecalho = ["Data", "Hora UTC", *colunas[2:]]
    linha = [""] * len(colunas)
    linha[0:2] = ["2026/01/01", "0300 UTC"]
    for coluna, valor in {
        "precipitacao_mm": "0",
        "pressao_hpa": "924,7",
        "temperatura_ar_c": "25,1",
        "umidade_relativa_pct": "58",
        "rajada_maxima_ms": "7",
        "vento_velocidade_ms": "2,6",
    }.items():
        linha[colunas.index(coluna)] = valor
    arquivo.write_text(
        "REGIAO:;SE\n"
        "UF:;SP\n"
        "ESTACAO:;SAO PAULO - MIRANTE\n"
        "CODIGO (WMO):;A701\n"
        "LATITUDE:;-23,5\n"
        "LONGITUDE:;-46,6\n"
        "ALTITUDE:;785\n"
        "DATA DE FUNDACAO:;25/07/06\n"
        + ";".join(cabecalho)
        + ";\n"
        + ";".join(linha)
        + ";\n",
        encoding="latin-1",
    )

    df = ingestao_chuva._carregar_estacao(arquivo)

    assert pd.isna(df.loc[0, "radiacao_global_kj_m2"])
    assert pd.isna(df.loc[0, "temperatura_orvalho_c"])
    assert df.loc[0, "horas_faltantes"] == 0


def test_dataset_descarta_bordas_parciais_e_linhas_sem_alvo(tmp_path):
    arquivo = tmp_path / "A701.CSV"
    colunas = ingestao_chuva.COLUNAS_PADRAO
    cabecalho = ["Data", "Hora UTC", *colunas[2:]]
    linhas = []
    inicio = pd.Timestamp("2026-01-01 00:00:00")
    for hora in range(53):
        instante = inicio + pd.Timedelta(hours=hora)
        linha = [""] * len(colunas)
        linha[0] = instante.strftime("%Y/%m/%d")
        linha[1] = instante.strftime("%H00 UTC")
        for coluna, valor in {
            "precipitacao_mm": "0",
            "pressao_hpa": "924,7",
            "pressao_max_hpa": "925",
            "pressao_min_hpa": "924",
            "temperatura_ar_c": "25,1",
            "umidade_relativa_pct": "58",
            "rajada_maxima_ms": "7",
            "vento_velocidade_ms": "2,6",
        }.items():
            linha[colunas.index(coluna)] = valor
        linhas.append(";".join(linha) + ";")

    arquivo.write_text(
        "REGIAO:;SE\n"
        "UF:;SP\n"
        "ESTACAO:;SAO PAULO - MIRANTE\n"
        "CODIGO (WMO):;A701\n"
        "LATITUDE:;-23,5\n"
        "LONGITUDE:;-46,6\n"
        "ALTITUDE:;785\n"
        "DATA DE FUNDACAO:;25/07/06\n"
        + ";".join(cabecalho)
        + ";\n"
        + "\n".join(linhas)
        + "\n",
        encoding="latin-1",
    )

    saida = tmp_path / "aviva_clima_diario.csv"
    ingestao_chuva.montar_aviva_clima_diario(tmp_path, saida)
    dataset = __import__("pandas").read_csv(saida)

    assert dataset["data"].tolist() == ["2026-01-01"]
    assert dataset["chuva_amanha_mm"].tolist() == [0.0]
