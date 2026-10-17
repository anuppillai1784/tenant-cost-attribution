import json
import os
import tempfile
import unittest

from cost_attribution.demo import run_demo
from cost_attribution.synthetic import SPIKE_DAY, SPIKE_KEY


class RunDemoTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db_path = os.path.join(self.tmp.name, "ledger.sqlite")

    def run_into(self, name: str) -> tuple[str, str]:
        out_dir = os.path.join(self.tmp.name, name)
        os.makedirs(out_dir)
        stdout = run_demo(self.db_path, out_dir)
        return out_dir, stdout

    def test_demo_writes_report_and_alerts_and_reconciles(self):
        out_dir, stdout = self.run_into("first")
        with open(os.path.join(out_dir, "alerts.json"), encoding="utf-8") as handle:
            alerts = json.load(handle)
        self.assertEqual(
            [(alert["tenant"], alert["feature"], alert["day"]) for alert in alerts],
            [(SPIKE_KEY[0], SPIKE_KEY[1], SPIKE_DAY)],
        )
        self.assertTrue(os.path.isfile(os.path.join(out_dir, "report.json")))
        self.assertIn("Reconcile: EXACT", stdout)

    def test_rerun_on_same_database_gives_identical_outputs(self):
        first_dir, first_stdout = self.run_into("first")
        second_dir, second_stdout = self.run_into("second")
        self.assertEqual(first_stdout, second_stdout)
        for name in ("report.json", "alerts.json"):
            with open(os.path.join(first_dir, name), "rb") as first, open(
                os.path.join(second_dir, name), "rb"
            ) as second:
                self.assertEqual(first.read(), second.read(), name)


if __name__ == "__main__":
    unittest.main()
