"""Gera clientes e transações sintéticas com cenários suspeitos conhecidos."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from .config import (
    DATA_RAW,
    N_CUSTOMERS,
    N_TRANSACTIONS,
    RANDOM_SEED,
    SIMULATED_SUSPICIOUS_RATE,
)


STATES = np.array(["SP", "RJ", "MG", "PR", "RS", "SC", "BA", "PE", "GO", "DF"])
STATE_WEIGHTS = np.array([0.35, 0.12, 0.12, 0.08, 0.07, 0.05, 0.07, 0.05, 0.05, 0.04])
TRANSACTION_TYPES = np.array(["PIX", "Cartao", "Transferencia", "Boleto", "Saque"])
TYPE_WEIGHTS = np.array([0.34, 0.38, 0.13, 0.10, 0.05])
CHANNELS = {
    "PIX": ["App", "Internet Banking"],
    "Cartao": ["POS", "E-commerce", "Carteira digital"],
    "Transferencia": ["App", "Internet Banking"],
    "Boleto": ["App", "Internet Banking"],
    "Saque": ["ATM"],
}
MERCHANT_CATEGORIES = np.array(
    ["Mercado", "Restaurante", "Transporte", "Eletronicos", "Servicos", "Viagem", "Outros"]
)


@dataclass(frozen=True)
class GenerationResult:
    customers: pd.DataFrame
    transactions: pd.DataFrame


def _sample_timestamps(rng: np.random.Generator, size: int) -> pd.Series:
    start = datetime(2025, 1, 1)
    day_offsets = rng.integers(0, 365, size=size)
    hour_options = np.arange(24)
    hour_weights = np.array(
        [0.008, 0.006, 0.005, 0.005, 0.007, 0.012, 0.025, 0.045, 0.055, 0.060, 0.065, 0.070,
         0.075, 0.070, 0.065, 0.065, 0.068, 0.072, 0.070, 0.060, 0.045, 0.030, 0.020, 0.012]
    )
    hour_weights = hour_weights / hour_weights.sum()
    hours = rng.choice(hour_options, size=size, p=hour_weights)
    minutes = rng.integers(0, 60, size=size)
    seconds = rng.integers(0, 60, size=size)
    return pd.Series(
        [start + timedelta(days=int(d), hours=int(h), minutes=int(m), seconds=int(s))
         for d, h, m, s in zip(day_offsets, hours, minutes, seconds)],
        dtype="datetime64[ns]",
    )


def generate_customers(rng: np.random.Generator) -> pd.DataFrame:
    customer_ids = [f"ACC-{number:05d}" for number in range(1, N_CUSTOMERS + 1)]
    income = np.round(rng.lognormal(mean=8.25, sigma=0.65, size=N_CUSTOMERS), 2)
    typical_amount = np.round(np.clip(income * rng.uniform(0.025, 0.16, N_CUSTOMERS), 35, 4_500), 2)
    customers = pd.DataFrame(
        {
            "account_id": customer_ids,
            "customer_age": rng.integers(18, 78, N_CUSTOMERS),
            "home_state": rng.choice(STATES, N_CUSTOMERS, p=STATE_WEIGHTS),
            "monthly_income": income,
            "account_age_days": rng.integers(30, 5_000, N_CUSTOMERS),
            "typical_amount": typical_amount,
            "customer_segment": rng.choice(
                ["Varejo", "Alta renda", "Digital", "Empresarial"],
                N_CUSTOMERS,
                p=[0.50, 0.15, 0.25, 0.10],
            ),
        }
    )
    return customers


def _base_transactions(rng: np.random.Generator, customers: pd.DataFrame) -> pd.DataFrame:
    account_indices = rng.integers(0, len(customers), N_TRANSACTIONS)
    selected = customers.iloc[account_indices].reset_index(drop=True)
    transaction_types = rng.choice(TRANSACTION_TYPES, N_TRANSACTIONS, p=TYPE_WEIGHTS)
    channels = [rng.choice(CHANNELS[tx_type]) for tx_type in transaction_types]
    amount_multiplier = rng.lognormal(mean=-0.12, sigma=0.72, size=N_TRANSACTIONS)
    amounts = np.round(np.clip(selected["typical_amount"].to_numpy() * amount_multiplier, 5, 18_000), 2)
    same_state = rng.random(N_TRANSACTIONS) < 0.92
    transaction_states = np.where(same_state, selected["home_state"], rng.choice(STATES, N_TRANSACTIONS, p=STATE_WEIGHTS))
    trusted_device = rng.random(N_TRANSACTIONS) < 0.93
    known_device = [f"DEV-{account[-5:]}-A" for account in selected["account_id"]]
    new_device = [f"NEW-{number:07d}" for number in rng.integers(0, 9_999_999, N_TRANSACTIONS)]

    transactions = pd.DataFrame(
        {
            "transaction_id": [f"TX-{number:07d}" for number in range(1, N_TRANSACTIONS + 1)],
            "timestamp": _sample_timestamps(rng, N_TRANSACTIONS),
            "account_id": selected["account_id"].to_numpy(),
            "transaction_type": transaction_types,
            "channel": channels,
            "amount": amounts,
            "transaction_state": transaction_states,
            "device_id": np.where(trusted_device, known_device, new_device),
            "device_trusted": trusted_device.astype(int),
            "merchant_category": rng.choice(MERCHANT_CATEGORIES, N_TRANSACTIONS),
            "merchant_id": [f"MER-{number:04d}" for number in rng.integers(1, 1_201, N_TRANSACTIONS)],
            "is_suspicious_simulated": 0,
            "suspicious_pattern": "Normal",
        }
    )
    return transactions


def _inject_suspicious_patterns(
    rng: np.random.Generator, transactions: pd.DataFrame, customers: pd.DataFrame
) -> pd.DataFrame:
    data = transactions.copy()
    total = int(round(len(data) * SIMULATED_SUSPICIOUS_RATE))
    candidates = rng.choice(data.index.to_numpy(), size=total, replace=False)
    groups = {
        "Valor atipico": candidates[:500],
        "Horario incomum": candidates[500:850],
        "Alta velocidade": candidates[850:1_350],
        "Novo dispositivo e local": candidates[1_350:1_700],
        "Fracionamento": candidates[1_700:2_000],
    }
    customer_lookup = customers.set_index("account_id")

    for pattern, indexes in groups.items():
        data.loc[indexes, "is_suspicious_simulated"] = 1
        data.loc[indexes, "suspicious_pattern"] = pattern

    high_idx = groups["Valor atipico"]
    typical = data.loc[high_idx, "account_id"].map(customer_lookup["typical_amount"])
    data.loc[high_idx, "amount"] = np.round(np.maximum(15_500, typical * rng.uniform(9, 18, len(high_idx))), 2)

    night_idx = groups["Horario incomum"]
    night_dates = pd.to_datetime(data.loc[night_idx, "timestamp"]).dt.normalize()
    night_hours = pd.to_timedelta(rng.integers(0, 5, len(night_idx)), unit="h")
    night_minutes = pd.to_timedelta(rng.integers(0, 60, len(night_idx)), unit="m")
    data.loc[night_idx, "timestamp"] = (night_dates + night_hours + night_minutes).to_numpy()
    night_typical = data.loc[night_idx, "account_id"].map(customer_lookup["typical_amount"])
    data.loc[night_idx, "amount"] = np.round(np.maximum(data.loc[night_idx, "amount"], night_typical * 3.2), 2)

    velocity_idx = groups["Alta velocidade"]
    for batch in np.array_split(velocity_idx, len(velocity_idx) // 5):
        anchor = int(batch[0])
        account = data.at[anchor, "account_id"]
        base_time = pd.Timestamp(data.at[anchor, "timestamp"]).floor("h")
        data.loc[batch, "account_id"] = account
        data.loc[batch, "timestamp"] = [base_time + pd.Timedelta(minutes=minute) for minute in range(len(batch))]
        data.loc[batch, "device_id"] = data.at[anchor, "device_id"]

    geo_idx = groups["Novo dispositivo e local"]
    data.loc[geo_idx, "device_trusted"] = 0
    data.loc[geo_idx, "device_id"] = [f"RISK-{number:07d}" for number in rng.integers(0, 9_999_999, len(geo_idx))]
    for idx in geo_idx:
        home = customer_lookup.at[data.at[idx, "account_id"], "home_state"]
        alternatives = STATES[STATES != home]
        data.at[idx, "transaction_state"] = rng.choice(alternatives)

    struct_idx = groups["Fracionamento"]
    for batch in np.array_split(struct_idx, len(struct_idx) // 5):
        anchor = int(batch[0])
        account = data.at[anchor, "account_id"]
        base_time = pd.Timestamp(data.at[anchor, "timestamp"]).floor("D") + pd.Timedelta(hours=10)
        data.loc[batch, "account_id"] = account
        data.loc[batch, "timestamp"] = [base_time + pd.Timedelta(hours=hour) for hour in range(len(batch))]
        data.loc[batch, "amount"] = rng.choice([3_000.0, 3_500.0, 4_000.0, 4_500.0], len(batch))
        data.loc[batch, "transaction_type"] = "PIX"
        data.loc[batch, "channel"] = "App"

    return data.sort_values("timestamp").reset_index(drop=True)


def generate_dataset(seed: int = RANDOM_SEED, save: bool = True) -> GenerationResult:
    rng = np.random.default_rng(seed)
    customers = generate_customers(rng)
    transactions = _base_transactions(rng, customers)
    transactions = _inject_suspicious_patterns(rng, transactions, customers)
    if save:
        DATA_RAW.mkdir(parents=True, exist_ok=True)
        customers.to_csv(DATA_RAW / "customers.csv", index=False)
        transactions.to_csv(DATA_RAW / "transactions.csv", index=False)
    return GenerationResult(customers=customers, transactions=transactions)


if __name__ == "__main__":
    result = generate_dataset()
    print(f"Clientes: {len(result.customers):,}")
    print(f"Transações: {len(result.transactions):,}")
    print(f"Cenários suspeitos: {result.transactions['is_suspicious_simulated'].sum():,}")

