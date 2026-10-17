import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout

from cost_attribution.cli import main


class CliTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db_path = os.path.join(self.tmp.name, "ledger.sqlite")
        self.out_dir = os.path.join(self.tmp.name, "out")
        os.makedirs(self.out_dir)

    def run_command(self, argv: list[str]) -> tuple[int, str]:
        output = io.StringIO()
        with redirect_stdout(output):
            code = main(argv)
        return code, output.getvalue()

    def test_demo_command_prints_summary_and_returns_zero(self):
        code, text = self.run_command(["demo", "--db", self.db_path, "--out", self.out_dir])
        self.assertEqual(code, 0)
        self.assertIn("Reconcile: EXACT", text)

    def test_reconcile_command_on_demo_ledger_returns_zero(self):
        self.run_command(["demo", "--db", self.db_path, "--out", self.out_dir])
        code, text = self.run_command(["reconcile", "--db", self.db_path])
        self.assertEqual(code, 0)
        self.assertIn("Reconcile: EXACT", text)


if __name__ == "__main__":
    unittest.main()
