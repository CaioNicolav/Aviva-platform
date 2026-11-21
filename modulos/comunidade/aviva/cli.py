"""Disponibiliza a interface de terminal do monitor AVIVA.

O fluxo interativo coleta leituras, executa a avaliação e permite
consultar os resultados durante a sessão."""

import sys

from aviva.apresentacao import mostrar_resultado
from aviva.config import LIMITES
from aviva.monitor import MonitorRisco
from aviva.validacao import validar_numero


def modo_demo():
    monitor = MonitorRisco()

    print(" CENÁRIOS DE TESTE (dados simulados) ")
    cenarios = [
        ("A1", {"nivel_agua_cm": 40, "chuva_mm_h": 5}),
        ("B2", {"nivel_agua_cm": 130, "chuva_mm_h": 10}),
        ("C3", {"nivel_agua_cm": 150, "chuva_mm_h": 30}),
        ("D4", {"nivel_agua_cm": 220, "chuva_mm_h": 60}),
    ]
    for local, entradas in cenarios:
        mostrar_resultado(monitor.avaliar(local, entradas))

    print("\n=== TESTES DE ENTRADAS INVÁLIDAS ===")
    invalidos = [
        ("A1", {"nivel_agua_cm": "abc", "chuva_mm_h": 10}),
        ("A1", {"nivel_agua_cm": -5, "chuva_mm_h": 10}),
        ("A1", {"nivel_agua_cm": 999, "chuva_mm_h": 10}),
        ("A1", {"nivel_agua_cm": "", "chuva_mm_h": 10}),
        ("A1", {"nivel_agua_cm": "nan", "chuva_mm_h": 10}),
        ("A1", {"nivel_agua_cm": "inf", "chuva_mm_h": 10}),
        ("; DROP TABLE", {"nivel_agua_cm": 50, "chuva_mm_h": 5}),
        ("A" * 21, {"nivel_agua_cm": 50, "chuva_mm_h": 5}),
        ("LOCAL 1", {"nivel_agua_cm": 50, "chuva_mm_h": 5}),
        ("SãoPaulo", {"nivel_agua_cm": 50, "chuva_mm_h": 5}),
    ]
    for local, entradas in invalidos:
        mostrar_resultado(monitor.avaliar(local, entradas))

    print("-" * 56)
    print("Resumo do histórico válido:", monitor.resumo_historico())


def pedir_valor(variavel):
    """Pergunta ate tres vezes e devolve o texto digitado."""
    cfg = LIMITES[variavel]
    texto = ""
    for _ in range(3):
        texto = input(f"{cfg['rotulo']} ({cfg['unidade']}): ")
        _, erro = validar_numero(variavel, texto)
        if erro is None:
            return texto
        print(f"{erro}")
    return texto


def modo_interativo():
    """Executa o monitor ate o usuario encerrar a sessao."""
    monitor = MonitorRisco()
    print("AVIVA - Monitor de risco (cenário provisório de alagamento)")
    print("Digite 'sair' no código do local para encerrar.\n")
    while True:
        local = input("Código do local (ex.: ZN-01): ")
        if local.strip().lower() == "sair":
            break
        entradas = {variavel: pedir_valor(variavel) for variavel in LIMITES}
        mostrar_resultado(monitor.avaliar(local, entradas))
        print()
    print("Resumo da sessão:", monitor.resumo_historico())


def main():
    """Seleciona o modo de execucao solicitado."""
    if "--demo" in sys.argv:
        modo_demo()
    else:
        modo_interativo()
