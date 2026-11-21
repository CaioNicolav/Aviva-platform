# Testes de segurança – AVIVA

Como reproduzir: `python -m aviva --demo` (bloco "TESTES DE ENTRADAS INVÁLIDAS") e `pytest`.
Todos os dados são simulados. Base de comparação: uma leitura válida de referência é `nivel_agua_cm = 40`, `chuva_mm_h = 5`, local `A1`.

## Tabela de testes

| ID | Risco | Entrada | Resultado esperado | Proteção | Resultado observado |
|---|---|---|---|---|---|
| T1 | R1 | Nível da água = `abc` (chuva = 10, local `A1`) | Rejeitar sem classificar | Conversão para número com tratamento de erro | Rejeitada: "Nível da água: formato inválido ('abc')." |
| T2 | R1 | Nível da água = `-5` | Rejeitar (abaixo da faixa 0–300 cm) | Verificação de faixa mínima | Rejeitada: "-5.0 fora da faixa permitida (0 a 300 cm)." |
| T3 | R1 | Nível da água = `999` | Rejeitar (acima da faixa 0–300 cm) | Verificação de faixa máxima | Rejeitada: "999.0 fora da faixa permitida (0 a 300 cm)." |
| T4 | R1 | Nível da água = `` (vazio) | Rejeitar | Verificação de valor ausente | Rejeitada: "Nível da água: valor ausente." |
| T5 | R1 | Nível da água = `nan` | Rejeitar | Verificação de NaN/infinito | Rejeitada: "Nível da água: valor não numérico." |
| T6 | R2 | Local = `Maria; DROP TABLE` | Rejeitar | Allowlist de caracteres do código do local | Rejeitada: "Código do local inválido (use até 20 letras, números, - ou _)." |

Em T1 a T5 apenas o campo testado foi rejeitado e em T6 apenas o local, o que confirma que cada validação age sobre o campo certo. Nenhuma entrada rejeitada entrou no histórico: o resumo final do demo ficou em `{'NORMAL': 1, 'ATENÇÃO': 1, 'CRÍTICO': 2}`, igual ao dos quatro cenários válidos.

## Teste do risco R3 (confiança excessiva)

| ID | Risco | Entrada | Resultado esperado | Proteção | Resultado observado |
|---|---|---|---|---|---|
| T7 | R3 | Qualquer entrada válida (ex.: cenário D4: 220 cm e 60 mm/h) | Toda saída válida traz o aviso e, em CRÍTICO, os telefones oficiais | `AVISO` e `RECOMENDACOES` | Aviso exibido nos 4 cenários; CRÍTICO (C3 e D4) mostrou Defesa Civil 199, Bombeiros 193 e SAMU 192 |

## Lacunas a cobrir

- Valor infinito (`inf`) e outros formatos numéricos (vírgula decimal, notação científica) estão tratados no código, mas não aparecem no demo. Convém acrescentar casos em `tests/test_validacao.py` e incluir o resultado nesta tabela.
- Não foram testados: entradas muito longas no código do local (mais de 20 caracteres), espaços e acentos no local. A regra deve rejeitá-los; falta registrar o teste.
- Testes de segurança de rede, autenticação e sensores só fazem sentido quando esses componentes existirem.
