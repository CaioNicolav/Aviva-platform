"""Verifica a saída textual reproduzível do modo de demonstração.

A execução em subprocesso compara o relatório impresso com cenários conhecidos."""

import subprocess
import sys


def test_demo_preserva_saida_esperada():
    resultado = subprocess.run(
        [sys.executable, "-m", "aviva", "--demo"],
        check=True,
        capture_output=True,
        text=True,
    )
    esperado = (
        " CENÁRIOS DE TESTE (dados simulados) \n"
       """--------------------------------------------------------
Local: A1
  Nível da água: 40 cm -> NORMAL
  Intensidade da chuva: 5 mm/h -> NORMAL
CLASSIFICAÇÃO: NORMAL
  - Condição estável. Manter o acompanhamento regular.
Aviso: classificação automática é apoio à decisão e não substitui serviços públicos, profissionais ou protocolos oficiais.
--------------------------------------------------------
Local: B2
  Nível da água: 130 cm -> ATENÇÃO
  Intensidade da chuva: 10 mm/h -> NORMAL
CLASSIFICAÇÃO: ATENÇÃO
  - Evitar áreas baixas e próximas a córregos.
  - Separar documentos e itens essenciais em local alto.
  - Acompanhar novas leituras com frequência.
Aviso: classificação automática é apoio à decisão e não substitui serviços públicos, profissionais ou protocolos oficiais.
--------------------------------------------------------
Local: C3
  Nível da água: 150 cm -> ATENÇÃO
  Intensidade da chuva: 30 mm/h -> ATENÇÃO
CLASSIFICAÇÃO: CRÍTICO
  - Priorizar a segurança: deixar áreas de risco se necessário.
  - Defesa Civil: 199 | Bombeiros: 193 | SAMU: 192.
  - Avisar vizinhos, idosos e pessoas com dificuldade de locomoção.
Aviso: classificação automática é apoio à decisão e não substitui serviços públicos, profissionais ou protocolos oficiais.
--------------------------------------------------------
Local: D4
  Nível da água: 220 cm -> CRÍTICO
  Intensidade da chuva: 60 mm/h -> CRÍTICO
CLASSIFICAÇÃO: CRÍTICO
  - Priorizar a segurança: deixar áreas de risco se necessário.
  - Defesa Civil: 199 | Bombeiros: 193 | SAMU: 192.
  - Avisar vizinhos, idosos e pessoas com dificuldade de locomoção.
Aviso: classificação automática é apoio à decisão e não substitui serviços públicos, profissionais ou protocolos oficiais.

=== TESTES DE ENTRADAS INVÁLIDAS ===
--------------------------------------------------------
ENTRADA REJEITADA:
  x Nível da água: formato inválido ('abc').
--------------------------------------------------------
ENTRADA REJEITADA:
  x Nível da água: -5.0 fora da faixa permitida (0 a 300 cm).
--------------------------------------------------------
ENTRADA REJEITADA:
  x Nível da água: 999.0 fora da faixa permitida (0 a 300 cm).
--------------------------------------------------------
ENTRADA REJEITADA:
  x Nível da água: valor ausente.
--------------------------------------------------------
ENTRADA REJEITADA:
  x Nível da água: valor não numérico.
--------------------------------------------------------
ENTRADA REJEITADA:
  x Nível da água: valor não numérico.
--------------------------------------------------------
ENTRADA REJEITADA:
  x Código do local inválido (use até 20 letras, números, - ou _).
--------------------------------------------------------
ENTRADA REJEITADA:
  x Código do local inválido (use até 20 letras, números, - ou _).
--------------------------------------------------------
ENTRADA REJEITADA:
  x Código do local inválido (use até 20 letras, números, - ou _).
--------------------------------------------------------
ENTRADA REJEITADA:
  x Código do local inválido (use até 20 letras, números, - ou _).
--------------------------------------------------------
Resumo do histórico válido: {'NORMAL': 1, 'ATENÇÃO': 1, 'CRÍTICO': 2}
"""
    )
    assert resultado.stdout == esperado
