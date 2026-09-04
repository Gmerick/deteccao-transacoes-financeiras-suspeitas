import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.database import build_database
from src.detector import calculate_metrics, detect_suspicious_transactions
from src.generate_data import generate_dataset
from src.reporting import export_outputs


class SuspiciousTransactionPipelineTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        generated = generate_dataset(save=False)
        cls.customers = generated.customers
        cls.transactions = generated.transactions
        cls.scored = detect_suspicious_transactions(cls.transactions, cls.customers)
        cls.metrics = calculate_metrics(cls.scored)

    def test_dataset_dimensions_and_labels(self):
        self.assertEqual(len(self.customers), 2_500)
        self.assertEqual(len(self.transactions), 50_000)
        self.assertEqual(int(self.transactions["is_suspicious_simulated"].sum()), 2_000)
        self.assertEqual(self.transactions["transaction_id"].nunique(), 50_000)

    def test_amounts_and_score_bounds(self):
        self.assertTrue((self.scored["amount"] >= 0).all())
        self.assertTrue(self.scored["risk_score"].between(0, 100).all())

    def test_detection_has_useful_signal(self):
        self.assertGreater(self.metrics["recall"], 0.65)
        self.assertGreater(self.metrics["precision"], 0.55)
        self.assertGreater(self.metrics["f1_score"], 0.60)

    def test_high_risk_transactions_are_alerts(self):
        high_risk = self.scored[self.scored["risk_level"].isin(["Alto", "Critico"])]
        self.assertTrue((high_risk["alert_flag"] == 1).all())

    def test_funnel_has_multiple_rule_types(self):
        triggered_rules = [column for column in self.scored if column.startswith("rule_")]
        self.assertEqual(len(triggered_rules), 7)
        self.assertTrue(all(self.scored[column].sum() > 0 for column in triggered_rules))

    def test_sql_views(self):
        export_outputs(self.scored)
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "test.db"
            build_database(path)
            with sqlite3.connect(path) as connection:
                transaction_count = connection.execute("SELECT COUNT(*) FROM transactions_scored").fetchone()[0]
                alert_count = connection.execute("SELECT alerts FROM vw_executive_summary").fetchone()[0]
                channel_count = connection.execute("SELECT COUNT(*) FROM vw_alerts_by_channel").fetchone()[0]
            self.assertEqual(transaction_count, 50_000)
            self.assertEqual(alert_count, self.metrics["alerts"])
            self.assertGreaterEqual(channel_count, 5)


if __name__ == "__main__":
    unittest.main()

