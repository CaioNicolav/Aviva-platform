"""Coordena a validação, classificação e apresentação lógica do monitor.

MonitorRisco mantém o histórico da sessão e devolve uma estrutura
com leituras, classificação, recomendações e eventuais erros."""

from aviva.classificacao import classificar
from aviva.config import LIMITES, NIVEIS, RECOMENDACOES
from aviva.validacao import validar_local, validar_numero


class MonitorRisco:
    """Guarda o historico de avaliacoes e gera resultados."""

    def __init__(self):
        self.historico = []

    def avaliar(self, local_bruto, entradas_brutas):
        """Valida as entradas e, se estiverem corretas, classifica."""
        erros = []
        local, erro = validar_local(local_bruto)
        if erro:
            erros.append(erro)

        leituras = {}
        for variavel in LIMITES:
            valor, erro = validar_numero(
                variavel, entradas_brutas.get(variavel, "")
            )
            if erro:
                erros.append(erro)
            else:
                leituras[variavel] = valor

        if erros:
            return {"ok": False, "erros": erros}

        nivel, detalhes = classificar(leituras)
        resultado = {
            "ok": True,
            "local": local,
            "leituras": leituras,
            "detalhes": {v: NIVEIS[n] for v, n in detalhes.items()},
            "nivel": nivel,
            "recomendacoes": RECOMENDACOES[nivel],
        }
        self.historico.append(resultado)
        return resultado

    def resumo_historico(self):
        """Conta as avaliacoes validas em cada nivel."""
        contagem = {nome: 0 for nome in NIVEIS}
        for item in self.historico:
            contagem[item["nivel"]] += 1
        return contagem
