from pesquisas.brapci_subject_index import parse_subject_text


def test_parse_subject_text_extracts_real_terms():
    sample = """
A(pt)
A amazon(pt)
A análise se estrutura em 9 grupos(pt)
Idioma: pt - Total: 4568 de Assuntos
"""

    terms = parse_subject_text(sample, "A")

    assert terms == ["A amazon", "A análise se estrutura em 9 grupos"]
