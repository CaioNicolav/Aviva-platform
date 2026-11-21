"""Valida identificadores de local e valores numéricos enviados ao monitor.

A verificação recusa dados ausentes, números inválidos e medidas fora
das faixas definidas na configuração."""

import math
import re

from aviva.config import LIMITES


def validar_local(texto):
    """Aceita apenas um codigo anonimo de local."""
    texto = str(texto).strip()
    if not texto:
        return None, "Código do local ausente."
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,20}", texto):
        return None, "Código do local inválido (use até 20 letras, números, - ou _)."
    return texto, None


def validar_numero(variavel, valor_bruto):
    """Converte para float e confere ausencia, formato e limites."""
    cfg = LIMITES[variavel]
    texto = str(valor_bruto).strip().replace(",", ".")
    if texto == "":
        return None, f"{cfg['rotulo']}: valor ausente."
    try:
        valor = float(texto)
    except ValueError:
        return None, f"{cfg['rotulo']}: formato inválido ('{texto}')."
    if math.isnan(valor) or math.isinf(valor):
        return None, f"{cfg['rotulo']}: valor não numérico."
    if valor < cfg["min"] or valor > cfg["max"]:
        return None, (
            f"{cfg['rotulo']}: {valor} fora da faixa permitida "
            f"({cfg['min']} a {cfg['max']} {cfg['unidade']})."
        )
    return valor, None
