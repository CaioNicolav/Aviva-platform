"""Valida a presença do arquivo original de nível de rio."""

from pathlib import Path


ARQUIVO_RAW = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "raw"
    / "ana_cemaden_nivel_rio.csv"
)
FONTE = "ANA/CEMADEN — nível de rio"


def ingestir(caminho=ARQUIVO_RAW):
    """Exige o arquivo real antes de definir seu parser."""
    caminho = Path(caminho)
    if not caminho.is_file():
        raise FileNotFoundError(
            f"Fonte {FONTE} ausente. Baixe o arquivo e coloque-o em: {caminho}"
        )
    raise NotImplementedError(
        f"Formato de {caminho} ainda não foi inspecionado; "
        "verifique cabeçalho, separador, decimal, codificação e metadados antes "
        "de implementar o parser."
    )


if __name__ == "__main__":
    try:
        ingestir()
    except (FileNotFoundError, NotImplementedError) as erro:
        raise SystemExit(str(erro)) from erro
