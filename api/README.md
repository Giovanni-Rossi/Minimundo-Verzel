# API Biblioteca Comunitária

Back-end em **FastAPI** (Python 3.12+). Os nomes de rotas, campos e schemas seguem o contrato
`openapi-biblioteca.yaml`. O acesso ao banco é feito pelo **SQLAlchemy** (o ORM), mapeando as
tabelas que o time de banco criou.

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
Com o `.env` padrão a API usa um SQLite local (`biblioteca.db`), cria as tabelas e semeia os
leitores Ana, Bruno e Carla.

### Usando o Postgres do time de banco
No `api/.env` (que não vai para o git):
```
DATABASE_URL=<link que o time de banco passou>
CRIAR_TABELAS=false
```
Com `CRIAR_TABELAS=false` a API não cria nem altera tabelas: só lê e grava dados nas que já
existem. O link pode vir como `postgresql://...`; a API troca para o driver `psycopg` sozinha.
Nunca coloque o link com senha no código, no README ou no `.env.example`.

### Variáveis (`.env`)
| Variável | Padrão | Para que serve |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./biblioteca.db` | Conexão com o banco (SQLite local ou Postgres). |
| `CRIAR_TABELAS` | `true` | `true` cria tabelas e semeia leitores (local). `false` usa o schema do time de banco sem mexer. |
| `CORS_ORIGINS` | `http://localhost:5173` | Endereços do front liberados, separados por vírgula. |

### Deploy no Dokploy
1. Crie uma **Application** apontando para este repositório, branch de deploy, **Build Path `/api`**
   e **Build Type `Dockerfile`** (o arquivo é `api/Dockerfile`).
2. Em **Environment**, configure (nada disso vai para o git):
   | Variável | Valor |
   |---|---|
   | `DATABASE_URL` | link do Postgres do time de banco |
   | `CORS_ORIGINS` | `https://<domínio do front>` (mais de um: separe por vírgula) |
   | `CRIAR_TABELAS` | já vem `false` na imagem; não mude em produção |
3. Em **Domains**, crie o domínio do back com **porta 8000** e HTTPS.
4. Faça o deploy e abra `https://<domínio do back>/docs` para conferir.
5. No front, configure `VITE_API_URL=https://<domínio do back>` e faça **rebuild** do front
   (o Vite grava essa variável no build; só reiniciar não basta).

Para testar a imagem localmente:
```bash
docker build -t biblioteca-api .
docker run --rm -p 8000:8000 -e CRIAR_TABELAS=true biblioteca-api   # SQLite dentro do container
```

### Testes
```bash
pytest
```
Os testes usam um banco em memória criado a partir dos models, zerado a cada teste
(`tests/conftest.py`). As fixtures `novo_leitor` e `novo_livro` criam os dados de cada teste.
`tests/test_contrato.py` falha se alguma rota ou schema sair do nome do contrato.

## Estrutura
```
app/
  main.py            cria a API, liga CORS, erros e rotas
  core/              config, banco e erros no formato {"erro": "..."}
  models/            mapeamento das tabelas do banco (único lugar com nomes do SQL)
  schemas/           JSON da API com os nomes do contrato: Livro, Leitor, Emprestimo...
  services/          regras de negócio, um service por assunto
  routers/           rotas do contrato, já ligadas aos services
  dependencias.py    entrega os services prontos para as rotas
  seed.py            leitores de exemplo para o banco local
```

## Mapeamento do banco
O código usa os nomes do contrato. Onde o banco do time de banco usa outro nome, a diferença
fica só em `app/models/`:

| Contrato (código) | Banco |
|---|---|
| `LeitorModel` / `Leitor` | tabela `usuarios`, só quem tem `perfil = leitor` |
| `ano` | coluna `livros.ano_publicacao` |
| `situacao` (`ativo`/`devolvido`) | coluna `emprestimos.status` (`ATIVO`/`DEVOLVIDO`) |

O banco exige que `status` e `data_devolucao` andem juntos (ATIVO sem data, DEVOLVIDO com data).
Se o SQL do time de banco mudar, ajuste só os models.

## Situação das histórias
Métodos ainda não implementados respondem **501** com `{"erro": "Ainda não implementado: ..."}`.
Para implementar, troque o `raise NotImplementedError` do método da história:

| História | Arquivo | Métodos | Situação |
|---|---|---|---|
| BIBL-1 | `services/livro_service.py` | `listar_livros`, `cadastrar_livro` | feito |
| BIBL-2 | `services/emprestimo_service.py` | `emprestar_livro`, `devolver_livro` | feito |
| Leitores | `services/leitor_service.py` | `listar_leitores` | feito |
| BIBL-3 | `services/relatorio_service.py` | `ranking_livros` | a fazer |
| BIBL-4 | `services/relatorio_service.py` | `relatorio_emprestimos` | a fazer |
| BIBL-5 | `services/relatorio_service.py` | `exportar_emprestimos_csv` | a fazer |

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
