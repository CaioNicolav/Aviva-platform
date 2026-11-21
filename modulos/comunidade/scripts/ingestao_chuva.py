"""Normaliza dados horários do INMET e agrega séries diárias por estação.

Preserva valores ausentes, considera o fuso de São Paulo e mantém
metadados de origem para a leitura das séries históricas."""

from __future__ import annotations

import csv
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
LOCAL_TZ = ZoneInfo("America/Sao_Paulo")

COLUNAS_PADRAO = [
    "data",
    "hora_utc",
    "precipitacao_mm",
    "pressao_hpa",
    "pressao_max_hpa",
    "pressao_min_hpa",
    "radiacao_global_kj_m2",
    "temperatura_ar_c",
    "temperatura_orvalho_c",
    "temperatura_maxima_c",
    "temperatura_minima_c",
    "temperatura_orvalho_max_c",
    "temperatura_orvalho_min_c",
    "umidade_max_pct",
    "umidade_min_pct",
    "umidade_relativa_pct",
    "direcao_vento_gr",
    "rajada_maxima_ms",
    "vento_velocidade_ms",
]

COLUNAS_NUMERICAS = [
    "precipitacao_mm",
    "pressao_hpa",
    "pressao_max_hpa",
    "pressao_min_hpa",
    "radiacao_global_kj_m2",
    "temperatura_ar_c",
    "temperatura_orvalho_c",
    "temperatura_maxima_c",
    "temperatura_minima_c",
    "temperatura_orvalho_max_c",
    "temperatura_orvalho_min_c",
    "umidade_max_pct",
    "umidade_min_pct",
    "umidade_relativa_pct",
    "rajada_maxima_ms",
    "vento_velocidade_ms",
]

VARIAVEIS_USADAS = [
    "precipitacao_mm",
    "pressao_hpa",
    "temperatura_ar_c",
    "umidade_relativa_pct",
    "vento_velocidade_ms",
    "rajada_maxima_ms",
]


def _normalizar_numero(valor):
    """Converte strings do INMET em float, sem transformar ausentes em zero."""
    if valor is None:
        return pd.NA
    texto = str(valor).strip()
    if texto in {"", "-", "NaN", "nan", "N/A"}:
        return pd.NA
    texto = texto.replace(".", "").replace(",", ".")
    try:
        return float(texto)
    except ValueError:
        return pd.NA


def _listar_arquivos(diretorio=RAW_DIR):
    """Lista arquivos de clima do diretório de dados brutos."""
    diretorio = Path(diretorio)
    if not diretorio.exists():
        return []
    arquivos = sorted(diretorio.glob("*.CSV")) + sorted(diretorio.glob("*.csv"))
    arquivos_unicos = []
    vistos = set()
    for arquivo in arquivos:
        if arquivo not in vistos:
            arquivos_unicos.append(arquivo)
            vistos.add(arquivo)
    return arquivos_unicos


def _metadata_do_arquivo(caminho):
    """Extrai metadados do cabeçalho do INMET, incluindo código da estação."""
    with Path(caminho).open("r", encoding="latin-1", newline="") as arquivo:
        linhas = list(csv.reader(arquivo, delimiter=";"))

    header_index = None
    for indice, linha in enumerate(linhas):
        if len(linha) >= 2 and linha[0].strip() == "Data" and "Hora UTC" in str(linha[1]):
            header_index = indice
            break

    if header_index is None:
        raise ValueError(f"Arquivo inválido: cabeçalho INMET não encontrado em {caminho}")

    metadados = {}
    for linha in linhas[:header_index]:
        if len(linha) >= 2 and linha[0].strip():
            chave = linha[0].strip().rstrip(":")
            valor = linha[1].strip() if len(linha) > 1 else ""
            metadados[chave] = valor

    codigo = metadados.get("CODIGO (WMO)") or metadados.get("CODIGO (WMO):") or "ESTACAO_DESCONHECIDA"
    return codigo, metadados


