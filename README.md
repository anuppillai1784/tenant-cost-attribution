# tenant-cost-attribution

## What it does

This tool stores inference spend for each request in a SQLite ledger. It attributes that spend to tenants, departments, and features, and it projects budget use to month end. It also flags unusual daily spend with a z-score test and writes alerts as JSON and text.

## Why it matters

Shared model usage makes cost hard to assign to the team that caused it. Exact, repeatable attribution lets finance and engineering trust the numbers and act on spend spikes early.

## Quickstart

Requires Python 3.11 or later. Run these commands from the repository root. No install step is needed.

```
python3 -m unittest discover
rm -f ledger.sqlite
python3 -m cost_attribution demo --db ledger.sqlite --out examples > examples/demo_output.txt
python3 -m cost_attribution reconcile --db ledger.sqlite
```

The demo writes `examples/report.json`, `examples/alerts.json`, and `examples/demo_output.txt`. Running the demo again gives the same bytes.

## Repo tree

```
tenant-cost-attribution/
├── .gitignore              # Ignores caches and the local SQLite ledger
├── LICENSE                 # MIT license
├── README.md               # This file
├── pyproject.toml          # Package metadata, no dependencies
├── cost_attribution/       # Python package
│   ├── __init__.py         # Marks the package
│   ├── __main__.py         # Entry point for python3 -m cost_attribution
│   ├── anomalies.py        # Z-score spike detection per tenant and feature
│   ├── attribution.py      # Prices events, totals them, and reconciles
│   ├── budgets.py          # Month-end spend projection
│   ├── cli.py              # The demo and reconcile commands
│   ├── demo.py             # Runs the demo and writes output files
│   ├── ledger.py           # SQLite ledger with idempotent ingest
│   ├── prices.py           # Versioned price table and cost formula
│   ├── render.py           # Text summary lines
│   ├── report.py           # Report data and money formatting
│   └── synthetic.py        # Seeded synthetic events with one spike
├── examples/               # Committed sample output
│   ├── alerts.json         # Alerts from the demo
│   ├── demo_output.txt     # Text printed by the demo
│   └── report.json         # Totals, reconcile flag, and budgets
└── tests/                  # unittest suite
    ├── __init__.py         # Marks the test package
    ├── test_anomalies.py   # Spike detection and history guard
    ├── test_budgets.py     # Month-end projection
    ├── test_cli.py         # Demo and reconcile commands
    ├── test_demo.py        # Output files and identical reruns
    ├── test_ledger.py      # Duplicate request_id is ignored
    ├── test_pipeline.py    # Daily roll-up and the seeded spike
    ├── test_prices.py      # Price versions and repricing
    ├── test_reconcile.py   # Exact reconciliation to the micro-dollar
    ├── test_report.py      # Totals, reconcile flag, and budgets
    └── test_synthetic.py   # Deterministic synthetic events
```

The quickstart also creates `ledger.sqlite` and `__pycache__/` directories. Git ignores them, so they are not in the tree.

## How it works

- Ingest: each event has a `request_id`. The ledger keeps the first row for each `request_id` and ignores later copies.
- Pricing: cost in micro-dollars is `(input tokens x input rate + output tokens x output rate) // 1000000`. Rates are micro-dollars per million tokens. All values are integers. Fractions of a micro-dollar are dropped per event.
- Price versions: each event uses the price version that is in effect on its day. A new version changes the cost of events from its start day on. Older events keep their old prices.
- Attribution: totals by tenant, by department, and by feature each sum to the grand total. The reconcile command checks that all three sums equal the grand total.
- Budgets: the projection is month-to-date spend times days in the month, divided by the day of the month. The result is rounded down.
- Anomalies: the detector checks daily spend for each tenant and feature pair. It compares each day with the previous 28 days. It needs at least 14 days of history. It flags a day when its z-score is 3.0 or higher. It skips a window with zero spread. Days with no events count as zero.
- Output: the demo writes `report.json` and `alerts.json`. It also prints a text summary.

## Sample output

The block below is the committed `examples/demo_output.txt`.

```
Spend through 2026-09-20: $3.328872
By tenant:
  tenant-alder   $1.007363
  tenant-birch   $1.355882
  tenant-cedar   $0.965627
By department:
  legal          $0.541681
  research       $0.637764
  sales          $0.880245
  support        $1.269182
By feature:
  chat-summary   $0.200859
  doc-search     $2.913339
  ticket-triage  $0.214674
Budgets projected to month end:
  tenant-alder   projected $1.511044 limit $2.000000 within budget
  tenant-birch   projected $2.033823 limit $1.200000 OVER BUDGET
  tenant-cedar   projected $1.448440 limit $2.000000 within budget
Anomalies: 1
  2026-09-18 tenant-birch doc-search cost $0.393991 baseline $0.042743 z=56.52
Reconcile: EXACT, attributed spend equals total 3328872 micro-dollars for tenant, department and feature
```

## Limits

- The demo data is synthetic. Tenant, department, feature, and model names are invented.
- The prices are illustrative. They do not match any model provider.
- The budget limits in the demo are invented inputs.
- The z-score test does not model weekly or seasonal patterns.
- The reconcile command checks internal totals only. It does not compare totals with an invoice.
- The ledger keeps the first row for each `request_id`. A later row with different values is ignored without a warning.
- The ledger runs on one SQLite file. It has no multi-writer controls.

