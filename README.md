# BibScrape

Projeto para coleta, processamento e visualização de resultados de busca do portal BRAPCI.

## Objetivo

Automatizar a busca de publicações no BRAPCI, extrair metadados relevantes e gerar um dashboard analítico com indicadores por termo e por ano.

## Stack

- Python 3.9+
- Selenium
- Plotly
- pytest

## Estrutura

```text
BibScrape/
├── brapci_pipeline.py          # processamento e indexação de termos
├── brapci_visualization.py     # geração do dashboard HTML
├── brapci_search_results.json  # dados coletados e normalizados
├── brapci_search_results.csv   # export em CSV
├── brapci_dashboard.html       # dashboard gerado
├── run_dashboard.sh             # comando para gerar e abrir o dashboard
├── tests/
│   └── test_pipeline.py        # testes do pipeline
├── pesquisas/
│   ├── brapci_selenium_search.py
│   ├── brapci_search.py
│   ├── brapci_search_results.csv
│   ├── brapci_search_results.json
│   └── requirements.txt
├── requirements.txt
└── README.md
```

## Como rodar

### 1) Instalar dependências

```bash
cd /Users/capanema/Projects/Jonas/BibScrape
/Users/capanema/Projects/Jonas/.venv/bin/python -m pip install -r requirements.txt
```

### 2) Gerar o dashboard

```bash
cd /Users/capanema/Projects/Jonas/BibScrape
./run_dashboard.sh
```

O script gera o HTML do dashboard e abre a URL local:

```text
http://localhost:8000
```

## Como rodar apenas o pipeline

```bash
cd /Users/capanema/Projects/Jonas/BibScrape
/Users/capanema/Projects/Jonas/.venv/bin/python -m pytest tests/test_pipeline.py -q
```

## Observações

- O scraper do BRAPCI usa Selenium porque a busca é renderizada no navegador e carrega resultados dinamicamente.
- As palavras-chave são extraídas na página de detalhe do trabalho, onde o site expõe o campo de palavras-chave.
- Os dados finais podem ser consultados em JSON e CSV.

## Status

Projeto funcional em etapa de pipeline e dashboard analítico.
