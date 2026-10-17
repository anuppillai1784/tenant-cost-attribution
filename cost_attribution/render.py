from typing import Sequence

from cost_attribution.anomalies import Alert
from cost_attribution.report import format_micros


def reconcile_line(total_micros: int, is_exact: bool) -> str:
    status = "EXACT" if is_exact else "MISMATCH"
    return (
        f"Reconcile: {status}, attributed spend equals total "
        f"{total_micros} micro-dollars for tenant, department and feature"
    )


def budget_line(tenant: str, row: dict) -> str:
    status = "OVER BUDGET" if row["over_budget"] else "within budget"
    return (
        f"  {tenant:<14} projected {format_micros(row['projected_micros'])} "
        f"limit {format_micros(row['limit_micros'])} {status}"
    )


def alert_line(alert: Alert) -> str:
    return (
        f"  {alert.day} {alert.tenant} {alert.feature} "
        f"cost {format_micros(alert.cost_micros)} "
        f"baseline {format_micros(alert.baseline_mean_micros)} z={alert.z_score:.2f}"
    )


def render_text(report: dict, alerts: Sequence[Alert]) -> str:
    lines = [f"Spend through {report['as_of_day']}: {format_micros(report['total_micros'])}"]
    for dimension, totals in report["totals"].items():
        lines.append(f"By {dimension}:")
        lines.extend(f"  {key:<14} {format_micros(micros)}" for key, micros in totals.items())
    lines.append("Budgets projected to month end:")
    lines.extend(budget_line(tenant, row) for tenant, row in report["budgets"].items())
    lines.append(f"Anomalies: {len(alerts)}")
    lines.extend(alert_line(alert) for alert in alerts)
    lines.append(reconcile_line(report["total_micros"], report["reconciled_exact"]))
    return "\n".join(lines) + "\n"
