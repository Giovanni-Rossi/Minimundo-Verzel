"""GET /leitores: lista os leitores semeados no banco."""

from app.models import LeitorModel
from app.seed import semear_leitores


def test_sem_leitores_devolve_lista_vazia(client):
    resposta = client.get("/leitores")

    assert resposta.status_code == 200
    assert resposta.json() == []


def test_lista_leitores_no_formato_do_contrato_ordenados_por_id(client, db):
    db.add_all([LeitorModel(id=2, nome="Bruno"), LeitorModel(id=1, nome="Ana")])
    db.commit()

    resposta = client.get("/leitores")

    assert resposta.status_code == 200
    assert resposta.json() == [{"id": 1, "nome": "Ana"}, {"id": 2, "nome": "Bruno"}]


def test_lista_os_leitores_do_seed(client, db):
    semear_leitores(db)

    nomes = [leitor["nome"] for leitor in client.get("/leitores").json()]

    assert nomes == ["Ana", "Bruno", "Carla"]


def test_seed_nao_duplica_leitores_ao_rodar_de_novo(client, db):
    semear_leitores(db)
    semear_leitores(db)

    assert len(client.get("/leitores").json()) == 3