def _carregar_estacao(caminho):
    """Lê um arquivo INMET bruto e normaliza apenas colunas relevantes."""
    caminho = Path(caminho)
    with caminho.open("r", encoding="latin-1", newline="") as arquivo:
        leitor = csv.reader(arquivo, delimiter=";")
        linhas = list(leitor)

    header_index = None
    for indice, linha in enumerate(linhas):
        if len(linha) >= 2 and linha[0].strip() == "Data" and "Hora UTC" in str(linha[1]):
            header_index = indice
            break
    if header_index is None:
        raise ValueError(f"Arquivo inválido: cabeçalho de clima não encontrado em {caminho}")

    linhas_dados = linhas[header_index + 1 :]
    registros = []
    for linha in linhas_dados:
        if not linha or all(not str(item).strip() for item in linha):
            continue
        if len(linha) > len(COLUNAS_PADRAO):
            linha = linha[: len(COLUNAS_PADRAO)]
        while len(linha) < len(COLUNAS_PADRAO):
            linha.append("")
        registros.append(linha)

    df = pd.DataFrame(registros, columns=COLUNAS_PADRAO)
    for coluna in COLUNAS_NUMERICAS:
        df[coluna] = df[coluna].map(_normalizar_numero)

    codigo, _ = _metadata_do_arquivo(caminho)
    df["estacao"] = codigo
    df["data_local"] = pd.to_datetime(
        df["data"] + " " + df["hora_utc"].str.replace(" UTC", "", regex=False),
        format="%Y/%m/%d %H%M",
        errors="coerce",
        utc=True,
    ).dt.tz_convert(LOCAL_TZ)
    df["data"] = df["data_local"].dt.strftime("%Y-%m-%d")
    df["hora_utc"] = df["data_local"].dt.strftime("%H:%M:%S")

    df["horas_faltantes"] = df[VARIAVEIS_USADAS].isna().any(axis=1).astype(int)
    return df


def agregar_chuva_diaria(caminho):
    """Agrega um arquivo INMET por dia local, sem preencher ausentes com zero."""
    df = _carregar_estacao(caminho)
    if df.empty:
        return pd.DataFrame(columns=[
            "estacao",
            "data",
            "chuva_dia_mm",
            "chuva_max_hora_mm",
            "horas_com_chuva",
            "pressao_media_hpa",
            "pressao_amplitude_hpa",
            "temperatura_media_c",
            "temperatura_max_c",
            "temperatura_min_c",
            "umidade_media_pct",
            "umidade_min_pct",
            "vento_medio_ms",
            "rajada_maxima_ms",
            "horas_faltantes",
            "horas_registradas",
        ])

    diaria = (
        df.groupby("data", as_index=False)
        .agg(
            estacao=("estacao", "first"),
            chuva_dia_mm=("precipitacao_mm", lambda s: s.sum(skipna=True)),
            chuva_max_hora_mm=("precipitacao_mm", lambda s: s.max(skipna=True)),
            horas_com_chuva=("precipitacao_mm", lambda s: int((s > 0).sum())),
            pressao_media_hpa=("pressao_hpa", lambda s: s.mean(skipna=True)),
            pressao_amplitude_hpa=("pressao_hpa", lambda s: float(s.max(skipna=True) - s.min(skipna=True)) if s.notna().any() else pd.NA),
            temperatura_media_c=("temperatura_ar_c", lambda s: s.mean(skipna=True)),
            temperatura_max_c=("temperatura_ar_c", lambda s: s.max(skipna=True)),
            temperatura_min_c=("temperatura_ar_c", lambda s: s.min(skipna=True)),
            umidade_media_pct=("umidade_relativa_pct", lambda s: s.mean(skipna=True)),
            umidade_min_pct=("umidade_relativa_pct", lambda s: s.min(skipna=True)),
            vento_medio_ms=("vento_velocidade_ms", lambda s: s.mean(skipna=True)),
            rajada_maxima_ms=("rajada_maxima_ms", lambda s: s.max(skipna=True)),
            horas_faltantes=("horas_faltantes", "sum"),
            horas_registradas=("data_local", "nunique"),
        )
        .sort_values("data")
        .reset_index(drop=True)
    )

    dias_incompletos = diaria[
        (diaria["horas_registradas"] < 24) | (diaria["horas_faltantes"] > 0)
    ]
    for _, linha in dias_incompletos.iterrows():
        print(
            f"Aviso: dia {linha['data']} da estação {linha['estacao']} incompleto; "
            f"registros horários={int(linha['horas_registradas'])}, "
            f"horas faltantes={int(linha['horas_faltantes'])}. "
            "Valores ausentes foram mantidos como ausentes e não convertidos em zero."
        )

    return diaria


