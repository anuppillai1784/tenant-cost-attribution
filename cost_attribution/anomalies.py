import statistics
from dataclasses import dataclass
from typing import Mapping, Sequence

WINDOW_DAYS = 14
MIN_HISTORY_DAYS = 7
Z_THRESHOLD = 3.0


@dataclass(frozen=True)
class Alert:
    tenant: str
    feature: str
    day: str
    cost_micros: int
    baseline_mean_micros: int
    z_score: float


def detect_anomalies(
    daily_by_series: Mapping[tuple[str, str], Mapping[str, int]],
    days: Sequence[str],
    window: int = WINDOW_DAYS,
    min_history: int = MIN_HISTORY_DAYS,
    threshold: float = Z_THRESHOLD,
) -> list[Alert]:
    alerts: list[Alert] = []
    for (tenant, feature), daily in sorted(daily_by_series.items()):
        costs = [daily.get(day, 0) for day in days]
        for index, day in enumerate(days):
            history = costs[max(0, index - window):index]
            if len(history) < min_history:
                continue
            spread = statistics.pstdev(history)
            if spread == 0:
                continue
            mean = statistics.fmean(history)
            z = (costs[index] - mean) / spread
            if z >= threshold:
                alerts.append(
                    Alert(
                        tenant=tenant,
                        feature=feature,
                        day=day,
                        cost_micros=costs[index],
                        baseline_mean_micros=round(mean),
                        z_score=z,
                    )
                )
    return alerts
