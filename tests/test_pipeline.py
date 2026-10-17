import unittest

from cost_attribution.anomalies import detect_anomalies
from cost_attribution.attribution import daily_costs, price_events
from cost_attribution.ledger import Event
from cost_attribution.prices import DEFAULT_PRICE_VERSIONS
from cost_attribution.synthetic import SPIKE_DAY, SPIKE_KEY, demo_days, generate_events


def make_event(request_id: str, day: str, feature: str) -> Event:
    return Event(
        request_id=request_id,
        tenant="tenant-alder",
        department="support",
        feature=feature,
        model="model-small",
        day=day,
        input_tokens=1_000,
        output_tokens=0,
    )


class DailyCostsTest(unittest.TestCase):
    def test_costs_sum_per_tenant_feature_and_day(self):
        priced = price_events(
            [
                make_event("r1", "2026-09-01", "chat-summary"),
                make_event("r2", "2026-09-01", "chat-summary"),
                make_event("r3", "2026-09-02", "chat-summary"),
                make_event("r4", "2026-09-01", "doc-search"),
            ],
            DEFAULT_PRICE_VERSIONS,
        )
        series = daily_costs(priced)
        self.assertEqual(
            series[("tenant-alder", "chat-summary")],
            {"2026-09-01": 2 * priced[0].cost_micros, "2026-09-02": priced[2].cost_micros},
        )
        self.assertEqual(series[("tenant-alder", "doc-search")], {"2026-09-01": priced[3].cost_micros})


class SeededSpikeTest(unittest.TestCase):
    def test_seeded_spike_is_the_only_alert_on_demo_data(self):
        priced = price_events(generate_events(), DEFAULT_PRICE_VERSIONS)
        alerts = detect_anomalies(daily_costs(priced), demo_days())
        flagged = [((alert.tenant, alert.feature), alert.day) for alert in alerts]
        self.assertEqual(flagged, [(SPIKE_KEY, SPIKE_DAY)])


if __name__ == "__main__":
    unittest.main()