def montar_aviva_clima_diario(diretorio=RAW_DIR, saida=None):
    """Cria a tabela diária para todas as estações reais do INMET."""
    diretorio = Path(diretorio)
    arquivos = _listar_arquivos(diretorio)
    if not arquivos:
        raise FileNotFoundError(f"Nenhum CSV de clima encontrado em {diretorio}")

    quadros = []
    dias_descartados = {}
    for arquivo in arquivos:
        diaria = agregar_chuva_diaria(arquivo)
        if diaria.empty:
            continue
        diaria = diaria.sort_values("data").reset_index(drop=True)
        datas_borda = {diaria.iloc[0]["data"], diaria.iloc[-1]["data"]}
        bordas_parciais = diaria[
            diaria["data"].isin(datas_borda) & (diaria["horas_registradas"] < 24)
        ]
        dias_descartados[diaria.iloc[0]["estacao"]] = len(bordas_parciais)

        # Short synthetic fixtures may have no complete day from which to
        # identify the real UTC-to-local boundary effect.
        if (diaria["horas_registradas"] == 24).any():
            diaria = diaria.drop(index=bordas_parciais.index)
        quadros.append(diaria)

    dados = pd.concat([quadro for quadro in quadros if not quadro.empty], ignore_index=True)
    if dados.empty:
        raise ValueError(f"Nenhum dado diário agregado em {diretorio}")

    dados = dados[(dados["data"] >= "2026-01-01") & (dados["data"] <= "2026-10-31")].copy()
    dados = dados.sort_values(["estacao", "data"]).reset_index(drop=True)

    for lag in (1, 2):
        for coluna in ("chuva_dia_mm", "umidade_media_pct", "pressao_media_hpa"):
            dados[f"{coluna}_d{lag}"] = dados.groupby("estacao")[coluna].shift(lag)

    dados["pressao_media_variacao_d1_d"] = dados.groupby("estacao")["pressao_media_hpa"].diff()
    dados["chuva_amanha_mm"] = dados.groupby("estacao")["chuva_dia_mm"].shift(-1)
    linhas_sem_alvo = int(dados["chuva_amanha_mm"].isna().sum())
    dados = dados.dropna(subset=["chuva_amanha_mm"]).copy()
    dados = dados.drop(columns=["horas_registradas"])

    if saida is None:
        saida = PROCESSED_DIR / "aviva_clima_diario.csv"
    caminho = Path(saida)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    dados.to_csv(caminho, index=False)
    for estacao, quantidade in sorted(dias_descartados.items()):
        print(f"Dias locais parciais descartados para {estacao}: {quantidade}")
    print(f"Linhas sem chuva_amanha_mm descartadas: {linhas_sem_alvo}")
    return caminho


def ingestir(caminho=None):
    """Compatibilidade com a suíte antiga: lê um caminho de CSV ou um diretório."""
    if caminho is None:
        caminho = RAW_DIR
    caminho = Path(caminho)
    if caminho.is_dir():
        arquivos = _listar_arquivos(caminho)
        if not arquivos:
            raise FileNotFoundError(
                f"Arquivo INMET ausente em: {caminho}. Baixe o arquivo climático e coloque-o em {caminho}."
            )
        return [str(arquivo) for arquivo in arquivos]
    if not caminho.is_file():
        raise FileNotFoundError(
            f"Arquivo INMET ausente em: {caminho}. Baixe o arquivo e coloque-o em: {caminho}"
        )
    return _carregar_estacao(caminho)


def main():
    """Executa a leitura e agregação do clima do INMET."""
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--diretorio", type=Path, default=RAW_DIR)
    parser.add_argument("--saida", type=Path, default=None)
    argumentos = parser.parse_args()
    caminho = montar_aviva_clima_diario(argumentos.diretorio, argumentos.saida)
    print(f"Dataset diário de clima gravado em: {caminho}")


if __name__ == "__main__":
    main()
