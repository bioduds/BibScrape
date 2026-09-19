#!/usr/bin/env python3
import html
import json
import os
import subprocess
import sys
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "brapci_search_results.json"
HTML_PATH = ROOT / "brapci_dashboard.html"
PYTHON = "/Users/capanema/Projects/Jonas/.venv/bin/python"
SCRAPER = ROOT / "pesquisas" / "brapci_selenium_search.py"
VISUALIZER = ROOT / "brapci_visualization.py"
ACTIVE_JOBS = {}


def normalize_query(raw_value: str) -> str:
    if raw_value is None:
        return ""
    value = str(raw_value).strip()
    value = value.replace("\r", " ").replace("\n", " ")
    value = " ".join(value.split())
    return value


def build_boolean_query(form_data):
    terms = []
    count = 0
    while True:
        term_key = f"term_{count}"
        op_key = f"op_{count}"
        if term_key not in form_data and op_key not in form_data:
            break
        term = normalize_query(form_data.get(term_key, [""])[0])
        operator = normalize_query(form_data.get(op_key, ["AND"])[0]).upper()
        if operator not in {"AND", "OR"}:
            operator = "AND"
        if term:
            terms.append({"term": term, "operator": operator})
        count += 1

    strategy = normalize_query(form_data.get("strategy_query", [""])[0])
    if strategy:
        return strategy

    if not terms:
        return "ciência da informação"

    query_parts = []
    for index, item in enumerate(terms):
        value = f'"{item["term"]}"'
        if index == 0:
            query_parts.append(value)
        else:
            query_parts.append(f"{item['operator']} {value}")
    return " ".join(query_parts)


def update_job(job_id: str, **payload):
    job = ACTIVE_JOBS.setdefault(job_id, {})
    for key, value in payload.items():
        job[key] = value
    return job


def _stream_pipeline(job_id: str, query: str):
    job = ACTIVE_JOBS[job_id]
    job["state"] = "running"
    job["progress"] = "iniciando coleta do BRAPCI..."
    job["logs"] = ["iniciando coleta do BRAPCI..."]

    cmd = [PYTHON, str(SCRAPER), "--query", query, "--max-results", "20"]
    proc = subprocess.Popen(cmd, cwd=str(ROOT), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    try:
        for line in proc.stdout:
            text = line.rstrip()
            if not text:
                continue
            job["logs"].append(text)
            job["progress"] = text
            job["last_update"] = time.time()
    finally:
        rc = proc.wait()
        if rc == 0:
            job["state"] = "rendering"
            job["progress"] = "gerando dashboard..."
            subprocess.run([PYTHON, str(VISUALIZER)], cwd=str(ROOT), check=True)
            job["state"] = "done"
            job["progress"] = "resultado finalizado"
            job["logs"].append("dashboard atualizado")
        else:
            job["state"] = "error"
            job["progress"] = "falha na coleta"
            job["logs"].append(f"comando falhou com código {rc}")


def start_pipeline(query: str):
    job_id = str(uuid.uuid4())
    update_job(job_id, query=query, state="queued", progress="registrando busca...", logs=["registrando busca..."])
    thread = threading.Thread(target=_stream_pipeline, args=(job_id, query), daemon=True)
    thread.start()
    return job_id


def run_pipeline(query: str):
    cmd = [PYTHON, str(SCRAPER), "--query", query, "--max-results", "20"]
    subprocess.run(cmd, cwd=str(ROOT), check=True)
    subprocess.run([PYTHON, str(VISUALIZER)], cwd=str(ROOT), check=True)
    return HTML_PATH.read_text(encoding="utf-8")


def render_dashboard(query: str = "ciência da informação"):
    from brapci_visualization import build_dashboard_html

    build_dashboard_html(str(DATA_PATH), str(HTML_PATH), query_text=query)
    return HTML_PATH.read_text(encoding="utf-8")


class DashboardHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/status":
            job_id = parse_qs(parsed.query).get("job_id", [""])[0]
            job = ACTIVE_JOBS.get(job_id, {})
            payload = json.dumps({
                "job_id": job_id,
                "state": job.get("state", "unknown"),
                "progress": job.get("progress", "aguardando..."),
                "logs": job.get("logs", []),
                "query": job.get("query", ""),
            }).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        if parsed.path != "/":
            self.send_response(404)
            self.end_headers()
            return

        query = "ciência da informação"
        if DATA_PATH.exists():
            try:
                payload = json.loads(DATA_PATH.read_text(encoding="utf-8"))
                if isinstance(payload, dict) and payload.get("query"):
                    query = str(payload["query"])
            except Exception:
                pass

        html_page = render_dashboard(query)
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(html_page.encode("utf-8"))))
        self.end_headers()
        self.wfile.write(html_page.encode("utf-8"))

    def do_POST(self):
        parsed = urlparse(self.path)

        if parsed.path == "/search":
            length = int(self.headers.get("Content-Length", "0"))
            raw_body = self.rfile.read(length)
            form_data = parse_qs(raw_body.decode("utf-8", errors="ignore"), keep_blank_values=True)
            query = build_boolean_query(form_data)
            job_id = start_pipeline(query)
            payload = json.dumps({"job_id": job_id, "query": query, "state": "queued"}).encode("utf-8")
            self.send_response(202)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        if parsed.path != "/":
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length)
        form_data = parse_qs(raw_body.decode("utf-8", errors="ignore"), keep_blank_values=True)
        query = build_boolean_query(form_data)

        try:
            run_pipeline(query)
            page = render_dashboard(query)
        except subprocess.CalledProcessError as exc:
            page = f"<html><body><h1>Erro na busca</h1><p>{html.escape(str(exc))}</p></body></html>"

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(page.encode("utf-8"))))
        self.end_headers()
        self.wfile.write(page.encode("utf-8"))


def main():
    host = "0.0.0.0"
    port = 8000
    server = ThreadingHTTPServer((host, port), DashboardHandler)
    print(f"Dashboard em: http://localhost:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
