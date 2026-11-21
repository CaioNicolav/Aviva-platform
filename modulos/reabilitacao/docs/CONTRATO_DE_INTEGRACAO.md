# Contrato de integração com o AVIVA principal

A parte de reabilitação tem rota e namespace próprios. O colega pode integrar depois usando os endpoints descritos em `http://localhost:8000/docs`.

- **Prefixo:** `/api/v1/reabilitacao/`.
- **Sem login no MVP:** não armazena nome, documentos ou informações de saúde do cidadão.
- **Status de base:** `sem_registros_conferidos` vs. `registros_conferidos`.
- **Busca:** `GET /api/v1/reabilitacao/servicos?uf=SP&municipio=São%20Paulo&modalidade=fisica`.
- **Orientações:** `GET /api/v1/reabilitacao/orientacoes`.
- **Modalidades:** `GET /api/v1/reabilitacao/modalidades`.
- **Saúde do módulo:** `GET /api/v1/reabilitacao/health`.

Exemplo de resposta enquanto não houver unidade validada:

```json
{
  "total": 0,
  "resultados": [],
  "situacao_base": "sem_registros_conferidos",
  "aviso": "A ausência de resultados não comprova ausência de serviços. Consulte a UBS ou secretaria municipal de saúde.",
  "fonte_principal": "https://dadosabertos.saude.gov.br/dataset/cnes-cadastro-nacional-de-estabelecimentos-de-saude"
}
```

**Integração posterior:** compartilhar autenticação apenas se necessário; definir CORS permitido e documentação OpenAPI; colocar banco em serviço próprio e versionar contrato. Pode ser consumido de React, Flutter, React Native, HTML/JS ou via backend.
