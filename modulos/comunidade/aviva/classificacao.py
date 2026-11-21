"""Regras provisorias de classificacao."""

from aviva.config import LIMITES, NIVEIS


def nivel_da_variavel(variavel, valor):
    """Retorna o indice NORMAL, ATENCAO ou CRITICO."""
    cfg = LIMITES[variavel]
    if valor >= cfg["critico"]:
        return 2
    elif valor >= cfg["atencao"]:
        return 1
    return 0


def classificar(leituras):
    """Classifica pelo pior nivel e aplica a regra de risco combinado."""
    detalhes = {}
    for variavel, valor in leituras.items():
        detalhes[variavel] = nivel_da_variavel(variavel, valor)

    pior = max(detalhes.values())
    todas_em_alerta = all(n >= 1 for n in detalhes.values())
    if todas_em_alerta and pior < 2:
        pior = 2
    return NIVEIS[pior], detalhes
