import json
import re
from collections import Counter
from pathlib import Path
from typing import Union


def build_boolean_query(term_rows):
    clauses = []
    for row in term_rows or []:
        raw_term = normalize_text(row.get("term", "")) if isinstance(row, dict) else ""
        raw_operator = normalize_text(row.get("operator", "AND")) if isinstance(row, dict) else "AND"
        if not raw_term:
            continue
        operator = raw_operator.upper()
        if operator not in {"AND", "OR"}:
            operator = "AND"
        clauses.append({"operator": operator, "term": raw_term})

    if not clauses:
        return ""

    fragments = [f'"{clause["term"]}"' for clause in clauses]
    if len(fragments) == 1:
        return fragments[0]

    query = fragments[0]
    for clause in clauses[1:]:
        query = f'{query} {clause["operator"]} "{clause["term"]}"'
    return query


def normalize_text(value: str) -> str:
    if value is None:
        return ""
    value = str(value).strip()
    value = re.sub(r"\s+", " ", value)
    return value


def normalize_keywords(raw_keywords):
    cleaned = []
    noise = {
        "palavras-chave:",
        "keywords:",
        "palabras clave:",
        "mots clés:",
        "abstract:",
        "resumo:",
        "summary:",
    }

    for item in raw_keywords or []:
        value = normalize_text(item)
        if not value:
            continue
        lowered = value.lower()
        if lowered in noise:
            continue
        if value.endswith(":"):
            continue
        if len(value) < 2:
            continue
        cleaned.append(value)

    seen = set()
    normalized = []
    for item in cleaned:
        key = item.lower().strip()
        if key in seen:
            continue
        seen.add(key)
        normalized.append(item)
    return normalized


def build_term_index(records):
    counter = Counter()
    for record in records or []:
        for keyword in normalize_keywords(record.get("keywords", [])):
            normalized = normalize_text(keyword).lower()
            if not normalized:
                continue
            counter[normalized] += 1
    return dict(sorted(counter.items(), key=lambda item: (-item[1], item[0])))


def summarize_by_year(records):
    summary = Counter()
    for record in records or []:
        year = normalize_text(record.get("year", ""))
        if not year:
            continue
        summary[year] += 1
    return dict(sorted(summary.items()))


def load_records(path: Union[str, Path]):
    file_path = Path(path)
    with file_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return payload.get("results", [])


def build_dashboard_data(path: Union[str, Path]):
    records = load_records(path)
    term_index = build_term_index(records)
    by_year = summarize_by_year(records)

    return {
        "total_records": len(records),
        "unique_terms": len(term_index),
        "top_terms": list(term_index.items())[:10],
        "by_year": by_year,
        "records": records,
    }
