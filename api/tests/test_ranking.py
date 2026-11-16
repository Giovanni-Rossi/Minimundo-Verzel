"""BIBL-3 — Ranking de livros mais emprestados (GET /livros/ranking)."""

from datetime import datetime

DIA = datetime(2026, 11, 10, 14, 0)


def test_sem_emprestimos_devolve_lista_vazia(client, criar):
    criar.livro("Dom Casmurro")

    resposta = client.get("/livros/ranking")

    assert resposta.status_code == 200
    assert resposta.json() == []


def test_ordena_do_mais_emprestado_para_o_menos(client, criar):
    ana = criar.leitor("Ana")
    pouco = criar.livro("Pouco procurado")
    muito = criar.livro("Muito procurado")
    medio = criar.livro("Médio")
    for _ in range(3):
        criar.emprestimo(muito, ana, em=DIA, devolvido_em=DIA)
    for _ in range(2):
        criar.emprestimo(medio, ana, em=DIA, devolvido_em=DIA)
    criar.emprestimo(pouco, ana, em=DIA)

    resposta = client.get("/livros/ranking")

    assert resposta.status_code == 200
    assert resposta.json() == [
        {"livroId": muito.id, "titulo": "Muito procurado", "totalEmprestimos": 3},
        {"livroId": medio.id, "titulo": "Médio", "totalEmprestimos": 2},
        {"livroId": pouco.id, "titulo": "Pouco procurado", "totalEmprestimos": 1},
    ]


def test_conta_emprestimos_ativos_e_devolvidos(client, criar):
    ana = criar.leitor("Ana")
    livro = criar.livro("Dom Casmurro")
    criar.emprestimo(livro, ana, em=DIA)
    criar.emprestimo(livro, ana, em=DIA, devolvido_em=DIA)

    assert client.get("/livros/ranking").json()[0]["totalEmprestimos"] == 2


def test_livro_nunca_emprestado_nao_aparece(client, criar):
    ana = criar.leitor("Ana")
    emprestado = criar.livro("Emprestado")
    criar.livro("Nunca emprestado")
    criar.emprestimo(emprestado, ana, em=DIA)

    titulos = [item["titulo"] for item in client.get("/livros/ranking").json()]

    assert titulos == ["Emprestado"]


def test_empate_e_desempatado_pelo_titulo(client, criar):
    ana = criar.leitor("Ana")
    criar.emprestimo(criar.livro("Zumbi"), ana, em=DIA)
    criar.emprestimo(criar.livro("Abril"), ana, em=DIA)

    titulos = [item["titulo"] for item in client.get("/livros/ranking").json()]

    assert titulos == ["Abril", "Zumbi"]
