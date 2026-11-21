# Revisão da publicação pública

**Autores autorizadores:** Caio Nicolav e Leonardo da Silva.

## Medidas adotadas

- Publicação em repositório independente, com **histórico Git novo**, para não importar commits privados antigos.
- Exclusão de arquivos `.git`, documentos de avaliação internos, prints de console com identificação de contas e arquivos de credenciais.
- Varredura dos códigos e dados de texto selecionados por padrões comuns de chaves AWS, tokens OAuth/GitHub, PEM e endereços pessoais; nenhum segredo reconhecível foi identificado.
- Manutenção apenas de medições e eventos marcados como **simulados**.
- Credenciais AWS/RDS em variáveis de ambiente ou Secrets Manager na implementação de referência, sem valores reais.
- Preservação da procedência e das limitações de uso de dados CNES, INMET e outros.

## Observações

A verificação estática não é uma garantia de ausência de todo segredo possível. Não foram publicadas capturas de consoles e não foi importado histórico privado. Antes de implantar, configure IAM mínimo, TLS com CA RDS, rede privada e proteção de credenciais.

As fontes públicas e imagens podem possuir restrições de licença distintas; mantenha suas atribuições. **AVIVA é um produto em desenvolvimento, não um serviço de alerta/emergência ou de indicação médica operacional.**
