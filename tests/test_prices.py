import unittest

from cost_attribution.prices import ModelRate, PriceVersion, price_micros

SMALL = "model-small"
OLD_RATE = ModelRate(input_micros_per_mtok=1_000_000, output_micros_per_mtok=2_000_000)
NEW_RATE = ModelRate(input_micros_per_mtok=2_000_000, output_micros_per_mtok=4_000_000)
VERSIONS = [
    PriceVersion(effective_from="2026-01-01", rates={SMALL: OLD_RATE}),
    PriceVersion(effective_from="2026-06-01", rates={SMALL: NEW_RATE}),
]


class PriceMicrosTest(unittest.TestCase):
    def test_cost_is_rate_times_tokens_per_million(self):
        cost = price_micros(VERSIONS, "2026-02-15", SMALL, 500_000, 250_000)
        self.assertEqual(cost, 1_000_000)

    def test_price_change_reprices_events_on_and_after_effective_day(self):
        before = price_micros(VERSIONS, "2026-05-31", SMALL, 500_000, 250_000)
        on_day = price_micros(VERSIONS, "2026-06-01", SMALL, 500_000, 250_000)
        self.assertEqual(before, 1_000_000)
        self.assertEqual(on_day, 2_000_000)

    def test_unknown_model_raises_value_error(self):
        with self.assertRaises(ValueError):
            price_micros(VERSIONS, "2026-02-15", "model-missing", 1, 1)

    def test_day_before_first_version_raises_value_error(self):
        with self.assertRaises(ValueError):
            price_micros(VERSIONS, "2025-12-31", SMALL, 1, 1)


if __name__ == "__main__":
    unittest.main()
