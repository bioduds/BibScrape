import json
from pathlib import Path

from brapci_pipeline import build_term_index, normalize_keywords, summarize_by_year


def test_normalize_keywords_removes_noise_and_duplicates():
    raw = [
        "Ciência da informação",
        "Ciência da informação",
        "Palavras-chave:",
        "Abstract:",
        "Interdisciplinaridade",
        "Information science",
    ]

    normalized = normalize_keywords(raw)

    assert "Ciência da informação" in normalized
    assert "Palavras-chave:" not in normalized
    assert "Abstract:" not in normalized
    assert len(normalized) == 3


def test_build_term_index_counts_terms_across_documents():
    records = [
        {
            "title": "Artigo A",
            "year": "2020",
            "keywords": ["Ciência da informação", "Interdisciplinaridade"],
        },
        {
            "title": "Artigo B",
            "year": "2021",
            "keywords": ["Ciência da informação", "Pesquisa"]
        },
    ]

    index = build_term_index(records)

    assert index["ciência da informação"] == 2
    assert index["interdisciplinaridade"] == 1
    assert index["pesquisa"] == 1


def test_summarize_by_year_counts_publications():
    records = [
        {"year": "2020"},
        {"year": "2020"},
        {"year": "2021"},
    ]

    summary = summarize_by_year(records)

    assert summary == {"2020": 2, "2021": 1}
