import json
from pathlib import Path

import plotly.graph_objects as go

from brapci_pipeline import build_dashboard_data


def build_dashboard_html(input_path: str, output_path: str, query_text: str = "ciência da informação"):
    data = build_dashboard_data(input_path)
    top_terms = data["top_terms"]

    terms = [term for term, _ in top_terms]
    counts = [count for _, count in top_terms]

    bar_chart = go.Figure(
        data=[
            go.Bar(
                x=terms,
                y=counts,
                marker_color="rgb(59,130,246)",
                hovertemplate="<b>%{x}</b><br>Frequência: %{y}<extra></extra>",
            )
        ]
    )
    bar_chart.update_layout(
        title="Termos mais frequentes",
        xaxis_title="Termo",
        yaxis_title="Frequência",
        height=500,
        margin={"l": 50, "r": 20, "t": 50, "b": 120},
    )

    years = list(data["by_year"].keys())
    values = list(data["by_year"].values())
    year_chart = go.Figure(
        data=[
            go.Scatter(
                x=years,
                y=values,
                mode="lines+markers",
                line={"color": "rgb(16,185,129)", "width": 3},
                marker={"size": 9},
                hovertemplate="<b>%{x}</b><br>Artigos: %{y}<extra></extra>",
            )
        ]
    )
    year_chart.update_layout(
        title="Publicações por ano",
        xaxis_title="Ano",
        yaxis_title="Quantidade",
        height=400,
        margin={"l": 50, "r": 20, "t": 50, "b": 50},
    )

    html = f"""
    <html>
      <head>
        <meta charset="utf-8">
        <title>BRAPCI Dashboard</title>
        <script>
          async function startSearch(event) {{
            event.preventDefault();
            const form = event.target;
            const formData = new FormData(form);
            const body = new URLSearchParams(formData).toString();

            const panel = document.getElementById('statusPanel');
            const stateEl = document.getElementById('statusState');
            const textEl = document.getElementById('statusText');
            const logEl = document.getElementById('statusLog');
            panel.style.display = 'block';
            stateEl.textContent = 'queued';
            textEl.textContent = 'enviando query...';
            logEl.textContent = 'enviando query...';

            const response = await fetch('/search', {{
              method: 'POST',
              headers: {{ 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8' }},
              body
            }});

            const result = await response.json();
            const jobId = result.job_id;
            pollStatus(jobId);
          }}

          async function pollStatus(jobId) {{
            const panel = document.getElementById('statusPanel');
            const stateEl = document.getElementById('statusState');
            const textEl = document.getElementById('statusText');
            const logEl = document.getElementById('statusLog');

            const interval = setInterval(async () => {{
              const response = await fetch('/status?job_id=' + encodeURIComponent(jobId));
              const data = await response.json();

              stateEl.textContent = data.state || 'unknown';
              textEl.textContent = data.progress || 'processando...';
              logEl.textContent = (data.logs || []).join('\\n');

              if (data.state === 'done' || data.state === 'error') {{
                clearInterval(interval);
                if (data.state === 'done') {{
                  window.location.reload();
                }}
              }}
            }}, 1000);
          }}

          document.addEventListener('DOMContentLoaded', () => {{
            const form = document.querySelector('form');
            if (form) {{
              form.addEventListener('submit', startSearch);
            }}
          }});
        </script>
        <style>
          body {{
            font-family: Arial, sans-serif;
            margin: 24px;
            background: #f3f4f6;
            color: #111827;
          }}
          h1 {{
            margin-bottom: 8px;
          }}
          .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 16px;
            margin: 24px 0;
          }}
          .card {{
            background: white;
            border-radius: 12px;
            padding: 18px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
          }}
          .label {{
            font-size: 12px;
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 0.04em;
          }}
          .value {{
            font-size: 28px;
            font-weight: bold;
            margin-top: 8px;
          }}
          .charts {{
            display: grid;
            grid-template-columns: 1.3fr 1fr;
            gap: 20px;
          }}
          .panel {{
            background: white;
            border-radius: 12px;
            padding: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
          }}
          table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 12px;
            overflow: hidden;
          }}
          th, td {{
            border-bottom: 1px solid #e5e7eb;
            padding: 10px 12px;
            text-align: left;
            vertical-align: top;
          }}
          th {{
            background: #e5e7eb;
          }}
          .search-box {{
            background: rgba(0,0,0,0.04);
            border: 1px solid #d1d5db;
            border-radius: 10px;
            padding: 16px 18px 10px;
            margin-top: 20px;
            margin-bottom: 24px;
          }}
          .search-title {{
            font-size: 18px;
            font-weight: 700;
            margin: 0 0 14px;
          }}
          .term-row {{
            display: grid;
            grid-template-columns: 120px 1fr 44px;
            gap: 10px;
            align-items: center;
            margin-bottom: 12px;
          }}
          select, input[type="text"] {{
            height: 42px;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            padding: 0 12px;
            font-size: 18px;
            background: #f9fafb;
            width: 100%;
            box-sizing: border-box;
          }}
          select {{
            background: #f3f4f6;
          }}
          .remove-term {{
            height: 42px;
            border: none;
            border-radius: 8px;
            background: #dc2626;
            color: white;
            font-size: 24px;
            font-weight: 700;
            cursor: pointer;
          }}
          .actions {{
            display: flex;
            gap: 16px;
            margin-top: 16px;
            margin-bottom: 20px;
          }}
          .add-term {{
            border: 2px solid #facc15;
            background: transparent;
            color: #111827;
            border-radius: 8px;
            padding: 10px 18px;
            font-weight: 600;
            cursor: pointer;
          }}
          .submit-btn {{
            background: #2563eb;
            color: white;
            border: 2px solid #2563eb;
            border-radius: 8px;
            padding: 10px 18px;
            font-weight: 600;
            cursor: pointer;
          }}
          .strategy-box {{
            background: #ffffff;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            padding: 8px;
          }}
          .strategy-box label {{
            display: block;
            font-size: 14px;
            margin-bottom: 8px;
            color: #374151;
          }}
          .strategy-box input {{
            width: 100%;
            border: none;
            font-size: 18px;
            background: transparent;
            color: #111827;
          }}
          .status-panel {{
            background: #ffffff;
            border: 1px solid #d1d5db;
            border-radius: 10px;
            padding: 14px 16px;
            margin-top: 16px;
            margin-bottom: 18px;
            display: none;
          }}
          .status-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-weight: 700;
            margin-bottom: 10px;
          }}
          .status-pill {{
            display: inline-block;
            background: #dbeafe;
            color: #1d4ed8;
            padding: 6px 10px;
            border-radius: 999px;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.02em;
          }}
          .status-log {{
            font-family: monospace;
            font-size: 12px;
            line-height: 1.7;
            background: #f9fafb;
            border-radius: 8px;
            padding: 10px 12px;
            white-space: pre-wrap;
            min-height: 48px;
          }}
        </style>
      </head>
      <body>
        <h1>BRAPCI — Pipeline de Busca e Índice de Termos</h1>

        <div class="search-box">
          <h2 class="search-title">Formulário de Termos Booleanos</h2>
          <form method="post" action="/">
            <div class="term-row">
              <select name="op_0">
                <option>AND</option>
                <option>OR</option>
              </select>
              <input type="text" name="term_0" value="ciência da informação">
              <button class="remove-term" type="button" aria-label="Remover termo">×</button>
            </div>
            <div class="term-row">
              <select name="op_1">
                <option>AND</option>
                <option>OR</option>
              </select>
              <input type="text" name="term_1" value="epistemologia">
              <button class="remove-term" type="button" aria-label="Remover termo">×</button>
            </div>
            <div class="term-row">
              <select name="op_2">
                <option>OR</option>
                <option>AND</option>
              </select>
              <input type="text" name="term_2" value="conceito">
              <button class="remove-term" type="button" aria-label="Remover termo">×</button>
            </div>
            <div class="term-row">
              <select name="op_3">
                <option>OR</option>
                <option>AND</option>
              </select>
              <input type="text" name="term_3" value="interdisciplinaridade">
              <button class="remove-term" type="button" aria-label="Remover termo">×</button>
            </div>

            <div class="actions">
              <button class="add-term" type="button">Adicionar Termo</button>
              <button class="submit-btn" type="submit">Pesquisar</button>
            </div>

            <div class="strategy-box">
              <label>Estratégia de Busca</label>
              <input type="text" name="strategy_query" value="&quot;ciência da informação&quot; AND &quot;epistemologia&quot; OR &quot;conceito&quot; OR &quot;interdisciplinaridade&quot;">
            </div>
          </form>
        </div>

        <div class="status-panel" id="statusPanel">
          <div class="status-header">
            <span>Pipeline em execução</span>
            <span class="status-pill" id="statusState">queued</span>
          </div>
          <div id="statusText">aguardando...</div>
          <div class="status-log" id="statusLog">iniciando...
</div>
        </div>

        <div class="summary">
          <div class="card">
            <div class="label">Registros coletados</div>
            <div class="value">{data['total_records']}</div>
          </div>
          <div class="card">
            <div class="label">Termos únicos</div>
            <div class="value">{data['unique_terms']}</div>
          </div>
          <div class="card">
            <div class="label">Termo mais frequente</div>
            <div class="value">{terms[0] if terms else '—'}</div>
          </div>
          <div class="card">
            <div class="label">Frequência máxima</div>
            <div class="value">{max(counts) if counts else 0}</div>
          </div>
        </div>

        <div class="charts">
          <div class="panel">
            {bar_chart.to_html(full_html=False, include_plotlyjs='cdn')}
          </div>
          <div class="panel">
            {year_chart.to_html(full_html=False, include_plotlyjs='cdn')}
          </div>
        </div>

        <h2>Resultados consolidados</h2>
        <table>
          <thead>
            <tr>
              <th>Título</th>
              <th>Autor</th>
              <th>Ano</th>
              <th>Tipo</th>
              <th>Palavras-chave</th>
            </tr>
          </thead>
          <tbody>
            {''.join(
              f"<tr><td>{record.get('title', '')}</td><td>{record.get('author', '')}</td><td>{record.get('year', '')}</td><td>{record.get('publication_type', '')}</td><td>{'; '.join(record.get('keywords', []))}</td></tr>"
              for record in data['records'][:20]
            )}
          </tbody>
        </table>
      </body>
    </html>
    """

    output_file = Path(output_path)
    output_file.write_text(html, encoding="utf-8")
    return str(output_file)


if __name__ == "__main__":
    build_dashboard_html("brapci_search_results.json", "brapci_dashboard.html")
