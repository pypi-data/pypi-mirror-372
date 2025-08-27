# judge.py
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class Verdict:
    pass_fail: str            # "PASS" | "FAIL"
    reasons: List[str]

def evaluate(metrics: Dict) -> Verdict:
    """Единственный источник правил PASS/FAIL."""
    reasons: List[str] = []
    passed = True
    # TODO: перенеси сюда правила из mark_day.py
    return Verdict("PASS" if passed else "FAIL", reasons)

if __name__ == "__main__":
    # быстрый smoke-запуск
    print(evaluate({"_smoke": True}))


try:
    from mark_day import *
except Exception:
    pass
