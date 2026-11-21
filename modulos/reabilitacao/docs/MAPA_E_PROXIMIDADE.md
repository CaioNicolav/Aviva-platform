# AVIVA 0.4 — Mapa e pesquisa dos mais próximos (São Paulo capital)

## Funcionalidades entregues

- A API `GET /api/v1/reabilitacao/cnes/mapa-sp` devolve **todos os candidatos** da capital com latitude e longitude válidas, respeitando `zona`, `bairro` e `categoria` quando informados. Não corta os resultados na página 30, ao contrário da listagem.
- O navegador utiliza Leaflet 1.9.4 e base OpenStreetMap para visualizar os candidatos com ruas (conexão à internet necessária). Quando a biblioteca não carrega, a interface desenha uma **prévia geográfica simplificada em SVG, sem ruas e sem limites oficiais**, que ainda permite selecionar um ponto e calcular proximidade.
- Modo **Lista**, **Mapa** e **Lista + mapa**.
- O cidadão pode escolher um ponto por clique no mapa ou, voluntariamente, usar a geolocalização do dispositivo.
- O botão **Encontrar 5 mais próximos** consulta os candidatos *em toda a capital* na categoria selecionada, mesmo se a busca anterior não encontrou resultados no bairro, e ordena por distância geodésica (Haversine) **no próprio navegador**. O cálculo não representa rota real, tempo nem transporte público.
- Nenhuma coordenada do cidadão é enviada ao backend ou gravada pelo módulo. Sem autenticação, banco de dados pessoal, cookies de localização nem armazenamento local. A localização permanece em memória até fechar/recarregar a página.
- Resultados sem coordenadas continuam disponíveis na lista, mas não podem aparecer como pins ou concorrer à busca por proximidade.

## Limitações essenciais

1. **Os pins são CANDIDATOS, não serviços validados.** A identificação de CAPS/CER/OUTROS depende de palavras no nome do estabelecimento e do campo de atendimento ambulatorial SUS da base. Isso não confirma que a modalidade esteja habilitada, que haja vagas, ou atendimento ativo.
2. As coordenadas foram obtidas diretamente da base CNES fornecida pelo estudante, sem geocodificação adicional. O projeto descarta valores vazios, incoerentes e evidentemente fora do entorno de São Paulo; não comprova a precisão fina da localização de cada unidade.
3. A associação zona/bairro continua preliminar e textual. Para produção, cruzar com limites geográficos oficiais dos distritos administrativos e corrigir ambiguidades.
4. O mapa com ruas depende de conexão à internet (OpenStreetMap e unpkg); há prévia geográfica sem ruas, e a lista/API são locais.
5. Quando o usuário permite geolocalização, sua posição pode ser imprecisa (especialmente em computadores). O ponto clicado é uma alternativa manual; o sistema não verifica se é residência verdadeira.
6. Ao carregar ruas do OpenStreetMap, o navegador consulta servidores externos para obter blocos do mapa. O AVIVA não compartilha coordenadas do usuário por sua API; no entanto, o serviço de mapas pode observar a área visualizada, segundo suas próprias políticas.
7. Confirmar unidade e fluxo de acesso com a UBS/Secretaria de Saúde antes de se deslocar.

## Endpoints e integração futura

- `GET /api/v1/reabilitacao/cnes/candidatos?uf=SP&municipio=S%C3%A3o%20Paulo&categoria=CAPS&zona=leste&bairro=ITAQUERA`
- `GET /api/v1/reabilitacao/cnes/bairros-sp?categoria=CAPS&zona=leste`
- `GET /api/v1/reabilitacao/cnes/mapa-sp?categoria=CAPS&zona=leste&bairro=ITAQUERA`
- `GET /api/v1/reabilitacao/cnes/mapa-sp?categoria=CAPS` (fonte para busca ampliada por proximidade)

Para a integração futura com o AVIVA completo, o frontend poderá ser adaptado a React/Flutter ou consumir a mesma API JSON. A localização do usuário não precisa ser enviada ao servidor para pesquisar proximidade no MVP.

## Teste manual

1. Iniciar o Uvicorn e acessar `http://127.0.0.1:8000/` no computador.
2. Pesquisar CAPS / Zona Leste / Itaquera e verificar lista + mapa e pins.
3. Trocar entre Lista, Mapa e Lista + mapa.
4. Selecionar um bairro/categoria sem resultados: clicar em **Buscar também em outros bairros**.
5. Clicar em **Marcar minha casa no mapa**, clicar no mapa e depois em **Encontrar 5 mais próximos**. Ver os cinco nomes, distâncias aproximadas e pins destacados, mesmo que estejam fora do bairro filtrado.
6. Como teste opcional, clicar em **Usar minha localização**, autorizar a permissão no navegador (localhost é contexto seguro) e repetir a pesquisa.
7. Revogar a autorização no navegador quando quiser.

Para a banca: a lista mostra candidatos do CNES, e não uma agenda, recomendação clínica ou classificação oficial de cobertura. A rede de atenção à saúde exige etapas de confirmação das habilitações e acesso.
