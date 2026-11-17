"""BIBL-4 — Relatório de empréstimos com filtros (GET /emprestimos)."""

from datetime import datetime, timezone

import pytest


@pytest.fixture
def cenario(criar):
    """Ana e Bruno com empréstimos em datas e situações diferentes."""
    ana, bruno = criar.leitor("Ana"), criar.leitor("Bruno")
    dom, iracema = criar.livro("Dom Casmurro"), criar.livro("Iracema")
    return {
        "ana": ana,
        "bruno": bruno,
        # ativo, Ana, 05/11
        "a1": criar.emprestimo(dom, ana, em=datetime(2026, 11, 5, 10, 0)),
        # devolvido, Ana, 12/11
        "a2": criar.emprestimo(
            iracema, ana, em=datetime(2026, 11, 12, 9, 0), devolvido_em=datetime(2026, 11, 14, 9, 0)
        ),
        # ativo, Bruno, 30/11 às 23h (borda do "fim" inclusivo)
        "b1": criar.emprestimo(iracema, bruno, em=datetime(2026, 11, 30, 23, 0)),
        # devolvido, Bruno, 02/12
        "b2": criar.emprestimo(
            dom, bruno, em=datetime(2026, 12, 2, 8, 0), devolvido_em=datetime(2026, 12, 3, 8, 0)
        ),
    }


def ids(resposta) -> list[int]:
    assert resposta.status_code == 200, resposta.json()
    return [emprestimo["id"] for emprestimo in resposta.json()]


def test_sem_filtros_lista_todos_do_mais_recente_para_o_mais_antigo(client, cenario):
    resposta = client.get("/emprestimos")

    assert ids(resposta) == [cenario[k].id for k in ("b2", "b1", "a2", "a1")]


def test_cada_item_tem_livro_leitor_data_e_situacao_no_formato_do_contrato(client, cenario):
    item = client.get("/emprestimos", params={"leitorId": cenario["ana"].id}).json()[-1]

    assert item["livro"] == {"id": cenario["a1"].livro_id, "titulo": "Dom Casmurro"}
    assert item["leitor"] == {"id": cenario["ana"].id, "nome": "Ana"}
    assert item["dataEmprestimo"].startswith("2026-11-05T10:00")
    assert item["dataDevolucao"] is None
    assert item["situacao"] == "ativo"


def test_filtra_por_leitor(client, cenario):
    resposta = client.get("/emprestimos", params={"leitorId": cenario["bruno"].id})

    assert ids(resposta) == [cenario["b2"].id, cenario["b1"].id]


def test_filtra_por_situacao_ativo(client, cenario):
    resposta = client.get("/emprestimos", params={"situacao": "ativo"})

    assert ids(resposta) == [cenario["b1"].id, cenario["a1"].id]


def test_filtra_por_situacao_devolvido(client, cenario):
    resposta = client.get("/emprestimos", params={"situacao": "devolvido"})

    assert ids(resposta) == [cenario["b2"].id, cenario["a2"].id]


def test_filtra_por_data_inicial_inclusiva(client, cenario):
    resposta = client.get("/emprestimos", params={"inicio": "2026-11-12"})

    assert ids(resposta) == [cenario[k].id for k in ("b2", "b1", "a2")]


def test_data_final_inclui_o_dia_inteiro(client, cenario):
    resposta = client.get("/emprestimos", params={"fim": "2026-11-30"})

    assert ids(resposta) == [cenario[k].id for k in ("b1", "a2", "a1")]


def test_filtros_combinados_aplicam_todos_ao_mesmo_tempo(client, cenario):
    resposta = client.get(
        "/emprestimos",
        params={
            "leitorId": cenario["bruno"].id,
            "inicio": "2026-11-01",
            "fim": "2026-11-30",
            "situacao": "ativo",
        },
    )

    assert ids(resposta) == [cenario["b1"].id]


def test_nenhum_resultado_devolve_lista_vazia(client, cenario):
    resposta = client.get(
        "/emprestimos", params={"leitorId": cenario["ana"].id, "inicio": "2026-12-01"}
    )

    assert resposta.status_code == 200
    assert resposta.json() == []


def test_sem_emprestimos_no_banco_devolve_lista_vazia(client):
    resposta = client.get("/emprestimos")

    assert resposta.status_code == 200
    assert resposta.json() == []


def test_inicio_depois_do_fim_e_recusado_com_mensagem(client, cenario):
    resposta = client.get("/emprestimos", params={"inicio": "2026-11-30", "fim": "2026-11-01"})

    assert resposta.status_code == 400
    assert resposta.json() == {"erro": "Data inicial não pode ser depois da data final."}


def test_data_mal_formatada_e_recusada_no_formato_do_contrato(client):
    resposta = client.get("/emprestimos", params={"inicio": "30/11/2026"})

    assert resposta.status_code == 400
    assert "erro" in resposta.json()


# ---------- Fuso horário: os dias dos filtros e do CSV são os dias de Brasília ----------
# O banco guarda o instante em UTC. Brasília é UTC-3: 01h UTC do dia 17 ainda é 22h do dia 16.
NOITE_DIA_16_EM_BRASILIA = datetime(2026, 11, 17, 1, 0, tzinfo=timezone.utc)


def test_emprestimo_a_noite_conta_no_dia_de_brasilia_para_a_data_final(client, criar):
    emprestimo = criar.emprestimo(
        criar.livro("Dom Casmurro"), criar.leitor("Ana"), em=NOITE_DIA_16_EM_BRASILIA
    )

    resposta = client.get("/emprestimos", params={"fim": "2026-11-16"})

    assert ids(resposta) == [emprestimo.id]


def test_emprestimo_a_noite_nao_entra_no_dia_seguinte_pela_data_inicial(client, criar):
    criar.emprestimo(criar.livro("Dom Casmurro"), criar.leitor("Ana"), em=NOITE_DIA_16_EM_BRASILIA)

    resposta = client.get("/emprestimos", params={"inicio": "2026-11-17"})

    assert ids(resposta) == []


def test_csv_mostra_a_data_no_dia_de_brasilia(client, criar):
    criar.emprestimo(criar.livro("Dom Casmurro"), criar.leitor("Ana"), em=NOITE_DIA_16_EM_BRASILIA)

    linhas = client.get("/emprestimos/export.csv").text.lstrip("﻿").splitlines()

    assert linhas[1] == "Dom Casmurro,Ana,2026-11-16,ativo"
