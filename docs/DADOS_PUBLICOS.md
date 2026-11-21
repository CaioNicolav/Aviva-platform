# Dados públicos e integridade

Este repositório contém fontes públicas e registros **explicitamente simulados**. A base de candidatos do CNES é usada como conjunto **exploratório**: cadastro não comprova modalidade, vagas, acesso ou funcionamento.

## CNES — distribuição reproduzível

O CSV original `modulos/reabilitacao/data/cnes_candidatos.csv` tem cerca de 6,6 MB. Para a publicação por API, os mesmos bytes foram comprimidos em GZIP e divididos em cinco arquivos `cnes_candidatos.csv.gz.part01` a `part05`, na mesma pasta. `load_candidates()` lê o CSV diretamente quando disponível ou recompõe as partes em memória de forma automática; a hash SHA-256 do GZIP é conferida antes da descompressão.

- SHA-256 do CSV integral: `c574c4d4092a400ed0adf193d398ec2e1ff428d76321b841eec06d05a503bac4`
- SHA-256 do GZIP concatenado: `44678323a25abaca26d8b4154f7280a7177b6653fbcd48b07b03d5390fb04261`
- Os arquivos INMET mantêm a codificação original exportada da fonte.
- As bases de eventos comunitários são **sintéticas**; não representam denúncias reais.

O banco SQL é uma camada de demonstração separada do backend atual, e os notebooks são experimentos independentes. Use as fontes atualizadas das instituições responsáveis ao tomar decisões no mundo real.
