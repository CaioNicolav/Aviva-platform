# AVIVA — Design System v1.3

## Direção e princípios

Uma plataforma social acessível, com linguagem simples e **mesma identidade** entre Início, Auxílios, Sobre, Login, Comunidade e Reabilitação. Inspirado nas referências do usuário: cabeçalho limpo, banners verdes arredondados, conteúdo sobre **branco**, painel verde-claro em **quatro colunas** e detalhes em **laranja claro**.

## Paleta principal

| Uso | Cor | Hex |
|---|---|---|
| Verde principal | Verde-escuro AVIVA | `#064532` |
| Verde de conteúdo | Verde médio | `#1D6B4B` |
| Branco | Fundo geral | `#FFFFFF` |
| Verde claro | Painéis e cards | `#D9EDB9` |
| Fundo auxiliar | Menta-pálida | `#EFF7E2` |
| Laranja apoio | Acentos e botões | `#EE965A` |
| Laranja mais escuro | Contraste de texto/botão | `#DB723C` |

Tipografia: **Poppins** do Google Fonts, fallback Arial/sans-serif. Pesos 400 / 500 / 600 / 700 / 800. O layout se adapta ao navegador e ao Android; o manifesto PWA não gera um aplicativo Android nativo.

## Componentes

- Cabeçalho: logotipo à esquerda, navegação central (`Início`, `Auxílios`, `Sobre`) e `Login` à direita. No celular, menu responsivo.
- Hero: slogan centralizado, texto curto e ilustração coletiva em aquarela.
- Faixa de destaque: banner horizontal verde-escuro, bordas de 29px e chamada em branco/verde-claro.
- Painel de serviços: fundo verde-pistache, quatro colunas no desktop e duas no Android, divisórias sutis.
- Páginas internas: hero institucional verde, títulos em branco, destaque laranja claro; blocos de apoio brancos/verdes com cantos arredondados.
- Módulo de Saúde e Reabilitação: mantém mapa, categorização de serviços, avisos nos pins e guia do SUS; adiciona navegação para o portal e aplica as cores do sistema.
- Módulo Comunidade e Território: preserva o mural, recursos e indicadores; atualiza as cores e links para o portal.

## Arquivos de customização

- `site/assets/aviva-design.css`: camada visual principal do portal
- `modulos/reabilitacao/web/aviva-brand.css`: camada visual do módulo de reabilitação
- `modulos/comunidade/web/styles.css`: incorpora o bloco final `AVIVA v1.3`

A lógica de negócio, as APIs e as bases de dados dos módulos **não foram substituídas**. Login permanece demonstrativo; nenhum PIN exploratório significa atendimento confirmado.

## Execução no VS Code

Abra diretamente a pasta contendo `portal.py`. No terminal:

```powershell
py -m pip install -r requirements.txt
py portal.py --port 8001
```

Acesse `http://127.0.0.1:8001/`. Se a 8001 estiver ocupada, use `--port 8002`. Para testar em Android fora do computador, publique em HTTPS com acesso controlado.

## Limitações

Esta é uma refatoração visual. Não são autenticação real, confirmação clínica, reserva de serviços ou aplicativo APK. Testes de interface precisam ser realizados também no dispositivo Android real após a instalação local.
