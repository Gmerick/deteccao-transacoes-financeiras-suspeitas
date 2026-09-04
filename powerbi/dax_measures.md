# Medidas DAX

As medidas abaixo assumem a tabela fato `fTransactions`.

```DAX
Transações =
COUNTROWS ( fTransactions )

Valor Monitorado =
SUM ( fTransactions[amount] )

Alertas =
CALCULATE ( [Transações], fTransactions[alert_flag] = 1 )

Taxa de Alertas =
DIVIDE ( [Alertas], [Transações] )

Valor em Alertas =
CALCULATE ( [Valor Monitorado], fTransactions[alert_flag] = 1 )

Participação do Valor em Alertas =
DIVIDE ( [Valor em Alertas], [Valor Monitorado] )

Contas com Alertas =
CALCULATE (
    DISTINCTCOUNT ( fTransactions[account_id] ),
    fTransactions[alert_flag] = 1
)

Score Médio dos Alertas =
CALCULATE (
    AVERAGE ( fTransactions[risk_score] ),
    fTransactions[alert_flag] = 1
)

Valor Médio por Alerta =
DIVIDE ( [Valor em Alertas], [Alertas] )
```

## Avaliação contra os cenários simulados

Estas medidas só são possíveis porque a base educacional possui um rótulo conhecido. Em produção, investigações concluídas seriam a fonte do desfecho.

```DAX
Verdadeiros Positivos =
CALCULATE (
    [Transações],
    fTransactions[alert_flag] = 1,
    fTransactions[is_suspicious_simulated] = 1
)

Falsos Positivos =
CALCULATE (
    [Transações],
    fTransactions[alert_flag] = 1,
    fTransactions[is_suspicious_simulated] = 0
)

Falsos Negativos =
CALCULATE (
    [Transações],
    fTransactions[alert_flag] = 0,
    fTransactions[is_suspicious_simulated] = 1
)

Precisão =
DIVIDE ( [Verdadeiros Positivos], [Verdadeiros Positivos] + [Falsos Positivos] )

Recall =
DIVIDE ( [Verdadeiros Positivos], [Verdadeiros Positivos] + [Falsos Negativos] )

F1 Score =
DIVIDE ( 2 * [Precisão] * [Recall], [Precisão] + [Recall] )
```

## Medidas de comparação temporal

```DAX
Alertas Mês Anterior =
CALCULATE ( [Alertas], DATEADD ( dDate[Date], -1, MONTH ) )

Variação Mensal de Alertas =
DIVIDE ( [Alertas] - [Alertas Mês Anterior], [Alertas Mês Anterior] )

Taxa de Alertas Acumulada =
VAR DataMaxima = MAX ( dDate[Date] )
RETURN
DIVIDE (
    CALCULATE ( [Alertas], FILTER ( ALL ( dDate ), dDate[Date] <= DataMaxima ) ),
    CALCULATE ( [Transações], FILTER ( ALL ( dDate ), dDate[Date] <= DataMaxima ) )
)
```

