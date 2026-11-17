# Minimundo-Verzel

Sistema de controle de acervo para a **Biblioteca Comunitária** do bairro: catálogo de livros,
empréstimos e devoluções, ranking dos mais procurados e relatório com exportação em CSV.

**No ar:** https://biblioteca-comunitaria.duckdns.org · API: `/api` · Swagger: `/api/docs`

| Parte | Tecnologia | Documentação |
|---|---|---|
| Front-end (`web/`) | React 19 + Vite | [web/README.md](web/README.md) |
| API (`api/`) | Python 3.12 + FastAPI + SQLAlchemy | [api/README.md](api/README.md) |
| Banco (`database/`) | PostgreSQL | [database/README.md](database/README.md) |
| Contrato (`openapi-biblioteca.yaml`) | OpenAPI 3.1 | [docs/API.md](docs/API.md) |

| Documento | Conteúdo |
|---|---|
| [docs/ARQUITETURA.md](docs/ARQUITETURA.md) | Camadas, fluxo de uma requisição, decisões e trade-offs |
| [docs/BANCO.md](docs/BANCO.md) | Schema: diagrama, tabelas, regras, trigger, view e índices |
| [docs/API.md](docs/API.md) | Rotas, formatos, mensagens de erro e exemplos |
| [docs/DEPLOY.md](docs/DEPLOY.md) | Publicação na VPS (Docker Compose + Caddy) e no Dokploy |

## Sumário

