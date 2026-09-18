#!/usr/bin/env python3
import csv
import json
import re
import sys
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

PAGE_URL = "https://www.brapci.inf.br/search_advanced"
OUTPUT_DIR = Path(__file__).resolve().parent


def build_driver() -> webdriver.Chrome:
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1200")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    )
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(60)
    return driver


def wait_visible(driver: webdriver.Chrome, locator: tuple, timeout: int = 30):
    return WebDriverWait(driver, timeout).until(EC.visibility_of_element_located(locator))


def read_result_status(driver: webdriver.Chrome):
    body_text = driver.find_element(By.TAG_NAME, "body").text
    match = re.search(r"Mostrando\s+(\d+)\s+de\s+(\d+)\s+resultado", body_text, flags=re.IGNORECASE)
    if match:
        return int(match.group(1)), int(match.group(2))
    return 0, 0


def extract_rendered_results(driver: webdriver.Chrome, query: str, max_total: int = 20):
    driver.get(PAGE_URL)
    time.sleep(1.5)

    term_input = wait_visible(driver, (By.CSS_SELECTOR, 'input[placeholder="Digite o termo"]'))
    term_input.clear()
    term_input.send_keys(query)

    add_button = wait_visible(driver, (By.XPATH, "//button[contains(., 'Adicionar Termo')]"))
    add_button.click()
    time.sleep(0.8)

    strategy_box = wait_visible(driver, (By.CSS_SELECTOR, 'textarea, #strategy'))
    strategy_box.clear()
    strategy_box.send_keys(f'"{query}"')

    query_button = wait_visible(driver, (By.XPATH, "//button[contains(., 'Busca pela query')]"))
    query_button.click()

    WebDriverWait(driver, 30).until(
        lambda d: "Mostrando" in d.find_element(By.TAG_NAME, "body").text
    )

    seen = set()
    collected = []
    last_visible_count = -1
    no_change_rounds = 0

    print("STATUS_INICIAL:", read_result_status(driver))
    for _ in range(80):
        tables = driver.find_elements(By.CSS_SELECTOR, "table.mb-3.mt-3.fadeIn")
        batch_records = []
        for table in tables:
            record = parse_result_table(table)
            if not record:
                continue
            key = (record["title"], record["author"], record["year"], record["publication_type"])
            if key not in seen:
                seen.add(key)
                batch_records.append(record)

        if batch_records:
            collected.extend(batch_records)
            write_outputs(collected, query)
            print(f"SCROLL_BATCH: {len(collected)} registros gravados em CSV/JSON")

        visible_count, total_count = read_result_status(driver)
        if len(collected) >= max_total:
            break

        if visible_count == last_visible_count:
            no_change_rounds += 1
            if no_change_rounds >= 2:
                break
        else:
            no_change_rounds = 0

        last_visible_count = visible_count
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2.5)

    return collected


def parse_result_table(table) -> dict:
    title_link = table.find_elements(By.CSS_SELECTOR, "a.work")
    if not title_link:
        return {}

    title = title_link[0].text.strip()

    author_elements = table.find_elements(By.TAG_NAME, "i")
    author = author_elements[0].text.strip() if author_elements else ""

    year = ""
    year_elements = table.find_elements(By.CSS_SELECTOR, "span[title='Ano de publicação do trabalho']")
    if year_elements:
        year = year_elements[0].text.strip()

    type_value = ""
    type_elements = table.find_elements(By.CSS_SELECTOR, "span.documment_type")
    if type_elements:
        type_value = type_elements[0].text.strip()

    keywords = []
    # A página de busca do Brapci não expõe as palavras-chave por item no HTML renderizado.
    # Quando o campo não existe, o export continua consistente com a interface real do site.

    return {
        "title": title,
        "author": author,
        "year": year,
        "publication_type": type_value,
        "keywords": keywords,
    }


def write_outputs(records: list[dict], query: str):
    csv_path = OUTPUT_DIR / "brapci_search_results.csv"
    json_path = OUTPUT_DIR / "brapci_search_results.json"

    fieldnames = ["title", "author", "year", "publication_type", "keywords"]
    with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow({
                "title": record.get("title", ""),
                "author": record.get("author", ""),
                "year": record.get("year", ""),
                "publication_type": record.get("publication_type", ""),
                "keywords": "; ".join(record.get("keywords", [])),
            })

    with json_path.open("w", encoding="utf-8") as json_file:
        json.dump({
            "query": query,
            "total": len(records),
            "results": records,
        }, json_file, ensure_ascii=False, indent=2)

    print(f"CSV salvo em: {csv_path}")
    print(f"JSON salvo em: {json_path}")


def main() -> int:
    query = "ciência da informação"
    driver = None
    try:
        driver = build_driver()
        records = extract_rendered_results(driver, query, max_total=20)

        print(f"RESULTADOS={len(records)}")
        for index, record in enumerate(records[:10], 1):
            print(f"{index}. {record['title']} | {record['author']} | {record['year']} | {record['publication_type']}")

        return 0
    except Exception as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 1
    finally:
        if driver is not None:
            driver.quit()


if __name__ == "__main__":
    raise SystemExit(main())
