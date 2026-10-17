import calendar
from dataclasses import dataclass


@dataclass(frozen=True)
class BudgetProjection:
    projected_micros: int
    limit_micros: int

    @property
    def over_budget(self) -> bool:
        return self.projected_micros > self.limit_micros


def project_month(spend_to_date_micros: int, as_of_day: str, limit_micros: int) -> BudgetProjection:
    year, month, day = (int(part) for part in as_of_day.split("-"))
    days_in_month = calendar.monthrange(year, month)[1]
    projected = spend_to_date_micros * days_in_month // day
    return BudgetProjection(projected_micros=projected, limit_micros=limit_micros)
