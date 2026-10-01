from dataclasses import dataclass
from ollama import Client
import json
import re

from retrieval.structured import load_card 

OLLAMA_MODEL = "llama3.2"

SYSTEM_PROMPT = """Você extrai filtros estruturados de buscas sobre cartas de Yu-Gi-Oh!.
Devolva APENAS um JSON válido, sem nenhum texto antes ou depois, neste formato:

{
  "attribute": ["DARK", "WATER"] ou null,
  "atk_min": number ou null,
  "atk_max": number ou null,
  "def_min": number ou null,
  "def_max": number ou null,
  "level_min": number ou null,
  "level_max": number ou null,
  "atk_degree": "high" | "very_high" | "low" | "very_low" | null,
  "def_degree": "high" | "very_high" | "low" | "very_low" | null,
  "semantic_text": "texto restante, sem os termos já capturados acima"
}

Atributos válidos: DARK, LIGHT, WATER, FIRE, EARTH, WIND, DIVINE.
Use atk_degree/def_degree só para intenção qualitativa ("forte", "fraco"), sem número.
Se houver valor numérico comparado a ATK/DEF/Level, use os campos _min/_max, nunca degree.
Nunca invente valores que não estão implícitos na query.
"""

FEW_SHOT = [
    {"role": "user", "content": "something cheap to summon but still hits like a truck"},
    {"role": "assistant", "content": json.dumps({
        "attribute": None, "atk_min": None, "atk_max": None,
        "def_min": None, "def_max": None,
        "level_min": None, "level_max": 4,
        "atk_degree": "high", "def_degree": None,
        "semantic_text": "",
    })},
    {"role": "user", "content": "a beefy DARK attacker"},
    {"role": "assistant", "content": json.dumps({
        "attribute": ["DARK"], "atk_min": None, "atk_max": None,
        "def_min": None, "def_max": None,
        "level_min": None, "level_max": None,
        "atk_degree": "high", "def_degree": None,
        "semantic_text": "attacker",
    })},
]

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

def _normalize_tokens(text:str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())

def build_name_index():
    index = {}
    max_len = 0
    for card in load_card():
        name = card["metadata"]["name"]
        tokens = tuple(_normalize_tokens(name))
        if tokens:
            index[tokens] = name
            max_len = max(max_len, len(tokens))
    return index, max_len

NAME_INDEX, MAX_NAME_WORDS = build_name_index()

def find_card_name_spans(text: str) -> list[tuple[int,  int]]:
    tokens_iter = list(re.finditer(r"[a-z0-9]+", text))
    words = [m.group() for m in tokens_iter]

    spans = []
    i = 0
    while i < len(words):
        matched = False
        for length in range(min(MAX_NAME_WORDS, len(words) - i), 0, -1):
            window = tuple(words[i:i + length])
            if window in NAME_INDEX:
                start = tokens_iter[i].start()
                end = tokens_iter[i + length - 1].end()
                if length > 1 or len(window[0]) >= 5:
                    spans.append((start, end))
                    i += length
                    matched = True
                    break
        if not matched:
            i += 1
    return spans

@dataclass
class QueryPlan:
    attribute: list[str] | None = None
    atk_min: int | None = None
    atk_max: int | None = None
    def_min: int | None = None
    def_max: int | None = None
    level: int | None = None
    level_min: int | None = None
    level_max: int | None = None
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

def _overlaps_any(span, zones):
    s, e = span
    return any(s < z1 and z0 < e for z0, z1 in zones)

def parse_query(query: str) -> QueryPlan:
    text = query.lower()
    plan, consumed = QueryPlan(), []

    name_spans = find_card_name_spans(text)

    fields = [f for f in _find(FIELDS, text) if not _overlaps_any(f[:2], name_spans)]
    comps = [c for c in _find(COMPARATORS, text) if not _overlaps_any(c[:2], name_spans)]
    degrees = [d for d in _find(DEGREES, text) if not _overlaps_any((d[0], d[1]), name_spans)]
    clauses = _clauses(text)

    used_fields_spans = set()

    for m in re.finditer(NUMBER, text):
        n = int(re.sub(r"[.,]","", m.group()))
        span = m.span()
        if _overlaps_any(span, name_spans):
            continue
        scope = next(c for c in clauses if c[0] <= span[0] <= c[1])

        available = [f for f in fields if f[:2] not in used_fields_spans]
        field = _nearest(span, available, scope)
        field_name = field[2] if field else ("atk" if _nearest(span, comps, scope) else None)

        if field_name is None:
            continue

        comp = _nearest(span, comps, scope)
        _apply_bound(plan, field_name, comp[2] if comp else "eq", n)
        consumed += [span] + ([field[:2]] if field else []) + ([comp[:2]] if comp else [])

        if field:
            used_fields_spans.add(field[:2])

    for s, e, degree in degrees:
        field = _nearest((s, e), fields, max_dist=12)
        name = field[2] if field else "atk"
        if name not in ("atk", "def") or _has_bound(plan, name):
            continue
        setattr(plan, f"{name}_degree", degree)
        consumed += [(s, e)] + ([field[:2]] if field else [])

    attributes = []
    for m in re.finditer(rf"(?<![a-z])({'|'.join(ATTRIBUTES)})(?![a-z])", text):
        if _overlaps_any(m.span(), name_spans):
            continue
        attributes.append(m.group(1). upper())
        consumed.append(m.span())

    plan.attribute = attributes or None

    chars = list(text)
    for s, e in consumed:
        chars[s:e] = " " * (e - s)
    words = [w for w in re.findall(r"[a-z0-9'\-]+", "".join(chars)) if w not in NOISE]
    plan.semantic_text = " ".join(words)
    return plan

def llm_fallback(query: str) -> dict:
    client = Client()
    response = client.chat(
        model = OLLAMA_MODEL,
        format="json",
        options={"temperature": 0},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            *FEW_SHOT,
            {"role": "user", "content": query},
        ],
    )
    try:
        data = json.loads(response["message"]["content"])
    except (KeyError, json.JSONDecodeError):
        return {}
    return {k: v for k, v in data.items() if v not in (None, "", [])}

def parse_query_with_fallback(query: str) -> QueryPlan:
    plan = parse_query(query)

    leftover_query = len(plan.semantic_text.split())
    if not plan.to_kwargs() and leftover_query >= 3:
        llm_data = llm_fallback(query)
        for key, value in llm_data.items():
            if key == "semantic_text":
                continue
            if hasattr(plan, key):
                setattr(plan, key, value)
        if llm_data.get("semantic_text"):
            plan.semantic_text = llm_data["semantic_text"]

    return plan


if __name__=="__main__":
    for q in [
        "Dark Magician",
        "cards similar to Dark Magician",
        "Alsei, the Sylvan High Protector",
        "High ATK Dark monsters",
    ]:
        print(q, "->", parse_query(q).to_kwargs())