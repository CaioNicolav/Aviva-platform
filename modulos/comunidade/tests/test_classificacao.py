"""Testes das regras de classificacao."""

import pytest

from aviva.classificacao import classificar, nivel_da_variavel


@pytest.mark.parametrize(
    "variavel,valor,nivel",
    [
        ("nivel_agua_cm", 119, 0),
        ("nivel_agua_cm", 120, 1),
        ("nivel_agua_cm", 200, 2),
        ("chuva_mm_h", 24, 0),
        ("chuva_mm_h", 25, 1),
        ("chuva_mm_h", 50, 2),
    ],
)
def test_nivel_da_variavel(variavel, valor, nivel):
    assert nivel_da_variavel(variavel, valor) == nivel


@pytest.mark.parametrize(
    "leituras,nivel",
    [
        ({"nivel_agua_cm": 40, "chuva_mm_h": 5}, "NORMAL"),
        ({"nivel_agua_cm": 130, "chuva_mm_h": 10}, "ATENÇÃO"),
        ({"nivel_agua_cm": 150, "chuva_mm_h": 30}, "CRÍTICO"),
        ({"nivel_agua_cm": 220, "chuva_mm_h": 60}, "CRÍTICO"),
    ],
)
def test_classificar_cenarios(leituras, nivel):
    assert classificar(leituras)[0] == nivel


def test_classificar_eleva_risco_combinado():
    nivel, detalhes = classificar({"nivel_agua_cm": 150, "chuva_mm_h": 30})
    assert nivel == "CRÍTICO"
    assert detalhes == {"nivel_agua_cm": 1, "chuva_mm_h": 1}
