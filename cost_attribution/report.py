from typing import Mapping, Sequence

from cost_attribution.attribution import DIMENSIONS, PricedEvent, Reconciliation, totals_by
from cost_attribution.budgets import project_month

MICROS_PER_DOLLAR = 1_000_000


def format_micros(value: int) -> str:
    dollars, micros = divmod(value, MICROS_PER_DOLLAR)
    return f"${dollars}.{micros:06d}"


def month_spend_by_tenant(priced: Sequence[PricedEvent], as_of_day: str) -> dict[str, int]:
    month = as_of_day[:7]
    in_month = [
        item
        for item in priced
        if item.event.day[:7] == month and item.event.day <= as_of_day
    ]
    return totals_by(in_month, "tenant")


def budget_rows(
    priced: Sequence[PricedEvent],
    budgets: Mapping[str, int],
    as_of_day: str,
) -> dict[str, dict[str, int | bool]]:
    spend = month_spend_by_tenant(priced, as_of_day)
    rows: dict[str, dict[str, int | bool]] = {}
    for tenant, limit in sorted(budgets.items()):
        spent = spend.get(tenant, 0)
        projection = project_month(spent, as_of_day, limit)
        rows[tenant] = {
            "limit_micros": limit,
            "spend_to_date_micros": spent,
            "projected_micros": projection.projected_micros,
            "over_budget": projection.over_budget,
        }
    return rows


def build_report(
    priced: Sequence[PricedEvent],
    reconciliation: Reconciliation,
    budgets: Mapping[str, int],
    as_of_day: str,
) -> dict:
    return {
        "as_of_day": as_of_day,
        "total_micros": reconciliation.total_micros,
        "reconciled_exact": reconciliation.is_exact,
        "totals": {
            dimension: dict(sorted(totals_by(priced, dimension).items()))
            for dimension in DIMENSIONS
        },
        "budgets": budget_rows(priced, budgets, as_of_day),
    }
