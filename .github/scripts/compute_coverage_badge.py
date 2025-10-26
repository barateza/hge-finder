#!/usr/bin/env python3
"""
Usage:
  python3 compute_coverage_badge.py coverage.json .github/coverage/coverage-badge.json

Reads coverage.json produced by coverage.py and emits a shields.io endpoint JSON.
"""
import json
import sys
from pathlib import Path

def color_for(percent):
    if percent is None:
        return "lightgrey"
    p = float(percent)
    if p < 60:
        return "red"
    if p < 80:
        return "yellow"
    if p < 90:
        return "yellowgreen"
    return "brightgreen"

def read_percent_from_coverage_json(p):
    try:
        data = json.loads(p.read_text())
    except Exception as e:
        print(f"Failed to parse JSON: {e}")
        return None
    totals = data.get("totals", {}) or {}
    # coverage.py uses "percent_covered" key in some versions
    percent = totals.get("percent_covered") or totals.get("percent") or totals.get("percent_cov")
    if percent is None:
        # fallback compute from covered_lines / num_statements
        covered = totals.get("covered_lines")
        statements = totals.get("num_statements") or totals.get("num_statements_total") or totals.get("num_statements_executed")
        if covered is not None and statements:
            try:
                percent = (covered / statements) * 100.0
            except Exception:
                percent = None
    return percent

def main():
    if len(sys.argv) < 3:
        print("Usage: compute_coverage_badge.py <coverage.json> <out.json>")
        sys.exit(2)
    in_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2])
    if not in_path.exists():
        print(f"Input {in_path} not found")
        sys.exit(1)

    percent = read_percent_from_coverage_json(in_path)

    if percent is not None:
        try:
            percent_val = float(percent)
            message = f"{int(round(percent_val))}%"
        except Exception:
            message = "unknown"
            percent_val = None
    else:
        message = "unknown"
        percent_val = None

    out = {
        "schemaVersion": 1,
        "label": "coverage",
        "message": message,
        "color": color_for(percent_val),
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2))
    print(f"Wrote {out_path} -> {message}")

if __name__ == "__main__":
    main()