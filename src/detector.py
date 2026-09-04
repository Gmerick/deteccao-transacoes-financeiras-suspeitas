"""Regras estatísticas explicáveis e score de priorização de alertas."""

from __future__ import annotations

from collections import deque

import numpy as np
import pandas as pd

from .config import ALERT_THRESHOLD, SCORE_WEIGHTS


def _rolling_counts(group: pd.DataFrame, minutes: int) -> pd.Series:
    times = pd.to_datetime(group["timestamp"]).astype("int64").to_numpy()
    window = minutes * 60 * 1_000_000_000
    queue: deque[int] = deque()
    counts: list[int] = []
    for value in times:
        queue.append(int(value))
        while queue and int(value) - queue[0] > window:
            queue.popleft()
        counts.append(len(queue))
    return pd.Series(counts, index=group.index, dtype="int64")


def detect_suspicious_transactions(
    transactions: pd.DataFrame, customers: pd.DataFrame
) -> pd.DataFrame:
    data = transactions.copy()
    data["timestamp"] = pd.to_datetime(data["timestamp"])
    data = data.merge(customers, on="account_id", how="left", validate="many_to_one")
    data = data.sort_values(["account_id", "timestamp", "transaction_id"]).reset_index(drop=True)

    stats = data.groupby("account_id")["amount"].agg(customer_amount_mean="mean", customer_amount_std="std", customer_amount_median="median")
    data = data.join(stats, on="account_id")
    data["customer_amount_std"] = data["customer_amount_std"].replace(0, np.nan).fillna(1)
    data["amount_zscore"] = (data["amount"] - data["customer_amount_mean"]) / data["customer_amount_std"]
    data["transactions_1h"] = (
        data.groupby("account_id", group_keys=False).apply(lambda group: _rolling_counts(group, 60), include_groups=False).sort_index()
    )
    data["transactions_24h"] = (
        data.groupby("account_id", group_keys=False).apply(lambda group: _rolling_counts(group, 1_440), include_groups=False).sort_index()
    )
    data["hour"] = data["timestamp"].dt.hour
    data["day_of_week"] = data["timestamp"].dt.day_name()
    data["month"] = data["timestamp"].dt.to_period("M").astype(str)
    data["location_mismatch"] = (data["transaction_state"] != data["home_state"]).astype(int)

    data["rule_amount_zscore"] = (data["amount_zscore"] >= 3.5).astype(int)
    data["rule_high_value"] = (data["amount"] >= 15_000).astype(int)
    data["rule_velocity_1h"] = (data["transactions_1h"] >= 3).astype(int)
    data["rule_unusual_hour"] = (
        data["hour"].between(0, 4) & (data["amount"] >= data["customer_amount_median"] * 2.5)
    ).astype(int)
    data["rule_new_device_location"] = (
        (data["device_trusted"] == 0) & (data["location_mismatch"] == 1)
    ).astype(int)
    data["rule_round_amount"] = (
        (data["amount"] >= 1_000) & np.isclose(data["amount"] % 1_000, 0, atol=0.01)
    ).astype(int)
    data["rule_structuring"] = (
        data["amount"].between(3_000, 4_500)
        & (data["transactions_24h"] >= 3)
        & (data["transaction_type"] == "PIX")
    ).astype(int)

    data["risk_score"] = 0
    for rule, weight in SCORE_WEIGHTS.items():
        data["risk_score"] += data[rule] * weight
    data["risk_score"] = data["risk_score"].clip(upper=100)
    data["alert_flag"] = (data["risk_score"] >= ALERT_THRESHOLD).astype(int)
    data["risk_level"] = pd.cut(
        data["risk_score"],
        bins=[-1, 9, 19, 49, 100],
        labels=["Baixo", "Medio", "Alto", "Critico"],
    ).astype(str)

    triggered = []
    for _, row in data[list(SCORE_WEIGHTS)].iterrows():
        names = [rule.removeprefix("rule_") for rule, value in row.items() if value == 1]
        triggered.append("; ".join(names) if names else "Nenhuma")
    data["triggered_rules"] = triggered
    return data.sort_values("timestamp").reset_index(drop=True)


def calculate_metrics(data: pd.DataFrame) -> dict[str, float | int]:
    actual = data["is_suspicious_simulated"] == 1
    predicted = data["alert_flag"] == 1
    tp = int((actual & predicted).sum())
    fp = int((~actual & predicted).sum())
    fn = int((actual & ~predicted).sum())
    tn = int((~actual & ~predicted).sum())
    precision = tp / (tp + fp) if tp + fp else 0
    recall = tp / (tp + fn) if tp + fn else 0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0
    return {
        "transactions": len(data),
        "simulated_suspicious": int(actual.sum()),
        "alerts": int(predicted.sum()),
        "alert_rate": float(predicted.mean()),
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "true_negatives": tn,
        "amount_monitored": float(data["amount"].sum()),
        "amount_in_alerts": float(data.loc[predicted, "amount"].sum()),
    }
