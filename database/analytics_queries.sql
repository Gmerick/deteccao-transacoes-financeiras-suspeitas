-- 1. Resumo executivo da operação monitorada.
SELECT * FROM vw_executive_summary;

-- 2. Fila priorizada para investigação humana.
SELECT * FROM vw_alert_queue LIMIT 50;

-- 3. Canais com maior taxa de alertas.
SELECT * FROM vw_alerts_by_channel ORDER BY alert_rate_percent DESC;

-- 4. Desempenho individual das regras.
SELECT * FROM vw_rule_performance ORDER BY flagged DESC;

-- 5. Contas com mais alertas e valor financeiro associado.
SELECT
    account_id,
    COUNT(*) AS transactions,
    SUM(alert_flag) AS alerts,
    ROUND(SUM(CASE WHEN alert_flag = 1 THEN amount ELSE 0 END), 2) AS amount_in_alerts,
    MAX(risk_score) AS max_risk_score
FROM transactions_scored
GROUP BY account_id
HAVING SUM(alert_flag) > 0
ORDER BY alerts DESC, amount_in_alerts DESC
LIMIT 25;

-- 6. Evolução mensal e variação contra o mês anterior.
WITH monthly AS (
    SELECT
        month,
        transactions,
        alerts,
        alert_rate,
        LAG(alerts) OVER (ORDER BY month) AS previous_alerts
    FROM monthly_monitoring
)
SELECT
    *,
    ROUND(100.0 * (alerts - previous_alerts) / NULLIF(previous_alerts, 0), 2) AS alerts_change_percent
FROM monthly
ORDER BY month;

-- 7. Distribuição por nível de risco.
SELECT
    risk_level,
    COUNT(*) AS transactions,
    ROUND(SUM(amount), 2) AS amount,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS share_percent
FROM transactions_scored
GROUP BY risk_level
ORDER BY CASE risk_level WHEN 'Critico' THEN 1 WHEN 'Alto' THEN 2 WHEN 'Medio' THEN 3 ELSE 4 END;

-- 8. Alertas por hora do dia.
SELECT
    hour,
    COUNT(*) AS transactions,
    SUM(alert_flag) AS alerts,
    ROUND(100.0 * SUM(alert_flag) / NULLIF(COUNT(*), 0), 2) AS alert_rate_percent
FROM transactions_scored
GROUP BY hour
ORDER BY hour;

-- 9. Combinações de regras mais frequentes.
SELECT
    triggered_rules,
    COUNT(*) AS alerts,
    ROUND(AVG(risk_score), 2) AS average_score,
    ROUND(SUM(amount), 2) AS amount_in_alerts
FROM transactions_scored
WHERE alert_flag = 1
GROUP BY triggered_rules
ORDER BY alerts DESC
LIMIT 20;

-- 10. Alertas envolvendo dispositivo novo e divergência geográfica.
SELECT
    transaction_id,
    timestamp,
    account_id,
    home_state,
    transaction_state,
    device_id,
    amount,
    risk_score
FROM transactions_scored
WHERE rule_new_device_location = 1
ORDER BY risk_score DESC, amount DESC;

-- 11. Potencial fracionamento em janela de 24 horas.
SELECT
    account_id,
    DATE(timestamp) AS transaction_date,
    COUNT(*) AS transactions,
    ROUND(SUM(amount), 2) AS total_amount,
    MAX(transactions_24h) AS max_transactions_24h
FROM transactions_scored
WHERE rule_structuring = 1
GROUP BY account_id, DATE(timestamp)
ORDER BY transactions DESC, total_amount DESC;

-- 12. Matriz de avaliação global das regras contra os cenários simulados.
SELECT
    SUM(CASE WHEN alert_flag = 1 AND is_suspicious_simulated = 1 THEN 1 ELSE 0 END) AS true_positives,
    SUM(CASE WHEN alert_flag = 1 AND is_suspicious_simulated = 0 THEN 1 ELSE 0 END) AS false_positives,
    SUM(CASE WHEN alert_flag = 0 AND is_suspicious_simulated = 1 THEN 1 ELSE 0 END) AS false_negatives,
    SUM(CASE WHEN alert_flag = 0 AND is_suspicious_simulated = 0 THEN 1 ELSE 0 END) AS true_negatives
FROM transactions_scored;

