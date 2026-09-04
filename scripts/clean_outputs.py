from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PROCESSED = ROOT / "data" / "processed"
FIGURES = ROOT / "reports" / "figures"
REPORTS = ROOT / "reports"
DATABASE = ROOT / "database" / "fraud_detection.db"


for path in DATA_PROCESSED.glob("*.csv"):
    path.unlink()
for path in FIGURES.glob("*.png"):
    path.unlink()
for path in [REPORTS / "dashboard_preview.png", REPORTS / "metrics.json", DATABASE]:
    if path.exists():
        path.unlink()
print("Artefatos gerados removidos.")
