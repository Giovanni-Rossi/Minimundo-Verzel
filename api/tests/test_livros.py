"""BIBL-1: cadastro e listagem de livros."""

from datetime import date

import pytest

LIVRO = {"titulo": "Dom Casmurro", "autor": "Machado de Assis", "ano": 1899, "copiasDisponiveis": 3}


def cadastrar(client, **mudancas):
    return client.post("/livros", json={**LIVRO, **mudancas})


def test_acervo_vazio_devolve_lista_vazia(client):
    resposta = client.get("/livros")
    assert resposta.status_code == 200
    assert resposta.json() == []


def test_livro_cadastrado_aparece_na_listagem(client):
    resposta = cadastrar(client)
    assert resposta.status_code == 201
    livro = resposta.json()
    assert livro == {"id": livro["id"], **LIVRO}
    assert client.get("/livros").json() == [livro]


def test_titulo_e_gravado_sem_espacos_nas_pontas(client):
    assert cadastrar(client, titulo="  Dom Casmurro  ").json()["titulo"] == "Dom Casmurro"


@pytest.mark.parametrize("titulo", ["", "   "])
def test_titulo_vazio_e_recusado(client, titulo):
    resposta = cadastrar(client, titulo=titulo)
    assert resposta.status_code == 400
    assert resposta.json() == {"erro": "Título é obrigatório."}


def test_ano_no_futuro_e_recusado(client):
    resposta = cadastrar(client, ano=date.today().year + 1)
    assert resposta.status_code == 400
    assert resposta.json() == {"erro": "Ano não pode ser no futuro."}


def test_ano_atual_e_aceito(client):
    assert cadastrar(client, ano=date.today().year).status_code == 201


def test_copias_negativas_sao_recusadas(client):
    resposta = cadastrar(client, copiasDisponiveis=-1)
    assert resposta.status_code == 400
    assert resposta.json() == {"erro": "Cópias não podem ser negativas."}


def test_zero_copias_e_aceito(client):
    assert cadastrar(client, copiasDisponiveis=0).status_code == 201


def test_cadastro_recusado_nao_entra_no_acervo(client):
    cadastrar(client, titulo="")
    assert client.get("/livros").json() == []
