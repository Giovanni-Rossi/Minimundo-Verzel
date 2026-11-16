# API Biblioteca Comunitária

Back-end em **FastAPI** (Python 3.12+). Os nomes de rotas, campos e schemas seguem o contrato
`openapi-biblioteca.yaml` (branch `docs/contrato-openapi`).

## Ambiente

### Desenvolvimento local
```bash
cd api
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env
uvicorn app.main:app --reload      # http://localhost:8000/docs
```
Na primeira subida a API cria o banco SQLite (`biblioteca.db`) e semeia os leitores Ana, Bruno e Carla.

### Variáveis (`.env`)
| Variável | Padrão | Para que serve |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./biblioteca.db` | Conexão com o banco. Para Postgres, instale o driver e use `postgresql+psycopg://usuario:senha@host/banco`. |
| `CORS_ORIGINS` | `http://localhost:5173` | Endereços do front liberados, separados por vírgula. |

### Testes
```bash
pytest
```
Os testes usam um banco em memória, zerado a cada teste (`tests/conftest.py`).
`tests/test_contrato.py` falha se alguma rota ou schema sair do nome do contrato.

## Estrutura
```
app/
  main.py            cria a API, liga CORS, erros e rotas
  core/              config, banco e erros no formato {"erro": "..."}
  models/            tabelas: LivroModel, LeitorModel, EmprestimoModel, Situacao
  schemas/           JSON da API com os nomes do contrato: Livro, Leitor, Emprestimo...
  services/          regras de negócio, um service por assunto (aqui entram as features)
  routers/           rotas do contrato, já ligadas aos services
  dependencias.py    entrega os services prontos para as rotas
  seed.py            leitores iniciais
```

## Como implementar uma história
As rotas já existem e chamam o service. Por enquanto cada método responde **501** com
`{"erro": "Ainda não implementado: ..."}`. Para implementar, troque o `raise NotImplementedError`
do método da sua história:

| História | Arquivo | Métodos |
|---|---|---|
| BIBL-1 | `services/livro_service.py` | `listar_livros`, `cadastrar_livro` |
| BIBL-2 | `services/emprestimo_service.py` | `emprestar_livro`, `devolver_livro` |
| BIBL-3 | `services/relatorio_service.py` | `ranking_livros` |
| BIBL-4 | `services/relatorio_service.py` | `relatorio_emprestimos` |
| BIBL-5 | `services/relatorio_service.py` | `exportar_emprestimos_csv` |
| Leitores | `services/leitor_service.py` | `listar_leitores` |

As mensagens de erro de cada método estão na docstring dele, iguais às do contrato. Para devolver
um erro, lance a exceção do status certo de `app/core/erros.py`:
```python
raise NaoEncontrado("Livro não encontrado.")          # 404
raise Conflito("Leitor já tem 3 empréstimos ativos.")  # 409
raise RequisicaoInvalida("Título é obrigatório.")      # 400
```

## Regras de nomes
- O contrato manda. Se precisar de um nome novo, combine e atualize o contrato primeiro.
- No Python os atributos ficam em snake_case (`copias_disponiveis`). O JSON sai em camelCase
  (`copiasDisponiveis`) automaticamente pelo `SchemaBase`.
- Tabelas levam o sufixo `Model` para não colidir com os schemas de mesmo nome.
