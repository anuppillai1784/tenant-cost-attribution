import json
import os
from typing import Sequence

from cost_attribution.anomalies import Alert, detect_anomalies
from cost_attribution.attribution import daily_costs, price_events, reconcile
from cost_attribution.ledger import ingest, load_events, open_ledger
from cost_attribution.prices import DEFAULT_PRICE_VERSIONS
from cost_attribution.render import render_text
from cost_attribution.report import build_report
from cost_attribution.synthetic import demo_days, generate_events

DEMO_BUDGETS_MICROS = {
    "tenant-alder": 2_000_000,
    "tenant-birch": 1_200_000,
    "tenant-cedar": 2_000_000,
}
REPORT_FILE = "report.json"
ALERTS_FILE = "alerts.json"


def alert_rows(alerts: Sequence[Alert]) -> list[dict]:
    return [
        {
            "tenant": alert.tenant,
            "feature": alert.feature,
            "day": alert.day,
            "cost_micros": alert.cost_micros,
            "baseline_mean_micros": alert.baseline_mean_micros,
            "z_score": round(alert.z_score, 2),
        }
        for alert in alerts
    ]


def write_json(path: str, payload: object) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def run_demo(db_path: str, out_dir: str) -> str:
    conn = open_ledger(db_path)
    ingest(conn, generate_events())
    events = load_events(conn)
    conn.close()
    priced = price_events(events, DEFAULT_PRICE_VERSIONS)
    days = demo_days()
    report = build_report(priced, reconcile(priced), DEMO_BUDGETS_MICROS, days[-1])
    alerts = detect_anomalies(daily_costs(priced), days)
    write_json(os.path.join(out_dir, REPORT_FILE), report)
    write_json(os.path.join(out_dir, ALERTS_FILE), alert_rows(alerts))
    return render_text(report, alerts)
