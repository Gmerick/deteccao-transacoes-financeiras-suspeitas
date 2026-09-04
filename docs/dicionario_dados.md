# Dicionário de dados

## Dados de entrada

| Campo | Tipo | Descrição |
|---|---|---|
| `transaction_id` | texto | Identificador único da transação |
| `timestamp` | data/hora | Momento da operação |
| `account_id` | texto | Identificador sintético da conta |
| `transaction_type` | texto | PIX, Cartão, Transferência, Boleto ou Saque |
| `channel` | texto | App, Internet Banking, POS, E-commerce, Carteira digital ou ATM |
| `amount` | decimal | Valor da transação em reais |
| `transaction_state` | texto | UF onde a operação foi registrada |
| `device_id` | texto | Identificador sintético do dispositivo |
| `device_trusted` | inteiro | 1 para dispositivo conhecido; 0 para novo |
| `merchant_category` | texto | Categoria do estabelecimento |
| `merchant_id` | texto | Identificador sintético do estabelecimento |
| `is_suspicious_simulated` | inteiro | Rótulo conhecido do cenário educacional |
| `suspicious_pattern` | texto | Cenário injetado ou Normal |
| `customer_age` | inteiro | Idade sintética do cliente |
| `home_state` | texto | UF habitual da conta |
| `monthly_income` | decimal | Renda mensal sintética |
| `account_age_days` | inteiro | Idade da conta em dias |
| `typical_amount` | decimal | Valor típico usado na simulação |
| `customer_segment` | texto | Segmento sintético da conta |

## Atributos e resultados

| Campo | Tipo | Descrição |
|---|---|---|
| `customer_amount_mean` | decimal | Média de valor por conta |
| `customer_amount_std` | decimal | Desvio-padrão de valor por conta |
| `customer_amount_median` | decimal | Mediana de valor por conta |
| `amount_zscore` | decimal | Distância padronizada do valor |
| `transactions_1h` | inteiro | Operações da conta na janela móvel de 1h |
| `transactions_24h` | inteiro | Operações da conta na janela móvel de 24h |
| `hour` | inteiro | Hora da operação |
| `day_of_week` | texto | Dia da semana |
| `month` | texto | Competência `AAAA-MM` |
| `location_mismatch` | inteiro | Divergência entre UF habitual e transacional |
| `rule_*` | inteiro | Resultado binário de cada regra |
| `risk_score` | inteiro | Score explicável de 0 a 100 |
| `alert_flag` | inteiro | 1 quando score ≥ 20 |
| `risk_level` | texto | Baixo, Médio, Alto ou Crítico |
| `triggered_rules` | texto | Lista das regras acionadas |

