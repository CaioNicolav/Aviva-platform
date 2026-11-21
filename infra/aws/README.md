# AWS — AVIVA

Fluxo validado em 19/11/2026: **S3 (medicoes/*.json) → Lambda Python 3.12 → Amazon RDS MySQL → trigger experimental de alertas.**

**`lambda_function.py` é reconstruído**, pois o arquivo exato implantado não estava disponível na conversa/arquivos recuperados. O comportamento de ingestão foi documentado por evidências de execução e Workbench, mas este novo código deve ser validado em conta própria.

```bash
python -m unittest discover -s infra/aws/tests -v
```

Crie o schema original, verifique duplicidades, aplique a chave UNIQUE e o trigger, configure IAM mínimo, Secrets Manager, RDS CA bundle e gatilho S3, sempre em ambiente de testes. Consulte `docs/IMPLEMENTACAO_AWS.md`. Não use as medições fictícias como alertas reais.
