"""Gera um conjunto reprodutível de eventos comunitários sintéticos.

A semente fixa, as regras de distribuição temporal e os identificadores
permitem testar agregações sem utilizar relatos pessoais reais."""

import csv
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path


SEMENTE = 20261107
QUANTIDADE_EVENTOS = 4000
CODIGOS_DISTRITO = tuple(f"D{numero:02d}" for numero in range(1, 21))
INICIO_SIMULACAO = datetime(2026, 1, 1)
FIM_SIMULACAO = datetime(2026, 10, 31, 23, 0)
DURACAO_DIAS = (FIM_SIMULACAO - INICIO_SIMULACAO).days + 1
FRACAO_ALERTAS_CANCELADOS = 0.2
PESO_NOITE = 2.0
PESO_FIM_DE_SEMANA = 1.5
RUIDO = 0.2
INICIO_ULTIMA_SEMANA = FIM_SIMULACAO.replace(hour=0, minute=0) - timedelta(days=6)
ARQUIVO_SAIDA = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "processed"
    / "eventos_violencia_simulados.csv"
)
CAMPOS = (
    "id_evento",
    "tipo",
    "distrito",
    "data_hora",
    "status",
    "origem",
)


def _criar_horas(rng):
    """Cria horas candidatas com sazonalidade inteiramente simulada."""
    horas = []
    pesos = []
    inicio = INICIO_SIMULACAO.replace(minute=0, second=0, microsecond=0)
    for deslocamento in range(DURACAO_DIAS * 24):
        hora = inicio + timedelta(hours=deslocamento)
        peso = PESO_NOITE if hora.hour >= 20 or hora.hour < 6 else 1.0
        if hora.weekday() >= 5:
            peso *= PESO_FIM_DE_SEMANA
        peso *= rng.uniform(1 - RUIDO, 1 + RUIDO)
        horas.append(hora)
        pesos.append(peso)
    return horas, pesos


def gerar_eventos(semente=SEMENTE, quantidade=QUANTIDADE_EVENTOS):
    """Gera eventos com campos sintéticos, sem expor dados pessoais e sem abrir eventos antigos."""
    rng = random.Random(semente)
    distritos = list(CODIGOS_DISTRITO)
    pesos_distrito = [rng.uniform(0.5, 1.5) for _ in distritos]
    horas, pesos_hora = _criar_horas(rng)
    eventos = []

    for _ in range(quantidade):
        tipo = rng.choices(("alerta", "denuncia"), weights=(0.7, 0.3))[0]
        data_hora = rng.choices(horas, weights=pesos_hora)[0]
        if data_hora < INICIO_ULTIMA_SEMANA:
            status = rng.choice(("atendido", "cancelado"))
        elif tipo == "alerta":
            sorteio_status = rng.random()
            if sorteio_status < FRACAO_ALERTAS_CANCELADOS:
                status = "cancelado"
            elif sorteio_status < 0.9:
                status = "atendido"
            else:
                status = "em_aberto"
        else:
            status = rng.choices(("atendido", "em_aberto"), weights=(0.9, 0.1))[0]

        eventos.append(
            {
                "id_evento": str(uuid.uuid4()),
                "tipo": tipo,
                "distrito": rng.choices(distritos, weights=pesos_distrito)[0],
                "data_hora": data_hora.isoformat(),
                "status": status,
                "origem": "simulado",
            }
        )
    return eventos


def gravar_eventos(caminho=ARQUIVO_SAIDA, semente=SEMENTE, quantidade=QUANTIDADE_EVENTOS):
    """Grava eventos sintéticos em CSV."""
    eventos = gerar_eventos(semente, quantidade)
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS)
        escritor.writeheader()
        escritor.writerows(eventos)
    return eventos


if __name__ == "__main__":
    gravar_eventos()
