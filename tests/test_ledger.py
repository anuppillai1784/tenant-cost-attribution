import unittest

from cost_attribution.ledger import Event, ingest, load_events, open_ledger


def make_event(request_id: str, input_tokens: int = 100, output_tokens: int = 50) -> Event:
    return Event(
        request_id=request_id,
        tenant="tenant-alder",
        department="support",
        feature="chat-summary",
        model="model-small",
        day="2026-03-01",
        input_tokens=input_tokens,
        output_tokens=output_tokens,
    )


class IngestTest(unittest.TestCase):
    def setUp(self):
        self.conn = open_ledger(":memory:")

    def tearDown(self):
        self.conn.close()

    def test_new_events_are_stored_and_counted(self):
        inserted = ingest(self.conn, [make_event("r1"), make_event("r2")])
        self.assertEqual(inserted, 2)
        self.assertEqual(len(load_events(self.conn)), 2)

    def test_duplicate_request_id_is_ignored(self):
        ingest(self.conn, [make_event("r1", input_tokens=100)])
        inserted = ingest(self.conn, [make_event("r1", input_tokens=999)])
        stored = load_events(self.conn)
        self.assertEqual(inserted, 0)
        self.assertEqual(len(stored), 1)
        self.assertEqual(stored[0].input_tokens, 100)

    def test_duplicate_inside_one_batch_is_stored_once(self):
        inserted = ingest(self.conn, [make_event("r1"), make_event("r1")])
        self.assertEqual(inserted, 1)
        self.assertEqual(len(load_events(self.conn)), 1)


if __name__ == "__main__":
    unittest.main()
