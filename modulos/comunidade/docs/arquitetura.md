# Arquitetura

- **Implementado:** entrada manual → validação (`validacao`) → análise (`classificacao`, `monitor`) → orientação (`apresentacao`). A CLI oferece os modos interativo e demo; o histórico existe apenas em memória.
- **Testado em simulação:** fluxo completo com quatro cenários e entradas inválidas.
- **Dados (Fase 1):** `data/raw/` recebe fontes reais baixadas manualmente; `scripts/ingestao_*.py` não assumem formatos e exigem inspeção prévia. `scripts/montar_dataset.py` combina arquivos semanais normalizados disponíveis e omite/avisa fontes ausentes. `scripts/gerar_eventos_simulados.py` gera eventos sintéticos para o módulo de violência, com distritos fictícios `D01`, `D02`, ... e origem preservada.
- **Privacidade:** não há integração real com polícia, sensores ou nuvem. A apresentação de ranking deve ocultar grupos com menos de `MINIMO_EVENTOS_RANKING` eventos (padrão 5) e mostrar “dados insuficientes”.
- **Evolução futura:** definir parsers somente após os arquivos reais serem baixados e inspecionados; persistência e integração dependem de requisitos próprios.
