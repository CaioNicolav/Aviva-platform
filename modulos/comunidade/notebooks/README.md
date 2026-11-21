# Notebooks

- **Implementado:** `ml-tradicional.ipynb` prepara o dataset climático no próprio notebook, define chuva forte pelo percentil 90 do treino e compara baseline, regressão logística e floresta aleatória em uma divisão temporal. O notebook contém saídas executadas, EDA, distribuição de classes, série temporal do teste, matrizes de confusão e curvas ROC.
- **Gráficos exportados:** `ENTREGAS_FIAP/04_ML/graficos/` contém as quatro figuras PNG para slides e relatório.
- **Google Colab:** use `ENTREGAS_FIAP/04_ML/AVIVA_ML_Colab.zip`. Extraia o ZIP em `/content` e abra `ml-tradicional.ipynb`; o CSV já está no caminho relativo que o notebook procura.
- **Decisões do experimento:** as 2 primeiras linhas de cada estação são descartadas apenas no notebook; dias com mais de 6 horas faltantes também são excluídos. O treino cobre verão/outono e o teste, inverno/primavera; como o dataset é pequeno, os resultados são exploratórios.
- **Etapa 05 - MLP:** `mlp.ipynb` compara redes com 16 e 32 neurônios, pondera classes usando somente o treino e inclui métricas, gráficos e previsões. A entrega e o pacote Colab estão em `ENTREGAS_FIAP/05_MLP/`; exige scikit-learn 1.7 ou superior.
- **Evolução futura:** ampliar período e estações e validar estabilidade antes de qualquer uso operacional.
