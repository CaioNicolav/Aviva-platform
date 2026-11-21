"""Valida formatos de códigos locais e limites das entradas numéricas.

Cobre dados aceitos e rejeitados pelo módulo de monitoramento."""

import pytest

from aviva.validacao import validar_local, validar_numero


@pytest.mark.parametrize(
    "entrada,esperado",
    [
        ("ZN-01", "ZN-01"),
        ("  zona_2  ", "zona_2"),
        ("A" * 20, "A" * 20),
    ],
)
def test_validar_local_aceita_codigo_anonimo(entrada, esperado):
    assert validar_local(entrada) == (esperado, None)


@pytest.mark.parametrize(
    "entrada,mensagem",
    [
        ("", "Código do local ausente."),
        ("; DROP TABLE", "Código do local inválido (use até 20 letras, números, - ou _)."),
        ("A" * 21, "Código do local inválido (use até 20 letras, números, - ou _)."),
        ("LOCAL 1", "Código do local inválido (use até 20 letras, números, - ou _)."),
        ("SãoPaulo", "Código do local inválido (use até 20 letras, números, - ou _)."),
    ],
)
def test_validar_local_rejeita_codigo_invalido(entrada, mensagem):
    assert validar_local(entrada) == (None, mensagem)


@pytest.mark.parametrize(
    "variavel,entrada,esperado",
    [
        ("nivel_agua_cm", "12,5", 12.5),
        ("nivel_agua_cm", "1.25e1", 12.5),
        ("chuva_mm_h", "25", 25.0),
        ("nivel_agua_cm", "0", 0.0),
        ("chuva_mm_h", "200", 200.0),
    ],
)
def test_validar_numero_aceita_valores_na_faixa(variavel, entrada, esperado):
    assert validar_numero(variavel, entrada) == (esperado, None)


@pytest.mark.parametrize(
    "entrada,mensagem",
    [
        ("", "Nível da água: valor ausente."),
        ("abc", "Nível da água: formato inválido ('abc')."),
        ("-5", "Nível da água: -5.0 fora da faixa permitida (0 a 300 cm)."),
        ("999", "Nível da água: 999.0 fora da faixa permitida (0 a 300 cm)."),
        ("nan", "Nível da água: valor não numérico."),
        ("inf", "Nível da água: valor não numérico."),
        ("-inf", "Nível da água: valor não numérico."),
    ],
)
def test_validar_numero_rejeita_entradas_invalidas(entrada, mensagem):
    assert validar_numero("nivel_agua_cm", entrada) == (None, mensagem)
