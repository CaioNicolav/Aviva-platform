"""AVIVA | Consolidação de dados territoriais e ambientais.
Agrupa fontes disponíveis e mantém eventos simulados separados dos registros oficiais.
"""

import argparse
import csv
from collections import defaultdict
from datetime import date
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from scripts.ingestao_chuva import montar_aviva_clima_diario
except ModuleNotFoundError:  # pragma: no cover - direct-script fallback
    from ingestao_chuva import montar_aviva_clima_diario


DIRETORIO_DADOS = Path(__file__).resolve().parents[1] / "data" / "processed"
FONTES_REAIS = {
    "chuva": ("chuva_semanal.csv", "chuva_mm", "ambiental"),
    "nivel_rio": ("nivel_rio_semanal.csv", "nivel_rio_m", "ambiental"),
    "desastres": ("desastres_semanal.csv", "total_desastres", "ambiental"),
    "ipvs": ("ipvs_semanal.csv", "ipvs", "vulnerabilidade"),
}
COLUNAS_EVENTOS = (
    "total_alertas",
    "total_denuncias",
    "alertas_atendidos",
    "alertas_cancelados",
    "alertas_em_aberto",
    "denuncias_atendidas",
    "denuncias_canceladas",
    "denuncias_em_aberto",
)


def _ler_linhas(caminho, colunas_obrigatorias):
    """Lê CSV UTF-8 normalizado e valida o cabeçalho."""
    with caminho.open("r", newline="", encoding="utf-8-sig") as arquivo:
        leitor = csv.DictReader(arquivo)
        ausentes = set(colunas_obrigatorias) - set(leitor.fieldnames or ())
        if ausentes:
            nomes = ", ".join(sorted(ausentes))
            raise ValueError(f"{caminho}: faltam colunas obrigatórias: {nomes}")
        return list(leitor)


def _adicionar_fonte_real(dados, diretorio, modulo, nome_arquivo, coluna, grupo):
    """Inclui valores reais semanais e avisa quando o arquivo não existe."""
    caminho = diretorio / nome_arquivo
    if not caminho.is_file():
        print(
            f"Aviso: fonte real {modulo} ausente ({caminho}); "
            f"colunas {coluna} e origem_{modulo} omitidas."
        )
        return
    linhas = _ler_linhas(caminho, ("distrito", "semana", coluna))
    for linha in linhas:
        chave = (linha["distrito"], linha["semana"])
        if re.fullmatch(r"D\d{2}", chave[0]):
            raise ValueError(
                f"{caminho}: distrito {chave[0]!r} usa código reservado "
                "a eventos simulados"
            )
        if chave in dados and coluna in dados[chave]:
            raise ValueError(
                f"{caminho}: mais de um registro para "
                f"distrito={chave[0]!r}, semana={chave[1]!r}"
            )
        dados[chave][coluna] = linha[coluna]
        dados[chave][f"origem_{grupo}"] = "real"


def _adicionar_eventos_simulados(dados, diretorio):
    """Agrega eventos sintéticos por distrito e semana ISO."""
    caminho = diretorio / "eventos_violencia_simulados.csv"
    if not caminho.is_file():
        print(
            f"Aviso: eventos simulados ausentes ({caminho}); "
            "colunas de violência omitidas."
        )
        return

    linhas = _ler_linhas(
        caminho, ("tipo", "distrito", "data_hora", "status", "origem")
    )
    agregados = defaultdict(lambda: {coluna: 0 for coluna in COLUNAS_EVENTOS})
    for linha in linhas:
        if linha["origem"] != "simulado":
            raise ValueError(f"{caminho}: evento sem origem='simulado'")
        try:
            ano, semana, _ = date.fromisoformat(linha["data_hora"][:10]).isocalendar()
        except ValueError as erro:
            raise ValueError(
                f"{caminho}: data_hora inválida: {linha['data_hora']!r}"
            ) from erro
        if linha["tipo"] not in ("alerta", "denuncia"):
            raise ValueError(f"{caminho}: tipo inválido: {linha['tipo']!r}")
        if linha["status"] not in ("atendido", "cancelado", "em_aberto"):
            raise ValueError(f"{caminho}: status inválido: {linha['status']!r}")
        chave = (linha["distrito"], f"{ano}-W{semana:02d}")
        categoria = "alertas" if linha["tipo"] == "alerta" else "denuncias"
        sufixo_status = {
            "atendido": "atendidos" if categoria == "alertas" else "atendidas",
            "cancelado": "cancelados" if categoria == "alertas" else "canceladas",
            "em_aberto": "em_aberto",
        }[linha["status"]]
        agregados[chave][f"total_{categoria}"] += 1
        agregados[chave][f"{categoria}_{sufixo_status}"] += 1

    for chave, valores in agregados.items():
        dados[chave].update(valores)
        dados[chave]["origem_violencia"] = "simulado"


def montar_dataset(diretorio=DIRETORIO_DADOS, saida=None):
    """Monta o CSV consolidado somente com fontes disponíveis."""
    diretorio = Path(diretorio)
    dados = defaultdict(dict)
    for modulo, (nome_arquivo, coluna, grupo) in FONTES_REAIS.items():
        _adicionar_fonte_real(dados, diretorio, modulo, nome_arquivo, coluna, grupo)
    _adicionar_eventos_simulados(dados, diretorio)

    colunas = ["distrito", "semana"]
    for _, (_, coluna, grupo) in FONTES_REAIS.items():
        if any(coluna in valores for valores in dados.values()):
            colunas.append(coluna)
            nome_origem = f"origem_{grupo}"
            if nome_origem not in colunas:
                colunas.append(nome_origem)
    if any("origem_violencia" in valores for valores in dados.values()):
        colunas.extend(COLUNAS_EVENTOS)
        colunas.append("origem_violencia")

    caminho_saida = Path(saida) if saida else diretorio / "aviva_dataset.csv"
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)
    with caminho_saida.open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=colunas)
        escritor.writeheader()
        for (distrito, semana), valores in sorted(dados.items()):
            escritor.writerow({"distrito": distrito, "semana": semana, **valores})
    return caminho_saida


def montar_dataset_clima(diretorio=Path(__file__).resolve().parents[1] / "data" / "raw", saida=None):
    """Gera o dataset diário de clima real com defasagens e rótulo futuro."""
    return montar_aviva_clima_diario(diretorio, saida)


def main():
    """Executa a montagem com caminhos opcionais."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dados", type=Path)
    parser.add_argument("--saida", type=Path)
    parser.add_argument("--tipo", choices=("clima", "semanal"), default="clima")
    argumentos = parser.parse_args()

    if argumentos.tipo == "clima":
        diretorio = argumentos.dados or ROOT / "data" / "raw"
        caminho = montar_dataset_clima(diretorio, argumentos.saida)
        print(f"Dataset climático montado em: {caminho}")
        return

    diretorio = argumentos.dados or DIRETORIO_DADOS
    caminho = montar_dataset(diretorio, argumentos.saida)
    print(f"Dataset semanal montado em: {caminho}")


if __name__ == "__main__":
    main()