- [O minimundo](#o-minimundo)
- [Regras de funcionamento da biblioteca](#regras-de-funcionamento-da-biblioteca)
- [Histórias](#histórias)
  - [BIBL-1 — Cadastro e listagem de livros](#bibl-1--cadastro-e-listagem-de-livros)
  - [BIBL-2 — Empréstimo e devolução de livros](#bibl-2--empréstimo-e-devolução-de-livros)
  - [BIBL-3 — Ranking de livros mais emprestados](#bibl-3--ranking-de-livros-mais-emprestados)
  - [BIBL-4 — Relatório de empréstimos](#bibl-4--relatório-de-empréstimos)
  - [BIBL-5 — Exportação do relatório de empréstimos](#bibl-5--exportação-do-relatório-de-empréstimos)
- [Visão da solução](#visão-da-solução)
- [Como rodar localmente](#como-rodar-localmente)
- [Estrutura do repositório](#estrutura-do-repositório)
- [Comportamentos a conhecer](#comportamentos-a-conhecer)

## O minimundo

A Biblioteca Comunitária do bairro sempre controlou seu acervo no papel. Com o crescimento do número de leitores, o caderno de empréstimos virou uma bagunça: ninguém sabe ao certo quais livros estão disponíveis, quem está com o quê, nem quais títulos têm mais saída. A bibliotecária responsável pediu ajuda para informatizar esse controle.

Fomos convidados para construir a primeira versão dessa aplicação. O sistema precisa dar conta do dia a dia da biblioteca:

- manter o catálogo de livros;
- controlar empréstimos e devoluções;
- oferecer algumas visões que ajudem a bibliotecária a entender o uso do acervo.

## Regras de funcionamento da biblioteca

1. Cada livro tem um **título**, um **autor**, o **ano de publicação** e um **número de cópias disponíveis**.
2. Um livro só pode ser emprestado se houver cópia disponível. Ao emprestar, uma cópia sai de circulação; ao devolver, ela retorna.
3. Cada leitor pode estar com **no máximo 3 livros** emprestados ao mesmo tempo.
4. A biblioteca quer acompanhar tanto o **histórico de cada leitor** quanto os **títulos mais procurados**.

## Histórias

### BIBL-1 — Cadastro e listagem de livros

> Como **bibliotecário**, quero **cadastrar livros e visualizar o acervo**, para **manter o catálogo da biblioteca atualizado e acessível**.

Um livro possui título, autor, ano de publicação e quantidade de cópias disponíveis. A aplicação deve expor uma API para essas operações e uma tela que a consuma.

**Critérios de aceite**

- [x] É possível cadastrar um livro com título, autor, ano e quantidade de cópias.
- [x] Após o cadastro, o livro aparece na listagem sem recarregar a página manualmente.
- [x] A tela principal exibe a lista de livros com seus dados.
- [x] Cadastro com título vazio é recusado e a mensagem de erro é exibida na tela.
- [x] Cadastro com ano no futuro é recusado e a mensagem de erro é exibida na tela.
- [x] Cadastro com quantidade de cópias negativa é recusado e a mensagem de erro é exibida na tela.

### BIBL-2 — Empréstimo e devolução de livros

> Como **usuário da biblioteca**, quero **pegar livros emprestados e devolvê-los**, para **consumir o acervo respeitando a disponibilidade de cópias**.

Ao emprestar, a quantidade de cópias disponíveis do livro diminui em 1. Ao devolver, aumenta em 1. Um usuário não pode manter mais de 3 empréstimos ativos ao mesmo tempo.

**Critérios de aceite**

- [x] Emprestar um livro com cópia disponível registra o empréstimo e diminui as cópias em 1.
- [x] A tela reflete a nova quantidade de cópias após o empréstimo.
- [x] Emprestar um livro com 0 cópias disponíveis é recusado e o usuário é avisado na tela.
- [x] Devolver um livro emprestado encerra o empréstimo e aumenta as cópias em 1.
- [x] Um usuário com 3 empréstimos ativos é impedido de emprestar um quarto livro e é avisado do limite na tela.

### BIBL-3 — Ranking de livros mais emprestados

> Como **bibliotecário**, quero **ver quais livros são os mais emprestados**, para **entender a demanda do acervo**.

**Critérios de aceite**

- [x] A visão de ranking exibe os livros ordenados pela quantidade de empréstimos.
- [x] Cada item mostra o total de vezes que o livro foi emprestado.
- [x] Quando nenhum livro foi emprestado ainda, a tela exibe um estado vazio tratado, sem erro.

### BIBL-4 — Relatório de empréstimos

> Como **bibliotecário**, quero **um relatório de empréstimos com filtros**, para **analisar a movimentação do acervo sob diferentes recortes**.

**Critérios de aceite**

- [x] O relatório lista os empréstimos com o livro, o usuário, a data e a situação (ativo ou devolvido).
- [x] É possível filtrar os empréstimos por usuário.
- [x] É possível filtrar os empréstimos por período (data inicial e final).
- [x] É possível filtrar os empréstimos por situação (ativo ou devolvido).
- [x] Os filtros podem ser combinados e o relatório reflete todos os critérios aplicados ao mesmo tempo.
- [x] Quando nenhum empréstimo atende aos filtros, a tela exibe um estado vazio tratado, sem erro.

### BIBL-5 — Exportação do relatório de empréstimos

> Como **bibliotecário**, quero **exportar o relatório de empréstimos em um arquivo**, para **compartilhar ou arquivar essa informação fora do sistema**.

**Critérios de aceite**

- [x] É possível acionar, a partir do relatório, a exportação em formato CSV.
- [x] O arquivo exportado contém uma linha por empréstimo com o livro, o usuário, a data e a situação.
- [x] O arquivo inclui uma linha de cabeçalho identificando as colunas.
- [x] A exportação reflete o mesmo conjunto de empréstimos atualmente filtrado no relatório.
- [x] Exportar um relatório sem resultados gera um arquivo apenas com o cabeçalho, sem erro.

## Visão da solução

```
Navegador ──HTTPS──▶ Front-end (React) ──JSON / contrato OpenAPI──▶ API (FastAPI) ──▶ PostgreSQL
```

- **Contrato primeiro:** o `openapi-biblioteca.yaml` foi combinado antes do código; front, API e
  banco foram feitos em paralelo sobre ele.
- **API em camadas:** rotas → services (regras) → models (tabelas). As regras não dependem do
  framework nem do banco.
- **Consistência do estoque:** empréstimo e devolução em uma transação, com as linhas travadas
  (`FOR UPDATE`); o banco reforça com `CHECK` e trigger (limite de 3, cópias ≥ 0).
- **Visões como consultas:** ranking, relatório e CSV são calculados a partir dos empréstimos;
  o CSV usa a mesma consulta do relatório.
- **56 testes automatizados** na API cobrindo os critérios de aceite de todas as histórias.

Detalhes e trade-offs em [docs/ARQUITETURA.md](docs/ARQUITETURA.md).

## Como rodar localmente

Pré-requisitos: Python 3.12+, Node 20+ e, opcionalmente, Docker para o Postgres.

```bash
# 1. API (usa SQLite local por padrão, sem precisar de banco)
cd api
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
uvicorn app.main:app --reload        # http://localhost:8000/docs
pytest                               # 56 testes

# 2. Front (em outro terminal)
cd web
npm install
npm run dev                          # http://localhost:5173
```

Para usar o PostgreSQL com o schema do time, veja [database/README.md](database/README.md) e
configure `DATABASE_URL` e `CRIAR_TABELAS=false` no `api/.env`.
Publicação: [docs/DEPLOY.md](docs/DEPLOY.md).

## Estrutura do repositório

```
api/                     API FastAPI (rotas, services, models, schemas, testes)
web/                     Front-end React + Vite
database/                Script do banco PostgreSQL e testes das regras do banco
docs/                    Arquitetura, banco, API e deploy
openapi-biblioteca.yaml  Contrato da API (fonte da verdade entre front e back)
script-bd/               Versão anterior dos testes do banco (use database/testes.sql)
```

## Comportamentos a conhecer

- **Sem login.** As histórias não pedem autenticação: o leitor é escolhido numa lista e qualquer
  pessoa com o link usa o sistema.
- **Bibliotecário não pega livro.** Usuários com perfil `bibliotecario` não aparecem em
  `/leitores`; um empréstimo para eles responde 404 `Leitor não encontrado.`.
- **Datas no fuso do servidor (UTC).** Os filtros de período e a data do CSV usam o dia em UTC.
  Um empréstimo feito depois das 21h (horário de Brasília) conta como do dia seguinte.
- **Ranking só com livros emprestados.** Livro que nunca foi emprestado não aparece no ranking.
- **Ano no futuro** é validado pela API; o banco não tem essa regra.
- **Trigger do banco como rede de segurança.** A API confere o limite de 3 e o perfil antes de
  gravar; se mesmo assim o banco recusar, a resposta é um erro genérico, sem mensagem específica.
- **Banco local da API:** com `CRIAR_TABELAS=true` (SQLite) a API cria as tabelas e semeia os
  leitores Ana, Bruno e Carla; os dados de exemplo do PostgreSQL são outros (veja
  [database/README.md](database/README.md)).
- **Script do banco roda uma vez:** `database/banco_biblioteca.sql` não usa `IF NOT EXISTS`.
