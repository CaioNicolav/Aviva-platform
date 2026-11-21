"""Exercita o monitor com diferentes combinações de nível de água e chuva.

Os testes asseguram a classificação esperada e o tratamento do histórico."""

import pytest

from aviva.monitor import MonitorRisco


@pytest.mark.parametrize(
    "local,leituras,nivel",
    [
        ("A1", {"nivel_agua_cm": 40, "chuva_mm_h": 5}, "NORMAL"),
        ("B2", {"nivel_agua_cm": 130, "chuva_mm_h": 10}, "ATENÇÃO"),
        ("C3", {"nivel_agua_cm": 150, "chuva_mm_h": 30}, "CRÍTICO"),
        ("D4", {"nivel_agua_cm": 220, "chuva_mm_h": 60}, "CRÍTICO"),
    ],
)
def test_monitor_avalia_quatro_cenarios(local, leituras, nivel):
    monitor = MonitorRisco()
    resultado = monitor.avaliar(local, leituras)

    assert resultado["ok"] is True
    assert resultado["nivel"] == nivel
    assert len(resultado["recomendacoes"]) > 0
    assert monitor.resumo_historico()[nivel] == 1


@pytest.mark.parametrize(
    "local,leituras",
    [
        ("A1", {"nivel_agua_cm": "abc", "chuva_mm_h": 10}),
        ("A1", {"nivel_agua_cm": -5, "chuva_mm_h": 10}),
        ("A1", {"nivel_agua_cm": 999, "chuva_mm_h": 10}),
        ("A1", {"nivel_agua_cm": "", "chuva_mm_h": 10}),
        ("A1", {"nivel_agua_cm": "nan", "chuva_mm_h": 10}),
        ("; DROP TABLE", {"nivel_agua_cm": 50, "chuva_mm_h": 5}),
    ],
)
def test_monitor_rejeita_seis_entradas_invalidas_sem_historico(local, leituras):
    monitor = MonitorRisco()

    resultado = monitor.avaliar(local, leituras)

    assert resultado["ok"] is False
    assert resultado["erros"]
    assert monitor.resumo_historico() == {
        "NORMAL": 0,
        "ATENÇÃO": 0,
        "CRÍTICO": 0,
    }
