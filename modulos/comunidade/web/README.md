# Protótipo web do AVIVA

Interface comunitária local em HTML, CSS e JavaScript, servida pelo Python da
aplicação. A cobertura territorial disponível é a cidade de São Paulo: o
morador escolhe um dos 96 distritos oficiais e pode informar um bairro para
recortar o mural local. São Paulo não tem uma lista oficial única de bairros;
o protótipo consulta separadamente o OpenStreetMap por objetos de localidade
`place=suburb`, `place=neighbourhood` e `place=quarter`. Essa lista colaborativa
pode estar incompleta e não é tratada como oficial. Os distritos vêm da API
de localidades do IBGE e estão incluídos em `data/distritos_sao_paulo.json`.

Após escolher um distrito, o servidor consulta o Nominatim e o Overpass API
para exibir o limite e os equipamentos nomeados no OpenStreetMap: saúde,
educação, assistência social, segurança, cultura e administração pública. Os
pontos são filtrados pela geometria do distrito, não apenas por uma caixa de
mapa. O mapa incorporado é do OpenStreetMap e apresenta o centro aproximado do
distrito; os links de cada equipamento abrem sua posição individual. As sugestões são baseadas nos objetos cartográficos retornados pelo OSM,
filtrados para o limite do distrito, e podem estar incompletas. O texto
digitado como bairro não é enviado à fonte geográfica.

O mural demonstra pedidos de ajuda, ofertas, doações e trocas, encontros ou
mutirões e problemas locais. As publicações ficam no `localStorage` do
navegador e podem ser excluídas por quem as criou neste dispositivo; elas não
são enviadas ao servidor e não aparecem para outros moradores. Não há contas,
mensagens, comentários, moderação ou atualização colaborativa em tempo real.

A série climática vem de CSV histórico do INMET; a simulação reutiliza as
regras provisórias do monitor Python.

## Executar

Na raiz do repositório:

```powershell
python -m aviva.web
```

Abra `http://127.0.0.1:8000`. O servidor usa a interface de loopback local e
encerra com `Ctrl+C`.

O painel requer
`entregas/pensamento-computacional/base_estatistica.csv` e
`data/distritos_sao_paulo.json`. Para servir a interface, o servidor usa
somente a biblioteca padrão de Python.

## Rotas locais

- `GET /api/clima?dias=14`: observações reais diárias das estações disponíveis,
  com período selecionável entre 1 e 30 dias.
- `GET /api/distritos`: os 96 distritos do município de São Paulo, obtidos do
  IBGE.
- `GET /api/bairros?distrito=355030890`: consulta localidades nomeadas no
  OpenStreetMap em uma requisição separada e focada, independente do catálogo
  de serviços; o resultado fica em cache na memória por 30 minutos.
- `GET /api/servicos?distrito=355030890`: consulta os pontos nomeados no
  OpenStreetMap para um dos distritos oficiais. O catálogo fica em cache na
  memória do processo por 30 minutos.
- `POST /api/avaliar`: recebe leituras manuais e devolve a classificação e as
  recomendações do monitor Python.

## Limites e privacidade

- O mural não carrega publicações reais. As publicações criadas ficam no
  armazenamento local deste navegador, podem persistir após recarregar e podem
  ser excluídas neste dispositivo; não são compartilhadas com outros
  moradores. Limpar os dados do navegador também as remove. Não há contas,
  mensagens privadas, moderação ou persistência no servidor.
- O filtro por distrito usa o código oficial do IBGE. Os limites e pontos de
  referência vêm do OpenStreetMap e não são cadastro oficial da Prefeitura;
  sua cobertura varia. Os bairros não têm uma lista oficial única na cidade:
  sugestões vêm dos objetos geográficos de localidade encontrados no
  OpenStreetMap; o texto livre também é aceito e restringe apenas os exemplos
  locais.
- A fonte não identifica sempre o tipo de gestão, funcionamento ou atendimento
  de uma unidade. Não presumimos que todo hospital, escola ou serviço mapeado é
  público; quando essa informação não existe, a interface avisa. Confirme dados
  diretamente com o serviço responsável.
- Não informe endereço, telefone, dados de terceiros ou relatos sensíveis.
  Não há localização GPS. O nome oficial do distrito é enviado ao Nominatim
  para localizar o limite; os serviços mapeados são consultados no Overpass.
- Os dados geográficos são © contribuidores do OpenStreetMap, sob a licença
  Open Database License (ODbL). Consulte
  [os créditos da fonte](https://www.openstreetmap.org/copyright).
- Se a consulta de localidades falhar, ainda é possível digitar o bairro
manualmente. A API de bairros é uma requisição independente da busca ampla de
serviços para que a indisponibilidade de um catálogo não oculte o outro.

Os contatos 190, 192, 193, 199 e 180 são atalhos para serviços públicos reais;
  o AVIVA não aciona nem monitora esses serviços.
- A classificação de risco é uma simulação acadêmica com limites provisórios.
  O painel não recebe leituras ao vivo, não mede nível de rio ou alagamento e
  não envia alertas. A série de chuva é diária, não horária.
