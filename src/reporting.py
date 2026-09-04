"""Exporta tabelas analíticas, métricas e visualizações do projeto."""

from __future__ import annotations

import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from .config import DATA_PROCESSED, FIGURES, REPORTS, SCORE_WEIGHTS
from .detector import calculate_metrics


RULE_LABELS = {
    "rule_amount_zscore": "Valor atípico (z-score)",
    "rule_high_value": "Alto valor absoluto",
    "rule_velocity_1h": "Alta velocidade",
    "rule_unusual_hour": "Horário incomum",
    "rule_new_device_location": "Novo dispositivo + local",
    "rule_round_amount": "Valor arredondado",
    "rule_structuring": "Possível fracionamento",
}


def export_outputs(data: pd.DataFrame) -> dict[str, float | int]:
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    metrics = calculate_metrics(data)
    data.to_csv(DATA_PROCESSED / "transactions_scored.csv", index=False)
    data[data["alert_flag"] == 1].sort_values("risk_score", ascending=False).to_csv(
        DATA_PROCESSED / "alerts_prioritized.csv", index=False
    )
    rule_summary = pd.DataFrame(
        {
            "rule": [RULE_LABELS[rule] for rule in SCORE_WEIGHTS],
            "transactions_flagged": [int(data[rule].sum()) for rule in SCORE_WEIGHTS],
            "weight": list(SCORE_WEIGHTS.values()),
        }
    )
    rule_summary.to_csv(DATA_PROCESSED / "rule_summary.csv", index=False)
    monthly = data.groupby("month", as_index=False).agg(
        transactions=("transaction_id", "count"),
        alerts=("alert_flag", "sum"),
        suspicious_simulated=("is_suspicious_simulated", "sum"),
        monitored_amount=("amount", "sum"),
        alert_amount=("amount", lambda series: data.loc[series.index, "amount"].where(data.loc[series.index, "alert_flag"].eq(1), 0).sum()),
    )
    monthly["alert_rate"] = monthly["alerts"] / monthly["transactions"]
    monthly.to_csv(DATA_PROCESSED / "monthly_monitoring.csv", index=False)
    with (REPORTS / "metrics.json").open("w", encoding="utf-8") as file:
        json.dump(metrics, file, indent=2, ensure_ascii=False)
    return metrics


def _style() -> None:
    sns.set_theme(style="whitegrid")
    plt.rcParams.update({"font.family": "DejaVu Sans", "axes.titleweight": "bold", "figure.facecolor": "#F8FAFC"})


