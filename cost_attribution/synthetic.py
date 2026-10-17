import random
from datetime import date, timedelta

from cost_attribution.ledger import Event

SEED = 7
DEMO_START = date(2026, 9, 1)
DEMO_DAYS = 30
TENANT_DEPARTMENTS = {
    "tenant-alder": ("support", "sales"),
    "tenant-birch": ("support", "research"),
    "tenant-cedar": ("legal", "sales"),
}
FEATURES = ("chat-summary", "doc-search", "ticket-triage")
MODELS = ("model-small", "model-large")
BASE_REQUESTS_PER_DAY = 6
EXTRA_REQUESTS_MAX = 3
SPIKE_KEY = ("tenant-birch", "doc-search")
SPIKE_DAY = "2026-09-21"
SPIKE_MULTIPLIER = 8
INPUT_TOKENS_RANGE = (200, 1_800)
OUTPUT_TOKENS_RANGE = (50, 600)


def demo_days() -> list[str]:
    return [(DEMO_START + timedelta(days=offset)).isoformat() for offset in range(DEMO_DAYS)]


def request_count(rng: random.Random, tenant: str, feature: str, day: str) -> int:
    count = BASE_REQUESTS_PER_DAY + rng.randint(0, EXTRA_REQUESTS_MAX)
    if (tenant, feature) == SPIKE_KEY and day == SPIKE_DAY:
        count *= SPIKE_MULTIPLIER
    return count


def generate_events(seed: int = SEED) -> list[Event]:
    rng = random.Random(seed)
    events: list[Event] = []
    for day in demo_days():
        for tenant, departments in TENANT_DEPARTMENTS.items():
            for feature in FEATURES:
                for index in range(request_count(rng, tenant, feature, day)):
                    events.append(
                        Event(
                            request_id=f"{day}-{tenant}-{feature}-{index:03d}",
                            tenant=tenant,
                            department=rng.choice(departments),
                            feature=feature,
                            model=rng.choice(MODELS),
                            day=day,
                            input_tokens=rng.randint(*INPUT_TOKENS_RANGE),
                            output_tokens=rng.randint(*OUTPUT_TOKENS_RANGE),
                        )
                    )
    return events
