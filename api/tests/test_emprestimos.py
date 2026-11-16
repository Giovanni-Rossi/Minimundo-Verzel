"""BIBL-2: empréstimo e devolução de livros."""

from app.models import PerfilUsuario


def emprestar(client, livro_id, leitor_id):
    return client.post("/emprestimos", json={"livroId": livro_id, "leitorId": leitor_id})


def devolver(client, emprestimo_id):
    return client.post(f"/emprestimos/{emprestimo_id}/devolucao")


def copias(client, livro_id):
    """Cópias como a tela vê, pela listagem do acervo."""
    return next(l["copiasDisponiveis"] for l in client.get("/livros").json() if l["id"] == livro_id)


def test_emprestar_registra_e_diminui_copias(client, novo_livro, novo_leitor):
    livro = novo_livro(copias=2)
    leitor = novo_leitor("Ana")

    resposta = emprestar(client, livro.id, leitor.id)

    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["livro"] == {"id": livro.id, "titulo": "Dom Casmurro"}
    assert corpo["leitor"] == {"id": leitor.id, "nome": "Ana"}
    assert corpo["situacao"] == "ativo"
    assert corpo["dataEmprestimo"]
    assert corpo["dataDevolucao"] is None
    assert copias(client, livro.id) == 1


def test_livro_sem_copias_e_recusado(client, novo_livro, novo_leitor):
    livro = novo_livro(copias=0)
    leitor = novo_leitor()

    resposta = emprestar(client, livro.id, leitor.id)

    assert resposta.status_code == 409
    assert resposta.json() == {"erro": "Livro sem cópias disponíveis."}
    assert copias(client, livro.id) == 0


def test_quarto_emprestimo_ativo_e_recusado(client, novo_livro, novo_leitor):
    leitor = novo_leitor()
    livros = [novo_livro(titulo=f"Livro {n}") for n in range(4)]
    for livro in livros[:3]:
        assert emprestar(client, livro.id, leitor.id).status_code == 201

    resposta = emprestar(client, livros[3].id, leitor.id)

    assert resposta.status_code == 409
    assert resposta.json() == {"erro": "Leitor já tem 3 empréstimos ativos."}
    assert copias(client, livros[3].id) == 1


def test_devolver_libera_vaga_no_limite(client, novo_livro, novo_leitor):
    leitor = novo_leitor()
    livros = [novo_livro(titulo=f"Livro {n}") for n in range(4)]
    ids = [emprestar(client, livro.id, leitor.id).json()["id"] for livro in livros[:3]]

    devolver(client, ids[0])

    assert emprestar(client, livros[3].id, leitor.id).status_code == 201


def test_livro_inexistente(client, novo_leitor):
    resposta = emprestar(client, 999, novo_leitor().id)
    assert resposta.status_code == 404
    assert resposta.json() == {"erro": "Livro não encontrado."}


def test_leitor_inexistente(client, novo_livro):
    resposta = emprestar(client, novo_livro().id, 999)
    assert resposta.status_code == 404
    assert resposta.json() == {"erro": "Leitor não encontrado."}


def test_bibliotecario_nao_pega_livro(client, novo_livro, novo_leitor):
    bibliotecaria = novo_leitor("Bia", PerfilUsuario.BIBLIOTECARIO)
    resposta = emprestar(client, novo_livro().id, bibliotecaria.id)
    assert resposta.status_code == 404
    assert resposta.json() == {"erro": "Leitor não encontrado."}


def test_devolver_encerra_e_aumenta_copias(client, novo_livro, novo_leitor):
    livro = novo_livro(copias=1)
    emprestimo_id = emprestar(client, livro.id, novo_leitor().id).json()["id"]

    resposta = devolver(client, emprestimo_id)

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["situacao"] == "devolvido"
    assert corpo["dataDevolucao"]
    assert copias(client, livro.id) == 1


def test_devolver_duas_vezes_nao_soma_de_novo(client, novo_livro, novo_leitor):
    livro = novo_livro(copias=1)
    emprestimo_id = emprestar(client, livro.id, novo_leitor().id).json()["id"]
    devolver(client, emprestimo_id)

    resposta = devolver(client, emprestimo_id)

    assert resposta.status_code == 409
    assert resposta.json() == {"erro": "Empréstimo já devolvido."}
    assert copias(client, livro.id) == 1


def test_devolver_emprestimo_inexistente(client):
    resposta = devolver(client, 999)
    assert resposta.status_code == 404
    assert resposta.json() == {"erro": "Empréstimo não encontrado."}


def test_listar_leitores_mostra_so_leitores(client, novo_leitor):
    ana = novo_leitor("Ana")
    novo_leitor("Bia", PerfilUsuario.BIBLIOTECARIO)

    assert client.get("/leitores").json() == [{"id": ana.id, "nome": "Ana"}]
