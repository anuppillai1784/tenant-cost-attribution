import unittest

from cost_attribution.attribution import price_events, reconcile
from cost_attribution.prices import DEFAULT_PRICE_VERSIONS
from cost_attribution.report import build_report, format_micros
from cost_attribution.synthetic import demo_days, generate_events

AS_OF = demo_days()[-1]
DAYS_IN_MONTH = 30
BUDGETS = {"tenant-alder": 1, "tenant-birch": 10**12}


class FormatMicrosTest(unittest.TestCase):
    def test_micros_render_as_dollars_with_six_decimals(self):
        self.assertEqual(format_micros(1_234_567), "$1.234567")
        self.assertEqual(format_micros(7), "$0.000007")


class BuildReportTest(unittest.TestCase):
    def setUp(self):
        self.priced = price_events(generate_events(), DEFAULT_PRICE_VERSIONS)
        self.report = build_report(self.priced, reconcile(self.priced), BUDGETS, AS_OF)

    def test_report_holds_exact_total_and_reconciled_flag(self):
        self.assertEqual(self.report["total_micros"], sum(item.cost_micros for item in self.priced))
        self.assertTrue(self.report["reconciled_exact"])

    def test_report_splits_totals_by_each_dimension(self):
        self.assertEqual(set(self.report["totals"]), {"tenant", "department", "feature"})
        for totals in self.report["totals"].values():
            self.assertEqual(sum(totals.values()), self.report["total_micros"])

    def test_budget_projection_scales_spend_to_month_end(self):
        budget = self.report["budgets"]["tenant-birch"]
        spent = self.report["totals"]["tenant"]["tenant-birch"]
        self.assertEqual(budget["spend_to_date_micros"], spent)
        self.assertEqual(budget["projected_micros"], spent * DAYS_IN_MONTH // len(demo_days()))
        self.assertFalse(budget["over_budget"])

    def test_tiny_budget_is_over_budget(self):
        self.assertTrue(self.report["budgets"]["tenant-alder"]["over_budget"])


if __name__ == "__main__":
    unittest.main()
