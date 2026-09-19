# BibScrape

Projeto para automação de busca, extração de metadados e visualização analítica de resultados do portal BRAPCI.

## Objetivo

Automatizar consultas ao BRAPCI, navegar pelo comportamento real do site em navegador, coletar publicações relevantes, enriquecer os registros com palavras-chave e apresentar os dados em um dashboard local.

## Funcionalidades

- Busca automatizada em navegador com Selenium
- Carregamento dinâmico da página com scroll infinito
- Extração de título, autor, ano, tipo de publicação e palavras-chave
- Exportação dos registros em CSV e JSON
- Pipeline de normalização e agregação por ano/termo
- Dashboard web local com status em tempo real
- Coletor separado de termos por índice de assunto A–Z

## Stack

- Python 3.9+
- Selenium
- Flask-like local HTTP server para dashboard
- Plotly (quando usado em visualizações do dashboard)
- pytest

## Estrutura do projeto

```text
BibScrape/
├── brapci_pipeline.py                 # normalização, indexação e agregação
├── brapci_visualization.py            # geração da interface visual do dashboard
├── brapci_dashboard.html             # dashboard HTML renderizado
├── dashboard_server.py                # servidor local para UI e execução do pipeline
├── run_dashboard.sh                  # launcher do dashboard
├── requirements.txt                  # dependências do projeto
├── README.md                         # documentação
├── tests/
│   ├── test_pipeline.py              # testes do pipeline de normalização
│   └── test_subject_index.py         # teste do parser do índice de assuntos
├── pesquisas/
│   ├── brapci_selenium_search.py     # automação da busca no BRAPCI
│   ├── brapci_search.py              # protótipo de busca
│   ├── brapci_subject_index.py       # coleta de termos por letra A–Z
│   ├── brapci_subject_terms.csv     # termos extraídos por assunto
│   ├── brapci_search_results.csv    # resultados gerados pela busca
│   ├── brapci_search_results.json   # resultados em JSON
│   └── requirements.txt
└── .gitignore
```

## Requisitos

- Python 3.9+
- Chrome/Chromium disponível no ambiente
- Dependências do projeto instaladas no ambiente virtual

## Como rodar

### 1) Instalar dependências

```bash
cd /Users/capanema/Projects/Jonas/BibScrape
/Users/capanema/Projects/Jonas/.venv/bin/python -m pip install -r requirements.txt
```

### 2) Abrir o dashboard

```bash
cd /Users/capanema/Projects/Jonas/BibScrape
./run_dashboard.sh
```

Esse comando inicia o servidor local e abre:

```text
http://localhost:8000
```

### 3) Executar a busca automatizada

A busca completa roda via dashboard ou executando diretamente o pipeline do navegador, conforme a interface do projeto.

### 4) Coletar termos do índice A–Z

```bash
cd /Users/capanema/Projects/Jonas/BibScrape
/Users/capanema/Projects/Jonas/.venv/bin/python pesquisas/brapci_subject_index.py
```

O script salva os termos em:

```text
pesquisas/brapci_subject_terms.csv
```

## Testes

```bash
cd /Users/capanema/Projects/Jonas/BibScrape
/Users/capanema/Projects/Jonas/.venv/bin/python -m pytest -q
```

## Observações importantes

- O BRAPCI não expõe uma API estável e simples para os dados de busca; por isso, a solução usa Selenium para reproduzir o comportamento real do navegador.
- A paginação/scroll infinito é necessário porque o site carrega blocos de resultados enquanto o usuário desce na página.
- As palavras-chave nem sempre aparecem na listagem inicial; muitas vezes elas só são acessíveis na página de detalhe do artigo.
- O projeto foi estruturado para gerar dados em CSV/JSON e permitir validação visual em tempo real no dashboard local.

## Status atual

O projeto está funcional para automação, extração, armazenamento e visualização local dos dados do BRAPCI, incluindo a coleta do índice de assuntos por letras A–Z.
