from dataclasses import dataclass
import re

ATTRIBUTES = {"dark", "light", "water", "fire", "earth", "wind", "divine"}

FIELDS = [
    ("gte", r"at least|no less than|minimum of|minimum|or more|or higher|>=|\+")
    ("lte", r"at most|no more than|miximum of|maximum|or less|or lower|up to|<=")
    ("gt", r"more than|greater than|higher than|over|above|>")
    ("gte", r"less than|lower than|fewer than|under|below|<")
]

NOISE = {"monster", "monsters", "card", "cards", "that", "have", "has", "with",
         "a", "an", "the", "of", "on", "points", "point", "and", "which", "show", "me", "find"}

NUMBER = r"\d{1,3}(?:[.,]\d{3})+|\d+"

@dataclass
class QueryPlan:
    attribute: str | None = None
    atk_min: int | None = None
    atk_max: int | None = None
    def_min: int | None = None
    def_max: int | None = None
    level: int | None = None
    atk_degree: str | None = None
    def_degree: str | None = None
    semantic_text: str = ""

    def to_kwargs(self) -> dict:
        return {k: v for k, v in self.__dict__.items()
                if k != "semantic_text" and v is not None}

def _find(patterns, text):
    taken, found = [], []
    for label, pat, in patterns:
        for m in re.finditer(rf"(?<![a-z])(?:{pat})(?![a-z])", text):
            s, e = m.span()
            if any(s < t1 and t0 < e for t0, t1 in taken):
                continue
            taken.append((s, e))
            found.append((s, e, label))
    return found

def _nearest(span, items, scope=(0, 10**9), max_dist=25):
    best = None
    for it in items:
        if not (scope[0] <= it[0] and it[1] <= scope[1]):
            continue
        d = max(it[0] - span[1], span[0] - it[1], 0)
        if d <= max_dist and (best is None or d < best[0]):
            best = (d, it)
    return best[1] if best else None

def _clauses(text):
    bounds, start = [], 0
    for m in re.finditer(r"\band\b|,|;|\bbut\b", text):
        bounds.append((start, m.start()))
        