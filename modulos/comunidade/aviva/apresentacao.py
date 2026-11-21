"""Formata os resultados do monitor de risco no terminal.

Oculta indicadores de grupos com poucos eventos e apresenta avisos
quando a validação rejeita uma entrada."""

from aviva.config import AVISO, LIMITES, MINIMO_EVENTOS_RANKING


def proteger_valor_ranking(valor, quantidade_eventos):
    """Oculta valores de grupos com poucos eventos."""
    if quantidade_eventos < MINIMO_EVENTOS_RANKING:
        return "dados insuficientes"
    return valor


def mostrar_resultado(resultado):
    """Imprime uma avaliacao ou os erros de entrada."""
    print("-" * 56)
    if not resultado["ok"]:
        print("ENTRADA REJEITADA:")
        for erro in resultado["erros"]:
            print(f"  x {erro}")
        return

    print(f"Local: {resultado['local']}")
    for variavel, valor in resultado["leituras"].items():
        cfg = LIMITES[variavel]
        nivel_var = resultado["detalhes"][variavel]
        print(f"  {cfg['rotulo']}: {valor:g} {cfg['unidade']} -> {nivel_var}")
    print(f"CLASSIFICAÇÃO: {resultado['nivel']}")
    for rec in resultado["recomendacoes"]:
        print(f"  - {rec}")
    print(AVISO)
