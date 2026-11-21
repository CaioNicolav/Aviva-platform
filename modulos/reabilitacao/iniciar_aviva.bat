@echo off
cd /d "%~dp0"
echo Iniciando AVIVA 0.9 - Saude e Reabilitacao...
echo Acesse http://127.0.0.1:8000/
echo Para parar: Ctrl+C
py -m uvicorn app.main:app --reload
pause
