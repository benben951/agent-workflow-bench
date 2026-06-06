from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from agent_workflow_bench.reporting import build_summary, render_markdown_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize benchmark run manifests.")
    parser.add_argument("--runs", default="outputs/runs", help="Directory containing JSON run manifests")
    parser.add_argument("--json-out", help="Optional path for summary JSON")
    parser.add_argument("--markdown-out", help="Optional path for recruiter-readable Markdown report")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = build_summary(args.runs)
    summary_json = json.dumps(summary, indent=2, ensure_ascii=False)
    if args.json_out:
        json_path = Path(args.json_out)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(summary_json + "\n", encoding="utf-8")
    if args.markdown_out:
        markdown_path = Path(args.markdown_out)
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(render_markdown_report(summary), encoding="utf-8")
    print(summary_json)


if __name__ == "__main__":
    main()
