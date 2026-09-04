DROP VIEW IF EXISTS vw_executive_summary;
CREATE VIEW vw_executive_summary AS
SELECT
    COUNT(*) AS transactions,
    ROUND(SUM(amount), 2) AS monitored_amount,
    SUM(alert_flag) AS alerts,
    ROUND(100.0 * SUM(alert_flag) / NULLIF(COUNT(*), 0), 2) AS alert_rate_percent,
    ROUND(SUM(CASE WHEN alert_flag = 1 THEN amount ELSE 0 END), 2) AS amount_in_alerts,
    COUNT(DISTINCT CASE WHEN alert_flag = 1 THEN account_id END) AS accounts_with_alerts,
    ROUND(AVG(CASE WHEN alert_flag = 1 THEN risk_score END), 2) AS average_alert_score
FROM transactions_scored;

DROP VIEW IF EXISTS vw_alerts_by_channel;
CREATE VIEW vw_alerts_by_channel AS
SELECT
    channel,
    COUNT(*) AS transactions,
    SUM(alert_flag) AS alerts,
    ROUND(100.0 * SUM(alert_flag) / NULLIF(COUNT(*), 0), 2) AS alert_rate_percent,
    ROUND(SUM(amount), 2) AS monitored_amount,
    ROUND(SUM(CASE WHEN alert_flag = 1 THEN amount ELSE 0 END), 2) AS amount_in_alerts
FROM transactions_scored
GROUP BY channel;

DROP VIEW IF EXISTS vw_alert_queue;
CREATE VIEW vw_alert_queue AS
SELECT
    transaction_id,
    timestamp,
    account_id,
    transaction_type,
    channel,
    amount,
    risk_score,
    risk_level,
    triggered_rules,
    suspicious_pattern
FROM transactions_scored
WHERE alert_flag = 1
ORDER BY risk_score DESC, amount DESC;

DROP VIEW IF EXISTS vw_rule_performance;
CREATE VIEW vw_rule_performance AS
WITH unpivot AS (
    SELECT 'Valor atípico (z-score)' AS rule, rule_amount_zscore AS triggered, is_suspicious_simulated FROM transactions_scored
    UNION ALL SELECT 'Alto valor absoluto', rule_high_value, is_suspicious_simulated FROM transactions_scored
    UNION ALL SELECT 'Alta velocidade', rule_velocity_1h, is_suspicious_simulated FROM transactions_scored
    UNION ALL SELECT 'Horário incomum', rule_unusual_hour, is_suspicious_simulated FROM transactions_scored
    UNION ALL SELECT 'Novo dispositivo + local', rule_new_device_location, is_suspicious_simulated FROM transactions_scored
    UNION ALL SELECT 'Valor arredondado', rule_round_amount, is_suspicious_simulated FROM transactions_scored
    UNION ALL SELECT 'Possível fracionamento', rule_structuring, is_suspicious_simulated FROM transactions_scored
)
SELECT
    rule,
    SUM(triggered) AS flagged,
    SUM(CASE WHEN triggered = 1 AND is_suspicious_simulated = 1 THEN 1 ELSE 0 END) AS true_positives,
    ROUND(100.0 * SUM(CASE WHEN triggered = 1 AND is_suspicious_simulated = 1 THEN 1 ELSE 0 END)
        / NULLIF(SUM(triggered), 0), 2) AS precision_percent
FROM unpivot
GROUP BY rule;

