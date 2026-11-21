# AVIVA — Estrutura de telas e textos finais (módulo Saúde e Reabilitação)

## Objetivo
O módulo ajuda o cidadão a compreender serviços públicos de saúde e reabilitação e a conhecer caminhos gerais de acesso ao SUS. **Não diagnostica, não prescreve próteses e não garante horários, vagas, habilitações ou acesso direto a serviços especializados.**

## Tela 1 — Encontrar serviços
- Filtros atuais: categoria, zona e bairro em São Paulo; mapa, lista e proximidade.
- Botões: pesquisar, usar localização com autorização, marcar ponto no mapa e encontrar os cinco mais próximos.
- Aviso fixo: “Resultados exploratórios do CNES. A presença no cadastro não confirma a oferta de reabilitação ou vaga.”
- **Limitação atual:** UBS são descritas no guia de serviços, mas não são pins importados na busca do AVIVA 0.5. Antes de adicioná-las, validar a classificação, geografia e o acesso pela rede de referência.

## Tela 2 — Entender os serviços

### UBS — Unidade Básica de Saúde
**O que é:** É um lugar para receber cuidados de saúde perto de casa, esclarecer dúvidas e iniciar o acompanhamento.
**O que pode oferecer:** Atendimento inicial, acompanhamento de saúde, orientações e encaminhamento para outros serviços quando necessário. Algumas UBS também oferecem ações de reabilitação ou apoio de equipes multiprofissionais.
**Quando procurar:** Quando não sabe qual atendimento precisa, percebe dificuldade persistente ou quer orientação para buscar reabilitação.
**Atenção:** Nem toda UBS oferece fisioterapia, terapia ocupacional ou outros atendimentos especializados no próprio local.

### CER — Centro Especializado em Reabilitação
**O que é:** Um serviço para pessoas que precisam de acompanhamento especializado para desenvolver ou recuperar habilidades e autonomia.
**O que pode oferecer:** Avaliação e reabilitação física, auditiva, visual e/ou intelectual, conforme as modalidades habilitadas.
**Como procurar:** Em geral, pela avaliação e orientação da rede de saúde, que pode organizar encaminhamento quando necessário.
**Atenção:** Reabilitação cognitiva não é uma quinta modalidade oficial de CER e pode envolver diferentes serviços.

### CAPS — Centro de Atenção Psicossocial
**O que é:** Um serviço de saúde mental para pessoas com sofrimento psíquico intenso e outras necessidades psicossociais.
**O que pode oferecer:** Acolhimento, acompanhamento multiprofissional, grupos e cuidados relacionados a álcool e outras drogas, segundo o tipo de CAPS.
**Como procurar:** É possível buscar o CAPS diretamente para o primeiro acolhimento, sem encaminhamento ou agendamento obrigatório.
**Atenção:** A equipe avalia o cuidado indicado; nem todo acolhimento resulta em acompanhamento continuado no CAPS.

### Oficina Ortopédica
**O que é:** Um serviço que trabalha com recursos que ajudam a pessoa a ter mais autonomia.
**O que pode oferecer:** Confecção, fornecimento, adaptação e manutenção de órteses, próteses e meios auxiliares de locomoção, conforme o serviço.
**Como procurar:** Em geral, após avaliação e indicação da equipe de saúde responsável.
**Atenção:** A escolha do dispositivo requer avaliação individualizada e não é um catálogo de produtos para compra direta.

## Tela 3 — Como funciona o atendimento
Fluxo geral em linguagem simples, sem indicar um estabelecimento específico.

1. **Percebi uma dificuldade:** andar, ouvir, enxergar, falar, lembrar ou realizar tarefas ficou difícil.
2. **Busco orientação:** posso procurar uma UBS para conversar e conhecer os caminhos do SUS.
3. **Recebo uma avaliação:** a equipe escuta, avalia e explica as possibilidades de cuidado.
4. **Sou encaminhado, quando necessário:** posso receber orientação para CER, serviço especializado ou oficina ortopédica.
5. **Começo o cuidado indicado:** posso receber acompanhamento, reabilitação, orientações ou recursos assistivos quando apropriados.
6. **Continuo meu acompanhamento:** posso ter retornos, reavaliações e apoio de diferentes serviços.

**Exceção importante:** CAPS é serviço de porta aberta e permite procura direta para primeiro acolhimento. **Urgência:** em situação de emergência, procure UPA/pronto-socorro ou SAMU 192, em vez de aguardar o fluxo rotineiro.

## Jornada e navegação
- Visão geral → Buscar serviços → mapa ou lista → informações da unidade e aviso de validação.
- Visão geral → Entender os serviços → UBS, CER, CAPS e Oficina → Como funciona.
- Visão geral → Como funciona → Buscar serviços.
- Tecnologia assistiva permanece como seção educativa existente.

## Integração futura ao app principal
Módulo independente FastAPI; os endpoints de conteúdo educativo são JSON e podem ser consumidos por aplicativo web ou mobile. Não armazenam dados de saúde ou localização do cidadão. Endpoints: `/api/v1/reabilitacao/guia-servicos`, `/api/v1/reabilitacao/fluxo-acesso`.

## Fontes institucionais
- [Rede de Cuidados à Pessoa com Deficiência — Ministério da Saúde](https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/s/saude-da-pessoa-com-deficiencia/rcpd)
- [Centros de Atenção Psicossocial — Ministério da Saúde](https://www.gov.br/saude/pt-br/composicao/saes/desmad/raps/caps/caps/)
- [Oficinas ortopédicas — Ministério da Saúde](https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/s/saude-da-pessoa-com-deficiencia/faq/o-que-e-uma-oficina)

Data da organização: 16/11/2026. Texto educativo elaborado para MVP acadêmico, sujeito à revisão técnica antes de publicação pública.
