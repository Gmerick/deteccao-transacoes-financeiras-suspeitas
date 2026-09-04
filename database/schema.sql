PRAGMA foreign_keys = ON;

CREATE TABLE transactions_scored (
    transaction_id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    account_id TEXT NOT NULL,
    transaction_type TEXT NOT NULL,
    channel TEXT NOT NULL,
    amount REAL NOT NULL CHECK (amount >= 0),
    transaction_state TEXT NOT NULL,
    device_id TEXT NOT NULL,
    device_trusted INTEGER NOT NULL CHECK (device_trusted IN (0, 1)),
    merchant_category TEXT NOT NULL,
    merchant_id TEXT NOT NULL,
    is_suspicious_simulated INTEGER NOT NULL CHECK (is_suspicious_simulated IN (0, 1)),
    suspicious_pattern TEXT NOT NULL,
    customer_age INTEGER NOT NULL,
    home_state TEXT NOT NULL,
    monthly_income REAL NOT NULL CHECK (monthly_income >= 0),
    account_age_days INTEGER NOT NULL CHECK (account_age_days >= 0),
    typical_amount REAL NOT NULL CHECK (typical_amount >= 0),
    customer_segment TEXT NOT NULL,
    customer_amount_mean REAL NOT NULL,
    customer_amount_std REAL NOT NULL,
    customer_amount_median REAL NOT NULL,
    amount_zscore REAL NOT NULL,
    transactions_1h INTEGER NOT NULL,
    transactions_24h INTEGER NOT NULL,
    hour INTEGER NOT NULL CHECK (hour BETWEEN 0 AND 23),
    day_of_week TEXT NOT NULL,
    month TEXT NOT NULL,
    location_mismatch INTEGER NOT NULL CHECK (location_mismatch IN (0, 1)),
    rule_amount_zscore INTEGER NOT NULL CHECK (rule_amount_zscore IN (0, 1)),
    rule_high_value INTEGER NOT NULL CHECK (rule_high_value IN (0, 1)),
    rule_velocity_1h INTEGER NOT NULL CHECK (rule_velocity_1h IN (0, 1)),
    rule_unusual_hour INTEGER NOT NULL CHECK (rule_unusual_hour IN (0, 1)),
    rule_new_device_location INTEGER NOT NULL CHECK (rule_new_device_location IN (0, 1)),
    rule_round_amount INTEGER NOT NULL CHECK (rule_round_amount IN (0, 1)),
    rule_structuring INTEGER NOT NULL CHECK (rule_structuring IN (0, 1)),
    risk_score INTEGER NOT NULL CHECK (risk_score BETWEEN 0 AND 100),
    alert_flag INTEGER NOT NULL CHECK (alert_flag IN (0, 1)),
    risk_level TEXT NOT NULL CHECK (risk_level IN ('Baixo', 'Medio', 'Alto', 'Critico')),
    triggered_rules TEXT NOT NULL
);

CREATE TABLE rule_summary (
    rule TEXT PRIMARY KEY,
    transactions_flagged INTEGER NOT NULL CHECK (transactions_flagged >= 0),
    weight INTEGER NOT NULL CHECK (weight BETWEEN 0 AND 100)
);

CREATE TABLE monthly_monitoring (
    month TEXT PRIMARY KEY,
    transactions INTEGER NOT NULL,
    alerts INTEGER NOT NULL,
    suspicious_simulated INTEGER NOT NULL,
    monitored_amount REAL NOT NULL,
    alert_amount REAL NOT NULL,
    alert_rate REAL NOT NULL
);

CREATE INDEX idx_transactions_account_time ON transactions_scored(account_id, timestamp);
CREATE INDEX idx_transactions_alert_score ON transactions_scored(alert_flag, risk_score DESC);
CREATE INDEX idx_transactions_channel ON transactions_scored(channel);
CREATE INDEX idx_transactions_pattern ON transactions_scored(suspicious_pattern);
