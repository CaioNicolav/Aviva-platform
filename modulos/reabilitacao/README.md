# AVIVA v0.11 — mapa único com localizações conferidas

**Atualização de segurança cartográfica:** o seletor "Explorar coordenadas CNES (sem validação)" foi eliminado. O mapa e a busca por proximidade utilizam exclusivamente registros conciliados com referência geográfica independente. Os registros sem essa comprovação continuam na **lista** e são explicitamente sinalizados, sem gerar pins.

**Base municipal já incluída neste pacote:** os arquivos KMZ de referência de UBS e áreas de abrangência (2026) estão na pasta `fontes_oficiais/`. O cruzamento liberou 448 UBS com código CNES, logradouro, número e CEP compatíveis; demais UBS, CAPS, CER e oficinas aguardam validação geográfica correspondente. Uma localização conferida não comprova atendimento ativo, horário, vaga, especialidade ou entrada exata.

Abra **esta pasta**, onde estão `app/`, `web/` e `requirements.txt`, e execute `py -m uvicorn app.main:app --reload`. Acesse `http://127.0.0.1:8000/`. Veja `docs/MAPA_UNICO_VERIFICADO_v11.md` para detalhes.

---
# AVIVA 0.10 — Busca e mapa de serviços de reabilitação (piloto São Paulo)

A versão 0.10 inclui os dados de referência geográfica de **UBS** publicados pela Prefeitura de São Paulo em 2026. A lista textual continua abrangendo candidatos do CNES (CAPS, CER, oficinas e outros), mas somente os pontos de UBS que tiveram **CNES e endereço compatíveis** com a camada municipal independente são liberados na visualização **Mapa validado** e na ferramenta de **5 mais próximos**.

## Abrir no VS Code
1. Abra esta pasta, que contém `app/` e `requirements.txt` (não há pasta interna extra).
2. Abra o Terminal e execute `py -m pip install -r requirements.txt` se necessário.
3. Execute `py -m uvicorn app.main:app --reload`.
4. Digite **manualmente** no navegador: `http://127.0.0.1:8000/` (sem asteriscos nem parâmetros extras).
5. Selecione `UBS` → `Mapa` para visualizar os pontos verificados; use “Exploratório” somente para comparação de coordenadas **não** validadas.

## Rastreabilidade e limites
Veja `docs/RELATORIO_CRUZAMENTO_GEOSAMPA_2026_v10.md` e os relatórios CSV em `data/`.

- `data/ubs_cnes_sp.csv` contém valores originais da importação CNES, mantidos sem sobrescrita.
- `data/referencia_municipal_ubs_2026.csv` contém pontos independentes com ID CNES, endereço e coordenada do município.
- `data/cruzamento_enderecos_ubs_2026.csv` mostra correspondências confirmadas e conflitos.
- `data/auditoria_integral_sp.csv` é usado pelo app para permitir somente os pins reconciliados.
- `fontes_oficiais/` preserva os KMZ oficiais para reprocessamento.

O aplicativo não garante serviço de reabilitação, vaga, horário, confirmação de UBS de referência ou acesso direto. A localização não é enviada ao servidor na busca de proximidade desta versão.
