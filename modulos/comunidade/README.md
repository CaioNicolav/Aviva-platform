# AVIVA

**Tecnologia para melhorar a vida e promover autonomia.**

Plataforma acadêmica de apoio comunitário e inteligência urbana. O protótipo web permite selecionar um dos 96 distritos oficiais de São Paulo, explorar equipamentos e serviços locais mapeados, consultar contatos públicos e experimentar um mural de pedidos, ofertas de ajuda e problemas do bairro. O painel climático e a simulação de risco são módulos complementares, não o propósito inteiro do AVIVA.

## Status

- **Implementado:** monitor em Python, validação, classificação e recomendações; protótipo web local com seleção de distrito IBGE, guia de equipamentos mapeados no OpenStreetMap, identidade visual AVIVA, mural de demonstração e dados climáticos do INMET; notebook experimental de ML tradicional em `notebooks/ml-tradicional.ipynb` (não integrado à plataforma).
- **Testado em simulação:** quatro cenários e seis entradas inválidas no modo de demonstração.
- **Evolução futura:** substituir cenário, variáveis e limites pelos critérios do PDF oficial de IoT/AICSS; integrar fontes de dados e desenvolver entregas disciplinares.

Os limites são provisórios. Não há integração real com sensores, serviços de nuvem ou modelos de ML/MLP na plataforma; o notebook de ML é exploratório e não operacional.

## Como executar

Requer Python 3.8 ou superior. O pacote `aviva` não tem dependências externas.

```bash
python -m aviva --demo
python -m aviva
```

Para abrir o protótipo web local, execute `python -m aviva.web` e acesse
`http://127.0.0.1:8000`. A cobertura atual é a cidade de São Paulo: escolha
um distrito oficial e, opcionalmente, informe um bairro. O mural demonstra
pedidos, ofertas, trocas, encontros e problemas; os exemplos são salvos apenas
neste navegador e não aparecem para outros moradores. Os distritos vêm do
IBGE; o guia territorial consulta equipamentos e limites colaborativos do
OpenStreetMap; e o módulo climático apresenta observações históricas do INMET.
A gestão e a cobertura dos pontos do mapa não são garantidas como cadastro
oficial. O mural ainda não tem contas, mensagens privadas, moderação nem
publicações compartilhadas; não recebe sensores em tempo real nem envia
alertas. Consulte
[web/README.md](web/README.md).

Para executar os testes, instale os requisitos de desenvolvimento e rode `pytest`.

## Estrutura

- `aviva/`: configuração, validação, classificação, monitoramento, apresentação e CLI.
- `tests/`: testes unitários e de cenários simulados.
- `data/`: dados climáticos brutos do INMET, lista oficial de distritos do IBGE, dataset diário tratado e dados simulados identificados como tais.
- `docs/`: arquitetura, limites provisórios, segurança e decisões pendentes.
- `entregas/`: evidências organizadas por disciplina.
- `iot/` e `cloud/`: espaços reservados para evoluções futuras; `scripts/` contém ingestão/montagem de dados e `notebooks/` contém o experimento de ML tradicional.

Cada disciplina — Pensamento Computacional com Python, Cibersegurança Cognitiva, Machine Learning & Modelling, Redes Neurais Artificiais (MLP) e IoT/AICSS — terá entregas próprias.
