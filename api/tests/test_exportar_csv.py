"""GET /emprestimos/export.csv (BIBL-5).

O CSV reaproveita o relatorio_emprestimos (BIBL-4). Para testar o BIBL-5 sozinho, os testes
substituem o relatório por uma lista conhecida (fixture relatorio_fake). O último teste usa o
relatório de verdade e só passa quando o BIBL-4 estiver implementado.
"""

from datetime import date, datetime, timezone

import pytest

from app.models import EmprestimoModel, LeitorModel, LivroModel, Situacao
from app.schemas import FiltroRelatorio
from app.services.relatorio_service import RelatorioService

BOM = "﻿"
CABECALHO = "livro,leitor,data,situacao\r\n"


@pytest.fixture
def emprestimos(db):
    """Dois empréstimos salvos no banco: um ativo e um devolvido."""
    ana = LeitorModel(nome="Ana")
    bruno = LeitorModel(nome="Bruno")
    dom_casmurro = LivroModel(titulo="Dom Casmurro", autor="Machado de Assis", ano=1899, copias_disponiveis=2)
    iracema = LivroModel(titulo="Iracema", autor="José de Alencar", ano=1865, copias_disponiveis=1)
    lista = [
        EmprestimoModel(
            livro=dom_casmurro,
            leitor=ana,
            data_emprestimo=datetime(2026, 11, 16, 19, 30, tzinfo=timezone.utc),
            data_devolucao=None,
            situacao=Situacao.ATIVO,
        ),
        EmprestimoModel(
            livro=iracema,
            leitor=bruno,
            data_emprestimo=datetime(2026, 11, 2, 10, 0, tzinfo=timezone.utc),
            data_devolucao=datetime(2026, 11, 9, 10, 0, tzinfo=timezone.utc),
            situacao=Situacao.DEVOLVIDO,
        ),
    ]
    db.add_all(lista)
    db.commit()
    return lista


@pytest.fixture
def relatorio_fake(monkeypatch):
    """Troca o relatório (BIBL-4) por uma lista fixa e guarda o filtro que ele recebeu."""
    chamada = {"resultado": [], "filtro": None}

    def falso(self, filtro):
        chamada["filtro"] = filtro
        return chamada["resultado"]

    monkeypatch.setattr(RelatorioService, "relatorio_emprestimos", falso)
    return chamada


def test_sem_resultados_gera_so_o_cabecalho(client, relatorio_fake):
    resposta = client.get("/emprestimos/export.csv")

    assert resposta.status_code == 200
    assert resposta.content.decode("utf-8") == BOM + CABECALHO


def test_resposta_e_um_arquivo_csv_para_download(client, relatorio_fake):
    resposta = client.get("/emprestimos/export.csv")

    assert resposta.headers["content-type"].startswith("text/csv")
    assert resposta.headers["content-disposition"] == 'attachment; filename="emprestimos.csv"'
    assert resposta.content.startswith(b"\xef\xbb\xbf")  # BOM UTF-8


def test_uma_linha_por_emprestimo_com_livro_leitor_data_e_situacao(client, relatorio_fake, emprestimos):
    relatorio_fake["resultado"] = emprestimos

    texto = client.get("/emprestimos/export.csv").content.decode("utf-8")

    assert texto == (
        BOM
        + CABECALHO
        + "Dom Casmurro,Ana,2026-11-16,ativo\r\n"
        + "Iracema,Bruno,2026-11-02,devolvido\r\n"
    )


def test_texto_com_virgula_ou_aspas_e_escapado(client, relatorio_fake, emprestimos):
    emprestimos[0].livro.titulo = 'Ah, "é"?'
    relatorio_fake["resultado"] = emprestimos[:1]

    texto = client.get("/emprestimos/export.csv").content.decode("utf-8")

    assert texto.splitlines()[1] == '"Ah, ""é""?",Ana,2026-11-16,ativo'


def test_repassa_os_filtros_da_url_para_o_relatorio(client, relatorio_fake):
    client.get("/emprestimos/export.csv?leitorId=1&inicio=2026-11-01&fim=2026-11-30&situacao=ativo")

    assert relatorio_fake["filtro"] == FiltroRelatorio(
        leitor_id=1, inicio=date(2026, 11, 1), fim=date(2026, 11, 30), situacao=Situacao.ATIVO
    )


@pytest.mark.parametrize(
    "query",
    ["inicio=16-11-2026", "fim=amanha", "situacao=perdido", "leitorId=0", "leitorId=abc"],
)
def test_filtro_mal_formatado_volta_400_em_json(client, relatorio_fake, query):
    resposta = client.get(f"/emprestimos/export.csv?{query}")

    assert resposta.status_code == 400
    assert "erro" in resposta.json()


@pytest.mark.xfail(reason="Depende do relatorio_emprestimos (BIBL-4) ainda não implementado.")
def test_csv_reflete_os_filtros_do_relatorio_de_verdade(client, emprestimos):
    resposta = client.get("/emprestimos/export.csv?situacao=devolvido")

    assert resposta.status_code == 200
    assert resposta.content.decode("utf-8") == BOM + CABECALHO + "Iracema,Bruno,2026-11-02,devolvido\r\n"
