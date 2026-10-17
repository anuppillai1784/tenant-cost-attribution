import argparse
from typing import Sequence

from cost_attribution.attribution import price_events, reconcile
from cost_attribution.demo import run_demo
from cost_attribution.ledger import load_events, open_ledger
from cost_attribution.prices import DEFAULT_PRICE_VERSIONS
from cost_attribution.render import reconcile_line


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cost_attribution", description="Inference spend attribution.")
    commands = parser.add_subparsers(dest="command", required=True)
    demo = commands.add_parser("demo", help="Generate synthetic events, ingest them, write reports.")
    demo.add_argument("--db", required=True, help="SQLite ledger file to create or reuse.")
    demo.add_argument("--out", required=True, help="Directory for report.json and alerts.json.")
    reconcile_cmd = commands.add_parser("reconcile", help="Prove attributed spend equals total spend.")
    reconcile_cmd.add_argument("--db", required=True, help="SQLite ledger file to check.")
    return parser


def reconcile_ledger(db_path: str) -> int:
    conn = open_ledger(db_path)
    events = load_events(conn)
    conn.close()
    result = reconcile(price_events(events, DEFAULT_PRICE_VERSIONS))
    print(reconcile_line(result.total_micros, result.is_exact))
    return 0 if result.is_exact else 1


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "demo":
        print(run_demo(args.db, args.out), end="")
        return 0
    return reconcile_ledger(args.db)
