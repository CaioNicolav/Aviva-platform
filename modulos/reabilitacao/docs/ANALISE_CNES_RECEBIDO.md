# Análise do arquivo CNES enviado — AVIVA 0.2

## Origem e alcance

- Arquivo recebido: `cnes_estabelecimentos_json.zip`, contendo `cnes_estabelecimentos.json`.
- Data de recebimento: 16/11/2026. **O arquivo JSON não contém, nos campos analisados, uma data de competência cadastral**; recebimento não significa atualização da base.
- Fonte declarada pelo arquivo: Cadastro Nacional de Estabelecimentos de Saúde (CNES), Ministério da Saúde.
- Link de referência: https://dadosabertos.saude.gov.br/dataset/cnes-cadastro-nacional-de-estabelecimentos-de-saude
- Registros JSON processados: **642.608**, nacional.
- Unidades candidatas por pistas textuais em `NO_FANTASIA` + `NO_RAZAO_SOCIAL`: **27.779**.

## Quantidades identificadas por termos nos nomes

| Categoria inferida pelo nome | Total de candidatos | Campo ambulatorial SUS = SIM | Campo ambulatorial SUS = NAO |
|---|---:|---:|---:|
| CAPS/psicossocial | 3.694 | 2.039 | 1.655 |
| CER/centro especializado em reabilitação | 416 | 310 | 106 |
| Oficinas ortopédicas | 32 | 22 | 10 |
| Outras referências a reabilitação/fisioterapia | 23.637 | 3.513 | 20.124 |
| **Total** | **27.779** | **5.884** | **21.895** |

A categoria deriva **exclusivamente de uma heurística de nome**, não de cadastro de
habilitações. Também podem existir verdadeiros serviços de reabilitação cujo nome
não contém essas expressões e que não entram na seleção. A sigla `CER` pode ocorrer
no nome de unidade sem ser Centro Especializado em Reabilitação; o resultado é candidato.

O arquivo CNES contém o campo `CO_AMBULATORIAL_SUS` com valores SIM/NAO. **Não
atribuir a ele o sentido de serviço especializado de reabilitação confirmado.**
Não inferir atendimento atual, gratuidade de procedimentos, agenda, elegibilidade,
modalidades físico/auditivo/visual/intelectual ou cobertura a partir desse campo.

## Estrutura de dados processada

Campos principais utilizados do ZIP: `CO_CNES`, `CO_UF`, `CO_IBGE`,
`NO_FANTASIA`, `NO_RAZAO_SOCIAL`, `CO_AMBULATORIAL_SUS`, `TP_UNIDADE`,
`NO_LOGRADOURO`, `NU_ENDERECO`, `NO_BAIRRO`, `CO_CEP`, `NU_TELEFONE`.
Os nomes de municípios **não estão presentes no JSON de entrada**: há códigos
`CO_IBGE` de seis dígitos. O script opcional enriquece esses códigos com os nomes da
API do IBGE (https://servicodados.ibge.gov.br/api/v1/localidades/municipios).

O CSV de candidatos **não contém informações pessoais de pacientes**.
Dados de contato cadastrados do estabelecimento podem estar desatualizados.

## O que já atende a parte de preparação

- Extração programática de dados reais e metadados de procedência.
- Estrutura preliminar com variáveis categóricas (categoria inferida, UF, sinalizador ambulatorial SUS) e quantidades de unidades por código de município.
- API Python com busca por UF, código/nome municipal e categoria de estabelecimento.
- Testes que comprovam a separação entre candidatos e registros efetivamente conferidos.

## Próximos passos para as disciplinas FIAP

1. **Estatística:** documentar variáveis e criar uma variável quantitativa discreta real, como o número de estabelecimentos por município, e uma quantitativa contínua fundamentada (p. ex., indicador de cobertura por 100 mil habitantes após associação com população do IBGE). As estatísticas de candidatos **não representam cobertura efetiva de reabilitação**.
2. **Machine Learning e MLP:** definir variável-alvo não circular e validada, com dados externos apropriados; o campo `categoria_indicio_nome` não deve ser tratado como verdade clínica para treinar previsão de especialidade sem rotulagem independente.
3. **Banco de dados:** modelar estabelecimentos, municípios, tipos de serviço e habilitações (ainda não disponíveis nesta extração) com chaves CNES/IBGE.
4. **AWS:** usar este CSV em um fluxo S3 → Lambda → RDS → CloudWatch, conforme autorização do professor para adaptar o exemplo agrícola.
5. **Python/Cyber/IoT:** requisitos específicos de sensor, 3 níveis e validações ainda precisam de protótipos próprios. O buscador CNES não substitui os dois sensores nem os três níveis exigidos.

## Prudência na apresentação

> "O AVIVA identifica estabelecimentos potencialmente relacionados à reabilitação a
> partir de registros públicos do CNES. Estamos demonstrando a etapa de descoberta e
> limpeza de dados; a confirmação das habilitações, modalidades e disponibilidade de
> atendimento é uma etapa separada e necessária antes de recomendar uma unidade ao cidadão."
