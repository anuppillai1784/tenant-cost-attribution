import unittest

from cost_attribution.budgets import project_month

SEPTEMBER_LIMIT = 25_000_000


class ProjectMonthTest(unittest.TestCase):
    def test_projection_scales_month_to_date_spend_to_full_month(self):
        projection = project_month(
            spend_to_date_micros=10_000_000,
            as_of_day="2026-09-10",
            limit_micros=SEPTEMBER_LIMIT,
        )
        self.assertEqual(projection.projected_micros, 30_000_000)

    def test_projection_above_limit_is_over_budget(self):
        projection = project_month(10_000_000, "2026-09-10", SEPTEMBER_LIMIT)
        self.assertTrue(projection.over_budget)

    def test_projection_equal_to_limit_is_not_over_budget(self):
        projection = project_month(
            spend_to_date_micros=25_000_000,
            as_of_day="2026-09-30",
            limit_micros=SEPTEMBER_LIMIT,
        )
        self.assertFalse(projection.over_budget)


if __name__ == "__main__":
    unittest.main()