def create_figures(data: pd.DataFrame, metrics: dict[str, float | int]) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    _style()
    colors = {"navy": "#0F172A", "blue": "#2563EB", "cyan": "#0891B2", "amber": "#F59E0B", "red": "#DC2626", "green": "#16A34A"}

    fig = plt.figure(figsize=(16, 9), constrained_layout=True)
    grid = fig.add_gridspec(3, 4, height_ratios=[0.8, 2.1, 2.1])
    fig.suptitle("Monitoramento de Transações Financeiras", fontsize=22, fontweight="bold", color=colors["navy"])
    kpis = [
        ("Transações", f"{int(metrics['transactions']):,}".replace(",", ".")),
        ("Alertas", f"{int(metrics['alerts']):,}".replace(",", ".")),
        ("Taxa de alertas", f"{float(metrics['alert_rate']):.2%}".replace(".", ",")),
        ("Recall simulado", f"{float(metrics['recall']):.1%}".replace(".", ",")),
    ]
    for col, (label, value) in enumerate(kpis):
        ax = fig.add_subplot(grid[0, col])
        ax.set_facecolor("white")
        ax.text(0.05, 0.72, label.upper(), fontsize=10, color="#64748B", transform=ax.transAxes)
        ax.text(0.05, 0.25, value, fontsize=24, fontweight="bold", color=colors["navy"], transform=ax.transAxes)
        ax.set_xticks([]); ax.set_yticks([])
        for spine in ax.spines.values(): spine.set_color("#CBD5E1")

    ax_rules = fig.add_subplot(grid[1, :2])
    rule_counts = pd.Series({RULE_LABELS[rule]: int(data[rule].sum()) for rule in SCORE_WEIGHTS}).sort_values()
    rule_bars = ax_rules.barh(rule_counts.index, rule_counts.values, color=colors["blue"])
    ax_rules.bar_label(rule_bars, padding=4, fmt="{:,.0f}")
    ax_rules.set_title("Acionamentos por regra")
    ax_rules.set_xlabel("Transações sinalizadas")

    ax_risk = fig.add_subplot(grid[1, 2:])
    risk_order = ["Baixo", "Medio", "Alto", "Critico"]
    risk_counts = data["risk_level"].value_counts().reindex(risk_order, fill_value=0)
    risk_bars = ax_risk.bar(risk_counts.index, risk_counts.values, color=[colors["green"], colors["cyan"], colors["amber"], colors["red"]])
    ax_risk.bar_label(risk_bars, padding=3, fmt="{:,.0f}")
    ax_risk.set_yscale("log")
    ax_risk.set_ylim(20, 120_000)
    ax_risk.set_title("Distribuição por nível de risco (escala log)")
    ax_risk.set_ylabel("Transações")

    ax_month = fig.add_subplot(grid[2, :2])
    monthly = data.groupby("month")["alert_flag"].sum()
    ax_month.plot(monthly.index, monthly.values, marker="o", linewidth=2.5, color=colors["red"])
    ax_month.set_title("Alertas por mês")
    ax_month.tick_params(axis="x", rotation=35)
    ax_month.set_ylabel("Alertas")

    ax_channel = fig.add_subplot(grid[2, 2:])
    channel = data.groupby("channel")["alert_flag"].mean().sort_values()
    ax_channel.barh(channel.index, channel.values * 100, color=colors["cyan"])
    ax_channel.set_title("Taxa de alertas por canal")
    ax_channel.set_xlabel("Alertas (%)")
    fig.savefig(REPORTS / "dashboard_preview.png", dpi=170, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(11, 6))
    plot_data = data.assign(amount_log=np.log10(data["amount"].clip(lower=1)))
    sns.histplot(data=plot_data, x="amount_log", hue="alert_flag", bins=45, stat="density", common_norm=False, ax=ax, palette={0: colors["blue"], 1: colors["red"]})
    ax.set_title("Distribuição do valor das transações: alertas x demais")
    ax.set_xlabel("Valor da transação (escala log10)")
    fig.savefig(FIGURES / "amount_distribution.png", dpi=160, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(12, 6))
    heat = pd.crosstab(data["hour"], data["day_of_week"], values=data["alert_flag"], aggfunc="mean").fillna(0) * 100
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    heat = heat.reindex(columns=days)
    sns.heatmap(heat, cmap="YlOrRd", ax=ax, cbar_kws={"label": "Taxa de alertas (%)"})
    ax.set_title("Mapa de calor da taxa de alertas por hora e dia")
    ax.set_xlabel("Dia da semana"); ax.set_ylabel("Hora")
    fig.savefig(FIGURES / "alerts_heatmap.png", dpi=160, bbox_inches="tight")
    plt.close(fig)

    matrix = np.array([[metrics["true_negatives"], metrics["false_positives"]], [metrics["false_negatives"], metrics["true_positives"]]])
    fig, ax = plt.subplots(figsize=(7, 6))
    sns.heatmap(matrix, annot=True, fmt=",.0f", cmap="Blues", cbar=False, ax=ax, xticklabels=["Sem alerta", "Alerta"], yticklabels=["Normal", "Suspeita simulada"])
    ax.set_title("Matriz de avaliação das regras")
    ax.set_xlabel("Classificação das regras"); ax.set_ylabel("Cenário conhecido")
    fig.savefig(FIGURES / "confusion_matrix.png", dpi=160, bbox_inches="tight")
    plt.close(fig)
