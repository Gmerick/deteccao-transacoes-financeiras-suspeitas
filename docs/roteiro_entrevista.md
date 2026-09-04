# Roteiro para entrevista

## Pitch de 60 segundos

> Desenvolvi um projeto ponta a ponta para detectar transações financeiras suspeitas e priorizar investigações. Gerei uma base sintética e reproduzível com 50 mil transações de 2.500 contas e injetei cinco cenários de risco, como valor atípico, alta velocidade e uso de novo dispositivo fora da localização habitual. Em Python e Pandas, criei atributos comportamentais, sete regras explicáveis e um score de zero a cem. A solução sinalizou 2.243 operações, com precisão de 74,36%, recall de 83,40% e F1 de 78,62% nos padrões simulados. Depois modelei a camada analítica em SQL e preparei o modelo, as medidas DAX e o layout para Power BI. O objetivo não é afirmar fraude automaticamente, mas reduzir o universo de análise e fornecer uma fila auditável para revisão humana.

## Apresentação de cinco minutos

### 1. Problema — 40 segundos

Explique que a equipe não consegue investigar todas as movimentações e precisa equilibrar cobertura, falsos positivos e capacidade operacional.

### 2. Dados — 50 segundos

Mostre o grão da base, as 50 mil transações, os atributos da conta e os cinco cenários simulados. Destaque que os dados são sintéticos por privacidade e reprodutibilidade.

### 3. Método — 90 segundos

Apresente z-score por conta, janelas de 1h e 24h, divergência geográfica, dispositivo e horário. Explique que os pesos geram um score transparente e fácil de auditar.

### 4. Resultados — 70 segundos

Mostre o dashboard e a matriz de avaliação:

- 2.243 alertas, equivalentes a 4,49% da carteira;
- 1.668 verdadeiros positivos simulados;
- precisão de 74,36%;
- recall de 83,40%;
- F1 de 78,62%;
- R$ 10,32 milhões associados aos alertas.

Evite dizer que R$ 10,32 milhões representam perda ou fraude confirmada. É apenas valor financeiro em operações sinalizadas.

### 5. Recomendação e próximos passos — 50 segundos

Defenda revisão humana por prioridade, calibração do limiar conforme capacidade da equipe, criação de feedback das investigações e monitoramento de drift. Como evolução, cite aprendizado supervisionado, grafos de relacionamento e detecção online.

## Perguntas prováveis

### Por que não chamou os alertas de fraude?

Porque comportamento fora do padrão é apenas um sinal. A confirmação depende de investigação, contexto e, em muitos casos, contato com o cliente.

### Por que usar regras em vez de machine learning?

Regras oferecem uma linha de base explicável, rápida e auditável. Elas também ajudam a estruturar dados e feedback antes de treinar um modelo. A evolução natural é comparar regras, modelo supervisionado e abordagem híbrida.

### Por que usar o z-score por conta?

O mesmo valor pode ser comum para uma conta e atípico para outra. A comparação individual reduz a dependência de um limite absoluto único.

### Como escolheu o limiar de 20 pontos?

Foi calibrado para este case, buscando boa cobertura sem gerar uma fila excessiva. Em produção, eu otimizaria o limiar usando custo de falso positivo, perda evitada e capacidade diária da equipe.

### Qual é a principal limitação?

A base é sintética e o cálculo usa o período completo. Em produção, os atributos precisam ser calculados apenas com eventos anteriores para evitar vazamento temporal.

### Como levaria para produção?

Separaria ingestão, feature store, motor de regras/modelo, fila de casos e feedback. Acrescentaria versionamento das regras, monitoramento, testes de carga, trilha de auditoria, controle de acesso e proteção de dados.

## Demonstração recomendada

1. Abra o README e explique a arquitetura.
2. Execute `python run_pipeline.py`.
3. Mostre `reports/dashboard_preview.png`.
4. Abra `alerts_prioritized.csv` e selecione um alerta crítico.
5. Execute uma consulta na view `vw_alert_queue`.
6. Mostre as medidas DAX e o blueprint do Power BI.

