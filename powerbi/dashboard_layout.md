# Blueprint do dashboard no Power BI

Formato recomendado: 16:9, plano de fundo `#F8FAFC` e grade de 12 colunas.

## Página 1 — Visão executiva

Filtros: período, canal, tipo de transação, estado e nível de risco.

- Cards: Transações, Valor Monitorado, Alertas, Taxa de Alertas, Valor em Alertas e Contas com Alertas.
- Linha: alertas por mês.
- Barras: taxa de alertas por canal.
- Colunas: distribuição por nível de risco.
- Tabela: dez alertas com maior score, valor, conta e regras acionadas.

## Página 2 — Investigação de alertas

- Segmentadores: score, regra, conta, canal, dispositivo confiável e divergência geográfica.
- Tabela detalhada: transação, data/hora, conta, valor, origem/destino, dispositivo, score e regras.
- Drill-through para uma página de conta.
- Formatação condicional: vermelho para Crítico, âmbar para Alto.

## Página 3 — Comportamento e regras

- Barras horizontais: acionamentos por regra.
- Mapa de calor: hora x dia da semana.
- Histograma: valor da transação em escala logarítmica.
- Matriz: regra, acionamentos, peso, verdadeiros positivos e precisão.
- Dispersão: `amount_zscore` x `amount`, tamanho pelo score.

## Página 4 — Qualidade da detecção

- Cards: Precisão, Recall e F1.
- Matriz 2x2: VP, FP, FN e VN.
- Barras: recall por cenário simulado.
- Linha: taxa de alertas ao longo do tempo.
- Caixa de texto: limitações, necessidade de revisão humana e próximos testes.

## Interações

- Sincronize os filtros de período e canal entre as páginas.
- Mantenha seleção cruzada nos gráficos, mas desative o filtro da fila sobre os cards executivos.
- Use tooltip dedicado com média da conta, z-score, volume em 1h/24h e regra acionada.
- Configure drill-through por `account_id`.

