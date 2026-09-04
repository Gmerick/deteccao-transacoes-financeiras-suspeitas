"""Executa geração, detecção, exportação, visualizações e banco SQL."""

from src.database import build_database
from src.detector import detect_suspicious_transactions
from src.generate_data import generate_dataset
from src.reporting import create_figures, export_outputs


def main() -> None:
    generated = generate_dataset()
    scored = detect_suspicious_transactions(generated.transactions, generated.customers)
    metrics = export_outputs(scored)
    create_figures(scored, metrics)
    build_database()
    print("Pipeline concluído")
    print(f"Transações: {metrics['transactions']:,}")
    print(f"Alertas: {metrics['alerts']:,} ({metrics['alert_rate']:.2%})")
    print(f"Precisão: {metrics['precision']:.2%} | Recall: {metrics['recall']:.2%} | F1: {metrics['f1_score']:.2%}")


if __name__ == "__main__":
    main()
