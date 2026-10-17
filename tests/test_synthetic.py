import unittest
from collections import Counter

from cost_attribution.synthetic import SPIKE_DAY, SPIKE_KEY, demo_days, generate_events


class GenerateEventsTest(unittest.TestCase):
    def test_same_seed_gives_identical_events(self):
        self.assertEqual(generate_events(seed=7), generate_events(seed=7))

    def test_request_ids_are_unique(self):
        request_ids = [event.request_id for event in generate_events()]
        self.assertEqual(len(set(request_ids)), len(request_ids))

    def test_events_cover_every_demo_day(self):
        days = {event.day for event in generate_events()}
        self.assertEqual(days, set(demo_days()))

    def test_seeded_spike_day_has_far_more_requests_than_other_days(self):
        tenant, feature = SPIKE_KEY
        counts = Counter(
            event.day
            for event in generate_events()
            if event.tenant == tenant and event.feature == feature
        )
        other_days = [count for day, count in counts.items() if day != SPIKE_DAY]
        self.assertGreater(counts[SPIKE_DAY], 2 * max(other_days))


if __name__ == "__main__":
    unittest.main()
