from dataclasses import dataclass
import re

ATTRIBUTES = {"dark", "light", "water", "fire", "earth", "wind", "divine"}

FIELDS = [
    ("atk", r"atk|attack|ataque"),
    ("def", r"def|defense|defence|defesa"),
    ("level", r"level|lvl|nivel"),
]

COMPARATORS = [
    ("gte", r"at least|no less than|minimum of|minimum|or more|or higher|>=|\+"),
    ("lte", r"at most|no more than|miximum of|maximum|or less|or lower|up to|<="),
    ("gt", r"more than|greater than|higher than|over|above|>"),
    ("lt", r"less than|lower than|fewer than|under|below|<"),
]

DEGREES = [
    ("very_high", r"very_high|extremely high|strongest|highest"),
    ("very_low", r"very low|extremely low|weakest|lowest"),
    ("high", r"high|strong|powerful|mighty"),
    ("low", r"low|weak|feeble"),
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
        start = m.end()
    bounds.append((start, len(text)))
    return bounds

def _apply_bound(plan, field, op, n):
    if field == "level":
        plan.level = n
        return
    lo, hi = {
        "gte": (n, None), "gt": (n + 1, None),
        "lte": (None, n), "lt": (None, n - 1),
        "eq": (n, n),
    }[op]
    if lo is not None:
        setattr(plan, f"{field}_min", lo)
    if hi is not None:
        setattr(plan, f"{field}_max", hi)

def _has_bound(plan, field):
    return getattr(plan, f"{field}_min") is not None or getattr(plan, f"{field}_max")

def parse_query(query: str) -> QueryPlan:
    text = query.lower()
    plan, consumed = QueryPlan(), []

    fields = _find(FIELDS, text)
    comps = _find(COMPARATORS, text)
    degrees = _find(DEGREES, text)
    clauses = _clauses(text)

    for m in re.finditer(NUMBER, text):
        n = int(re.sub(r"[.,]","", m.group()))
        span = m.span()
        scope = next(c for c in clauses if c[0] <= span[0] <= c[1])
        field = _nearest(span, fields, scope)
        if not field:
            continue
        comp = _nearest(span, comps, scope)
        _apply_bound(plan, field[2], comp[2] if comp else "eq", n)
        consumed += [span, field[:2]] + ([comp[:2]] if comp else [])

    for s, e, degree in degrees:
        field = _nearest((s, e), fields, max_dist=12)
        name = field[2] if field else "atk"
        if name not in ("atk", "def") or _has_bound(plan, name):
            continue
        setattr(plan, f"{name}_degree", degree)
        consumed += [(s, e)] + ([field[:2]] if field else [])

    for m in re.finditer(rf"(?<![a-z])({'|'.join(ATTRIBUTES)})(?![a-z])", text):
        plan.attribute = plan.attribute or m.group(1).upper()
        consumed.append(m.span())

    chars = list(text)
    for s, e in consumed:
        chars[s:e] = " " * (e - s)
    words = [w for w in re.findall(r"[a-z0-9'\-]+", "".join(chars)) if w not in NOISE]
    plan.semantic_text = " ".join(words)
    return plan

