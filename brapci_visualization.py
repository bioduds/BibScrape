import json
from pathlib import Path

import plotly.graph_objects as go

from brapci_pipeline import build_dashboard_data


def build_dashboard_html(input_path: str, output_path: str):
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
        </style>
      </head>
      <body>
        <h1>BRAPCI — Pipeline de Busca e Índice de Termos</h1>

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
