# Modelo de dados no Power BI

## Arquivos de entrada

- `data/processed/transactions_scored.csv`: fato transacional com atributos, regras e score.
- `data/processed/rule_summary.csv`: quantidade de acionamentos e peso de cada regra.
- `data/processed/monthly_monitoring.csv`: resumo mensal para conferência.

## Modelo recomendado

Use `transactions_scored.csv` como origem da consulta `stgTransactions`. Desabilite sua carga e crie referências para o modelo estrela:

| Tabela | Grão | Construção |
|---|---|---|
| `fTransactions` | Uma transação | Selecione IDs, data/hora, valores, flags, score e chaves dimensionais |
| `dAccount` | Uma conta | Remova duplicatas de `account_id` e mantenha perfil e estado de origem |
| `dDate` | Um dia | Calendário DAX entre as datas mínima e máxima |
| `dChannel` | Um canal | Lista distinta de `channel` |
| `dRule` | Uma regra | Importe `rule_summary.csv`; tabela desconectada para auditoria |

## Relacionamentos

| De | Para | Cardinalidade | Direção |
|---|---|---|---|
| `dAccount[account_id]` | `fTransactions[account_id]` | 1:* | Única |
| `dDate[Date]` | `fTransactions[transaction_date]` | 1:* | Única |
| `dChannel[channel]` | `fTransactions[channel]` | 1:* | Única |

Evite relacionamentos bidirecionais. A tabela `dRule` fica desconectada porque as regras estão armazenadas como colunas binárias na fato.

## Transformações no Power Query

1. Defina `timestamp` como Data/Hora.
2. Crie `transaction_date = Date.From([timestamp])`.
3. Defina valores e estatísticas como Número decimal.
4. Defina flags, contagens e score como Número inteiro.
5. Substitua nomes técnicos somente na camada de apresentação; preserve-os na origem.
6. Confirme que `transaction_id` é único e que `account_id` não contém nulos.

## Calendário DAX

```DAX
dDate =
ADDCOLUMNS (
    CALENDAR (
        MIN ( fTransactions[transaction_date] ),
        MAX ( fTransactions[transaction_date] )
    ),
    "Ano", YEAR ( [Date] ),
    "MesNumero", MONTH ( [Date] ),
    "Mes", FORMAT ( [Date], "mmm" ),
    "AnoMes", FORMAT ( [Date], "yyyy-MM" ),
    "Trimestre", "T" & FORMAT ( [Date], "Q" )
)
```

Ordene `Mes` por `MesNumero` e marque `dDate` como tabela de datas.

