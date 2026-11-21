# Executar e testar o AVIVA

Instale Python e execute na raiz:

```powershell
py -m pip install -r requirements.txt
py portal.py --port 8001
```

Abra `http://127.0.0.1:8001/`. O gateway é criado dinamicamente por `portal.py`: não rode diretamente `uvicorn portal:app`.

## Testes por módulo

```bash
cd modulos/comunidade
python -m pytest -q
cd ../reabilitacao
python -m pytest -q
```

## Testes AWS offline (sem acesso à nuvem)

```bash
python -m unittest discover -s infra/aws/tests -v
```

Para rodar SQL no Workbench, use o schema e a carga original do pacote, em banco **vazio de teste**. A carga SQL não é idempotente. Consulte `docs/IMPLEMENTACAO_AWS.md`.

As ferramentas locais não garantem disponibilidade de recursos AWS nem comprovam uma implantação pública.
