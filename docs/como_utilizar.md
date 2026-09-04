# Como utilizar o projeto

## Pré-requisitos

- Python 3.10 ou superior;
- Power BI Desktop, opcional, para construir o relatório interativo;
- SQLite CLI ou extensão de banco, opcional, para explorar o banco.

## Instalação

```bash
git clone https://github.com/Gmerick/deteccao-transacoes-financeiras-suspeitas.git
cd deteccao-transacoes-financeiras-suspeitas
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python run_pipeline.py
```

Linux ou macOS:

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
python run_pipeline.py
```

## Saídas geradas

| Arquivo | Uso |
|---|---|
| `data/raw/customers.csv` | Perfis sintéticos das contas |
| `data/raw/transactions.csv` | Movimentações antes da pontuação |
| `data/processed/transactions_scored.csv` | Base completa para SQL e Power BI |
| `data/processed/alerts_prioritized.csv` | Fila pronta para investigação |
| `data/processed/rule_summary.csv` | Auditoria de regras e pesos |
| `data/processed/monthly_monitoring.csv` | Série mensal de monitoramento |
| `database/fraud_detection.db` | Banco SQLite local, não versionado |
| `reports/dashboard_preview.png` | Visão estática do dashboard |
| `reports/metrics.json` | Métricas da execução |

## Consultas SQL

```bash
sqlite3 database/fraud_detection.db
```

```sql
.headers on
.mode column
SELECT * FROM vw_executive_summary;
SELECT * FROM vw_alert_queue LIMIT 20;
SELECT * FROM vw_rule_performance;
.read database/analytics_queries.sql
```

## Power BI

1. Use **Obter dados → Texto/CSV**.
2. Importe `transactions_scored.csv`, `rule_summary.csv` e `monthly_monitoring.csv`.
3. Siga `powerbi/data_model.md`.
4. Crie as medidas de `powerbi/dax_measures.md`.
5. Importe `powerbi/theme_fraud_detection.json` em **Exibir → Temas**.
6. Construa as quatro páginas descritas em `powerbi/dashboard_layout.md`.

## Testes

```bash
python -m unittest discover -s tests -v
```

Os testes verificam dimensões, unicidade, limites de score, sinal mínimo da detecção, presença das sete regras e integridade das views SQL.

