#!/usr/bin/env python3
import argparse
import json
from typing import Any, Dict, Iterable, List

import requests

API_URL = "https://cip.brapci.inf.br/api/BRAPCI/search/v1"
PAGE_URL = "https://www.brapci.inf.br/search_advanced"


def search_brapci(query: str, di: int = 1972, df: int = 2026, start: int = 0) -> Dict[str, Any]:
    params = {
        "q": query,
        "di": di,
        "df": df,
        "start": start,
    }

    response = requests.get(API_URL, params=params, timeout=30)
    response.raise_for_status()

    content_type = response.headers.get("Content-Type", "").lower()
    if "application/json" not in content_type:
        raise ValueError(
            "A API do Brapci não está retornando JSON neste momento. "
            f"Content-Type: {content_type}. Isso geralmente indica que o endpoint está indisponível ou que a busca depende do frontend. "
            f"Confira a página: {PAGE_URL}"
        )

    try:
        data = response.json()
    except ValueError as exc:
        raise ValueError("A resposta da API não é um JSON válido.") from exc

    if not isinstance(data, dict):
        raise ValueError(f"Formato inesperado: {type(data).__name__}")

    return data


def print_results(data: Dict[str, Any]) -> None:
    total = data.get("total")
    works = data.get("works", {}).get("data", [])

    print(f"TOTAL: {total}")
    for i, work in enumerate(works, 1):
        print(f"{i}. {json.dumps(work, ensure_ascii=False, indent=2)}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Busca simples no Brapci.")
    parser.add_argument("--q", default='"ciência da informação" AND "epistemologia" OR "conceito" OR "interdisciplinaridade"', help="Consulta de busca.")
    parser.add_argument("--di", type=int, default=1972, help="Ano inicial.")
    parser.add_argument("--df", type=int, default=2026, help="Ano final.")
    parser.add_argument("--start", type=int, default=0, help="Índice inicial dos resultados.")
    args = parser.parse_args()

    try:
        data = search_brapci(args.q, di=args.di, df=args.df, start=args.start)
        print_results(data)
        return 0
    except requests.RequestException as exc:
        print(f"Erro de rede: {exc}")
        print(f"Tente a busca pelo frontend em {PAGE_URL}")
        return 1
    except ValueError as exc:
        print(f"Erro de resposta: {exc}")
        print(f"O endpoint atual responde em HTML. O caminho mais confiável para automatização é usar a página web com Playwright/Selenium.")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
