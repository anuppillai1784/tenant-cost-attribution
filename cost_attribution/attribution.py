from dataclasses import dataclass
from typing import Callable, Mapping, NamedTuple, Sequence

from cost_attribution.ledger import Event
from cost_attribution.prices import PriceVersion, price_micros

DIMENSIONS: Mapping[str, Callable[[Event], str]] = {
    "tenant": lambda event: event.tenant,
    "department": lambda event: event.department,
    "feature": lambda event: event.feature,
}


class PricedEvent(NamedTuple):
    event: Event
    cost_micros: int


@dataclass(frozen=True)
class Reconciliation:
    total_micros: int
    attributed: Mapping[str, int]

    @property
    def is_exact(self) -> bool:
        return all(value == self.total_micros for value in self.attributed.values())


def price_events(events: Sequence[Event], versions: Sequence[PriceVersion]) -> list[PricedEvent]:
    return [
        PricedEvent(
            event,
            price_micros(versions, event.day, event.model, event.input_tokens, event.output_tokens),
        )
        for event in events
    ]


def totals_by(priced: Sequence[PricedEvent], dimension: str) -> dict[str, int]:
    key_of = DIMENSIONS[dimension]
    totals: dict[str, int] = {}
    for item in priced:
        key = key_of(item.event)
        totals[key] = totals.get(key, 0) + item.cost_micros
    return totals


def reconcile(priced: Sequence[PricedEvent]) -> Reconciliation:
    total = sum(item.cost_micros for item in priced)
    attributed = {
        dimension: sum(totals_by(priced, dimension).values()) for dimension in DIMENSIONS
    }
    return Reconciliation(total_micros=total, attributed=attributed)


def daily_costs(priced: Sequence[PricedEvent]) -> dict[tuple[str, str], dict[str, int]]:
    series: dict[tuple[str, str], dict[str, int]] = {}
    for item in priced:
        key = (item.event.tenant, item.event.feature)
        days = series.setdefault(key, {})
        days[item.event.day] = days.get(item.event.day, 0) + item.cost_micros
    return series
