"""Garante que os nomes da API continuam batendo com o contrato openapi-biblioteca.yaml."""

OPERACOES_DO_CONTRATO = {
    ("get", "/livros"): "listarLivros",
    ("post", "/livros"): "cadastrarLivro",
    ("get", "/livros/ranking"): "rankingLivros",
    ("get", "/leitores"): "listarLeitores",
    ("get", "/emprestimos"): "relatorioEmprestimos",
    ("post", "/emprestimos"): "emprestarLivro",
    ("post", "/emprestimos/{id}/devolucao"): "devolverLivro",
    ("get", "/emprestimos/export.csv"): "exportarEmprestimosCsv",
}

SCHEMAS_DO_CONTRATO = {
    "Erro",
    "Situacao",
    "LivroNovo",
    "Livro",
    "Leitor",
    "LivroResumo",
    "EmprestimoNovo",
    "Emprestimo",
    "ItemRanking",
}


def test_rotas_e_operation_ids_batem_com_o_contrato(client):
    paths = client.get("/openapi.json").json()["paths"]
    encontradas = {
        (metodo, caminho): operacao["operationId"]
        for caminho, metodos in paths.items()
        for metodo, operacao in metodos.items()
    }
    assert OPERACOES_DO_CONTRATO.items() <= encontradas.items()


def test_schemas_batem_com_o_contrato(client):
    schemas = set(client.get("/openapi.json").json()["components"]["schemas"])
    assert SCHEMAS_DO_CONTRATO <= schemas


def test_erro_de_validacao_sai_no_formato_do_contrato(client):
    resposta = client.post("/emprestimos", json={})
    assert resposta.status_code == 400
    assert "erro" in resposta.json()
