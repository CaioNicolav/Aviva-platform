# AVIVA 0.6 — Oficinas ortopédicas documentadas (São Paulo)

A classificação anterior usava termos no **nome fantasia do estabelecimento CNES**. Isso fazia com que oficinas ligadas a hospitais e outras organizações não aparecessem quando seus nomes de cadastro não incluíam “oficina”.

A versão 0.6 incorpora em arquivo independente `data/oficinas_documentadas_sp.csv` duas oficinas com documentação pública:

1. Oficina Ortopédica do Instituto de Ortopedia e Traumatologia — HCFMUSP, cadastro CNES **2078015**. Instituição: https://www.iothcfmusp.com.br/pt/assistencia/especialidades-de-atendimento/oficina-ortopedica/ ; cadastro oficial de incentivo: https://cnes2.datasus.gov.br/Mod_IntegraSUS.asp?VCo_Unidade=3550302078015 ; endereço da oficina divulgado pelo IOT: Rua Dr. Ovídio Pires de Campos, 333, Cerqueira César.
2. Oficina Ortopédica AACD Ibirapuera, CNES institucional **2077655**. Instituição: https://aacd.org.br/unidades/ibirapuera-sp ; endereço específico da oficina: Rua Pedro de Toledo, 1620, Vila Clementino/Ibirapuera. Em portaria de 2023, ambos aparecem como oficinas fixas: https://bvs.saude.gov.br/bvs/saudelegis/gm/2023/prt1602_19_10_2023.html .

**Interpretação correta:** fonte institucional prova a existência/descritivo da oficina na publicação consultada, mas não confirma vagas atuais, encaminhamento direto, elegibilidade SUS, agendamentos ou disponibilidade de produtos. O campo `ambulatorial_sus_informado=SIM` vem do cadastro CNES **do estabelecimento**, não autoriza inferir atendimento específico na oficina.

**Geografia:** coordenadas foram obtidas do registro CNES do estabelecimento vinculado e podem marcar a unidade geral, não exatamente a porta da oficina, que tem endereço diferente; distâncias de proximidade devem ser tratadas como aproximadas. Não atribuir automaticamente disponibilidade de serviços a todos os moradores da região.

Atualização recomendada antes de produção: consultar habilitações atuais do CNES e serviços especializados, conferir canal oficial de regulação e geocodificar apenas os endereços institucionais verificados.
