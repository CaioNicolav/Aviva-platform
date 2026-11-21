# Riscos de segurança e privacidade – AVIVA

Escopo: o que existe hoje (programa Python local, entrada digitada ou simulada, histórico em memória). Não há rede, banco de dados, sensores reais, nuvem ou autenticação. Riscos desses componentes serão avaliados quando forem implementados.

## Mapa de riscos

| # | Risco | Impacto | Prevenção aplicada | Onde no código |
|---|---|---|---|---|
| R1 | **Entrada inválida ou manipulada**: valor ausente, texto no lugar de número, NaN/infinito ou fora da faixa física do sensor | Classificação errada (um alerta crítico deixa de ser emitido ou um falso alarme é gerado) e falhas no programa | Conversão controlada para número, rejeição de ausente, formato inválido, não numérico e fora da faixa; a entrada rejeitada nunca chega à classificação | `aviva/validacao.py` (`validar_numero`) |
| R2 | **Texto livre no campo de local**: tentativa de injetar comandos, SQL ou dados pessoais (nome, contato) | Se o dado fosse usado depois em banco, arquivo ou página, abriria porta para injeção; dado pessoal seria armazenado sem necessidade | Lista permitida (allowlist): só código anônimo com letras, números, `-` e `_`, até 20 caracteres | `aviva/validacao.py` (`validar_local`) |
| R3 | **Confiança excessiva na classificação**: usuário toma decisão crítica só pelo resultado automático, ou limites provisórios geram classificação incorreta | Decisão errada em situação de risco real | Aviso fixo em toda saída de que a classificação é apoio à decisão e não substitui serviços oficiais; limites documentados como provisórios; telefones oficiais no nível CRÍTICO | `aviva/config.py` (`AVISO`, `RECOMENDACOES`), `docs/limites-provisorios.md` |
| R4 | **Vazamento ou uso indevido do histórico de alertas**: dados de eventos são usados para identificar, vigiar ou discriminar pessoas/grupos | Exposição de situações sensíveis, estigmatização territorial ou dano a pessoas | Nesta fase não há usuárias reais; os eventos são simulados e não incluem dados pessoais. Manter agregação por semana/distrito, limitar acesso caso haja persistência futura e não reutilizar para decisão individual | `scripts/gerar_eventos_simulados.py`, `scripts/montar_dataset.py` |
| R5 | **Alerta falso, spam ou replay**: repetição ou geração indevida de alertas pode sobrecarregar quem atende e reduzir confiança | Resposta desviada, demora em alertas legítimos ou confiança indevida em eventos forjados | Os alertas atuais são apenas sintéticos e não são enviados a serviços externos. Antes de qualquer integração futura, exigir autenticação, proteção contra repetição/idempotência, limites de frequência e procedimento de validação/encaminhamento | Evolução futura do módulo de alertas |
| R6 | **Reidentificação em distrito com poucos eventos**: uma contagem pequena, combinada com contexto externo, pode revelar quem acionou o sistema | Exposição de pessoas e de situações sensíveis | Não gerar registros de pessoas; em rankings, mostrar “dados insuficientes” abaixo de `MINIMO_EVENTOS_RANKING` (padrão 5), agregar períodos e evitar publicar linhas individuais. O limite não é garantia de anonimização | `aviva/config.py` (`MINIMO_EVENTOS_RANKING`), `aviva/apresentacao.py` |

## Limitações conhecidas (não tratadas hoje)

- Não há autenticação nem controle de acesso: qualquer pessoa com acesso ao programa o usa.
- O histórico fica só em memória e se perde ao encerrar; não há criptografia porque não há persistência.
- Não há registro (log) de eventos de segurança.
- Os limites numéricos são provisórios e não vêm de fonte oficial de IoT/AICSS.
- Os eventos de violência são sintéticos; não há integração real com polícia, botão de pânico, sensores ou nuvem.

## Evolução futura (quando houver os componentes)

- Autenticação e autorização se houver API ou interface web.
- Segredos fora do código (variáveis de ambiente, `.env` já ignorado pelo Git).
- Validação do lado do servidor, limite de requisições e logs de auditoria.
- Minimização e anonimização de dados caso entrem dados de pessoas (LGPD).
- Revisão de riscos específicos de sensores IoT (integridade da leitura, dispositivo falso) após receber o PDF de IoT/AICSS.
