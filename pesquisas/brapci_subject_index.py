#!/usr/bin/env python3
import csv
import re
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = "https://brapci.inf.br/indexs/subject/"
OUTPUT_PATH = Path(__file__).resolve().parent / "brapci_subject_terms.csv"


def build_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1200")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(60)
    return driver


def normalize_term(value: str) -> str:
    if value is None:
        return ""
    value = re.sub(r"\s+", " ", str(value)).strip()
    value = re.sub(r"\s*\(pt\)\s*$", "", value, flags=re.IGNORECASE)
    value = value.strip(" -:")
    return value


def parse_subject_text(raw_text: str, letter: str):
    if raw_text is None:
        return []

    raw_lines = raw_text.splitlines()
    terms = []
    seen = set()

    for raw_line in raw_lines:
        line = normalize_term(raw_line)
        if not line:
            continue
        lowered = line.lower()
        if "idioma:" in lowered or "total:" in lowered:
            continue
        if lowered.startswith(letter.lower()) and "(" not in lowered:
            candidate = line
        elif re.match(rf"^{re.escape(letter)}\b.*", line, flags=re.IGNORECASE):
            candidate = re.sub(rf"^\s*{re.escape(letter)}\s*", "", line, flags=re.IGNORECASE)
            candidate = candidate.strip()
        else:
            continue

        if not candidate or candidate.lower() == letter.lower():
            continue
        if candidate.lower() in seen:
            continue
        seen.add(candidate.lower())
        terms.append(candidate)

    return terms


def extract_terms_from_page(driver: webdriver.Chrome, letter: str):
    url = f"{BASE_URL}{letter}"
    driver.get(url)
    WebDriverWait(driver, 20).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    WebDriverWait(driver, 20).until(
        lambda d: "Idioma:" in d.find_element(By.TAG_NAME, "body").text
        or "Total:" in d.find_element(By.TAG_NAME, "body").text
    )

    body_text = driver.find_element(By.TAG_NAME, "body").text
    return parse_subject_text(body_text, letter)


def save_terms(rows):
    fieldnames = ["letter", "term"]
    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({"letter": row["letter"], "term": row["term"]})

    print(f"CSV salvo em: {OUTPUT_PATH}")
    print(f"Total de termos: {len(rows)}")


def main():
    letters = [chr(code) for code in range(ord("A"), ord("Z") + 1)]
    rows = []
    driver = build_driver()
    try:
        for letter in letters:
            terms = extract_terms_from_page(driver, letter)
            if not terms:
                continue
            print(f"{letter}: {len(terms)} termos")
            for term in terms:
                rows.append({"letter": letter, "term": term})
                print(f"  - {term}")
    finally:
        driver.quit()

    save_terms(rows)


if __name__ == "__main__":
    main()
