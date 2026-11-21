"""Centraliza parâmetros do monitor de risco comunitário.

As faixas de nível e chuva são experimentais e servem para simulação.
Não representam critérios oficiais nem medições de sensores reais."""

LIMITES = {
    "nivel_agua_cm": {
        "rotulo": "Nível da água",
        "unidade": "cm",
        "min": 0,
        "max": 300,
        "atencao": 120,
        "critico": 200,
    },
    "chuva_mm_h": {
        "rotulo": "Intensidade da chuva",
        "unidade": "mm/h",
        "min": 0,
        "max": 200,
        "atencao": 25,
        "critico": 50,
    },
}

NIVEIS = ["NORMAL", "ATENÇÃO", "CRÍTICO"]

MINIMO_EVENTOS_RANKING = 5

RECOMENDACOES = {
    "NORMAL": [
        "Condição estável. Manter o acompanhamento regular.",
    ],
    "ATENÇÃO": [
        "Evitar áreas baixas e próximas a córregos.",
        "Separar documentos e itens essenciais em local alto.",
        "Acompanhar novas leituras com frequência.",
    ],
    "CRÍTICO": [
        "Priorizar a segurança: deixar áreas de risco se necessário.",
        "Defesa Civil: 199 | Bombeiros: 193 | SAMU: 192.",
        "Avisar vizinhos, idosos e pessoas com dificuldade de locomoção.",
    ],
}

AVISO = (
    "Aviso: classificação automática é apoio à decisão e não substitui "
    "serviços públicos, profissionais ou protocolos oficiais."
)
