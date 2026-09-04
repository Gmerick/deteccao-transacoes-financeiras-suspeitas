from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
REPORTS = ROOT / "reports"
FIGURES = REPORTS / "figures"
DATABASE = ROOT / "database" / "fraud_detection.db"

RANDOM_SEED = 2026
N_CUSTOMERS = 2_500
N_TRANSACTIONS = 50_000
SIMULATED_SUSPICIOUS_RATE = 0.04

ALERT_THRESHOLD = 20
SCORE_WEIGHTS = {
    "rule_amount_zscore": 30,
    "rule_high_value": 20,
    "rule_velocity_1h": 25,
    "rule_unusual_hour": 20,
    "rule_new_device_location": 25,
    "rule_round_amount": 10,
    "rule_structuring": 20,
}
