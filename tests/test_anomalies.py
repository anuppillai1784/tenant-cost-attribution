import unittest

from cost_attribution.anomalies import detect_anomalies

DAYS = [f"2026-09-{number:02d}" for number in range(1, 31)]
NORMAL_PATTERN = [100, 110, 95, 105, 102, 98, 107]
SERIES_KEY = ("tenant-alder", "chat-summary")


def daily_values(values: list[int]) -> dict[str, int]:
    return dict(zip(DAYS, values))


def normal_values(count: int) -> list[int]:
    return [NORMAL_PATTERN[index % len(NORMAL_PATTERN)] for index in range(count)]


class DetectAnomaliesTest(unittest.TestCase):
    def test_seeded_spike_is_flagged_and_normal_days_are_not(self):
        values = normal_values(len(DAYS))
        values[20] = 1_000
        alerts = detect_anomalies({SERIES_KEY: daily_values(values)}, DAYS)
        self.assertEqual([alert.day for alert in alerts], [DAYS[20]])
        self.assertEqual(alerts[0].tenant, "tenant-alder")
        self.assertEqual(alerts[0].feature, "chat-summary")
        self.assertEqual(alerts[0].cost_micros, 1_000)
        self.assertGreater(alerts[0].z_score, 3.0)

    def test_spike_before_minimum_history_is_not_flagged(self):
        values = normal_values(len(DAYS))
        values[3] = 1_000
        alerts = detect_anomalies({SERIES_KEY: daily_values(values)}, DAYS)
        self.assertEqual(alerts, [])

    def test_constant_history_has_no_variance_and_raises_no_alert(self):
        values = [100] * len(DAYS)
        values[20] = 100
        alerts = detect_anomalies({SERIES_KEY: daily_values(values)}, DAYS)
        self.assertEqual(alerts, [])


if __name__ == "__main__":
    unittest.main()
