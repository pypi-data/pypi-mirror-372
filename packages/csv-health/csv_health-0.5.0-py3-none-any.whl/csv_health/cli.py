
from __future__ import annotations
import argparse, os, sys, subprocess
from pathlib import Path
from .api import check, save_processed, get_state, clear_state, get_home

def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="csv-health", description="CSV Health Checks inside your venv")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("check", help="Audit & remember CSV; write logs inside venv")
    sp.add_argument("input_csv", help="Path to CSV")
    sp.add_argument("--report", help="Path to JSON report (optional)", default=None)
    sp.add_argument("--report-text", help="Path to TEXT report (optional)", default=None)

    sp = sub.add_parser("save", help="Process remembered CSV and save (into venv by default)")
    sp.add_argument("-o", "--output", help="Output CSV path (optional)")

    sub.add_parser("info", help="Show current state")
    sub.add_parser("clear", help="Clear state & cached copy")
    sub.add_parser("open-home", help="Open storage directory in file explorer")
    return p

def main(argv: list[str] | None = None) -> int:
    p = _parser()
    args = p.parse_args(argv)

    if args.cmd == "check":
        info = check(args.input_csv, report_path=args.report, report_text_path=args.report_text)
        print(info)
        return 0
    if args.cmd == "save":
        print(save_processed(args.output))
        return 0
    if args.cmd == "info":
        print(get_state() or "No state")
        return 0
    if args.cmd == "clear":
        clear_state()
        print("State cleared")
        return 0
    if args.cmd == "open-home":
        home = get_home()
        print(home)
        if sys.platform.startswith("win"):
            os.startfile(home)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.run(["open", str(home)])
        else:
            subprocess.run(["xdg-open", str(home)])
        return 0
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
