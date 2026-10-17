import unittest

from cost_attribution.attribution import Reconciliation, price_events, reconcile, totals_by
from cost_attribution.ledger import Event
from cost_attribution.prices import ModelRate, PriceVersion

VERSIONS = [
    PriceVersion(
        effective_from="2026-01-01",
        rates={"model-small": ModelRate(input_micros_per_mtok=333_333, output_micros_per_mtok=777_777)},
    )
]


def make_event(request_id: str, tenant: str, department: str, feature: str, input_tokens: int, output_tokens: int) -> Event:
    return Event(
        request_id=request_id,
        tenant=tenant,
        department=department,
        feature=feature,
        model="model-small",
        day="2026-03-01",
        input_tokens=input_tokens,
        output_tokens=output_tokens,
    )


EVENTS = [
    make_event("r1", "tenant-alder", "support", "chat-summary", 1_001, 37),
    make_event("r2", "tenant-alder", "sales", "doc-search", 4_093, 11),
    make_event("r3", "tenant-birch", "support", "chat-summary", 77, 5_003),
]


class ReconcileTest(unittest.TestCase):
    def test_attributed_spend_equals_total_to_the_micro_dollar(self):
        priced = price_events(EVENTS, VERSIONS)
        result = reconcile(priced)
        expected_total = sum(item.cost_micros for item in priced)
        self.assertEqual(result.total_micros, expected_total)
        self.assertTrue(result.is_exact)
        self.assertEqual(set(result.attributed), {"tenant", "department", "feature"})
        for dimension, attributed in result.attributed.items():
            self.assertEqual(attributed, expected_total, dimension)

    def test_totals_by_tenant_split_the_total(self):
        priced = price_events(EVENTS, VERSIONS)
        by_tenant = totals_by(priced, "tenant")
        self.assertEqual(set(by_tenant), {"tenant-alder", "tenant-birch"})
        self.assertEqual(sum(by_tenant.values()), sum(item.cost_micros for item in priced))

    def test_reconciliation_with_a_missing_micro_dollar_is_not_exact(self):
        result = Reconciliation(total_micros=10, attributed={"tenant": 9, "feature": 10})
        self.assertFalse(result.is_exact)


if __name__ == "__main__":
    unittest.main()
