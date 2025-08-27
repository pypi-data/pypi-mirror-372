from pathlib import Path
from datetime import date
import json, argparse
from typing import Dict
from judge import evaluate, Verdict

def load_metrics(path: Path) -> Dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def metrics_date(metrics: Dict) -> str:
    d = metrics.get("date")
    return d if isinstance(d, str) else date.today().isoformat()

def format_line(day: str, verdict: Verdict) -> str:
    reasons = "; ".join(verdict.reasons) if verdict.reasons else "-"
    return f"{day}\t{verdict.pass_fail}\t{reasons}\n"

def write_log(verdict: Verdict, log_path: Path, day: str) -> None:
    line = format_line(day, verdict)
    with log_path.open("w", encoding="utf-8") as f:
        f.write(line)

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--metrics", required=True)
    p.add_argument("--log", required=True)
    p.add_argument("--date")
    args = p.parse_args()

    metrics = load_metrics(Path(args.metrics))
    verdict = evaluate(metrics)

    comment = str(metrics.get("comment", "")).strip()
    if comment and not verdict.reasons:
        verdict = Verdict(verdict.pass_fail, [comment])

    day = args.date or metrics_date(metrics)
    write_log(verdict, Path(args.log), day)

if __name__ == "__main__":
    main()
