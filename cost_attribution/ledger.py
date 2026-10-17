import sqlite3
from dataclasses import dataclass

SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
    request_id TEXT PRIMARY KEY,
    tenant TEXT NOT NULL,
    department TEXT NOT NULL,
    feature TEXT NOT NULL,
    model TEXT NOT NULL,
    day TEXT NOT NULL,
    input_tokens INTEGER NOT NULL,
    output_tokens INTEGER NOT NULL
)
"""

INSERT_EVENT = "INSERT OR IGNORE INTO events VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
SELECT_EVENTS = (
    "SELECT request_id, tenant, department, feature, model, day, "
    "input_tokens, output_tokens FROM events ORDER BY day, request_id"
)


@dataclass(frozen=True)
class Event:
    request_id: str
    tenant: str
    department: str
    feature: str
    model: str
    day: str
    input_tokens: int
    output_tokens: int


def open_ledger(path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.execute(SCHEMA)
    return conn


def ingest(conn: sqlite3.Connection, events: list[Event]) -> int:
    before = conn.total_changes
    conn.executemany(
        INSERT_EVENT,
        [
            (
                event.request_id,
                event.tenant,
                event.department,
                event.feature,
                event.model,
                event.day,
                event.input_tokens,
                event.output_tokens,
            )
            for event in events
        ],
    )
    conn.commit()
    return conn.total_changes - before


def load_events(conn: sqlite3.Connection) -> list[Event]:
    return [Event(*row) for row in conn.execute(SELECT_EVENTS)]
