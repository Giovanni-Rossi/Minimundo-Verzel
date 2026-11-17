# Banco de dados

Scripts do PostgreSQL da Biblioteca Comunitária. O schema explicado (tabelas, regras, trigger,
view e diagrama) está em [docs/BANCO.md](../docs/BANCO.md).

## Arquivos

| Arquivo | O que faz |
|---|---|
| `banco_biblioteca.sql` | Cria tudo: tipos, tabelas, índices, view `relatorio_emprestimos`, dados de exemplo e o trigger `regras_emprestimo` |
| `testes.sql` | Testa as regras do banco dentro de uma transação desfeita no final (não altera os dados) |

> `script-bd/testes.sql` é uma versão anterior dos testes e não bate com os dados do schema atual
> (usa outros e-mails e títulos). Use `database/testes.sql`.

## Como aplicar

O script cria os objetos sem `IF NOT EXISTS`: rode **uma vez**, num banco vazio.

**Neon / qualquer Postgres gerenciado:** cole `banco_biblioteca.sql` inteiro no SQL Editor e execute.

**psql:**
```bash
psql "$DATABASE_URL" -f database/banco_biblioteca.sql
```

**Docker (Postgres local):**
```bash
docker run -d --name biblioteca-db -p 5432:5432 \
  -e POSTGRES_DB=biblioteca -e POSTGRES_USER=biblioteca -e POSTGRES_PASSWORD=<senha> \
  -v "$PWD/database/banco_biblioteca.sql:/docker-entrypoint-initdb.d/01-banco.sql:ro" \
  postgres:16-alpine
```
O script roda sozinho na primeira subida (volume vazio).

Depois, na API (`api/.env`):
```
DATABASE_URL=postgresql://biblioteca:<senha>@localhost:5432/biblioteca
CRIAR_TABELAS=false
```

## Testar as regras

```bash
psql "$DATABASE_URL" -f database/testes.sql
```
Cada caso mostra o resultado esperado, o obtido e `OK` ou `FALHOU`. O bloco roda dentro de
`BEGIN ... ROLLBACK`, então os dados de exemplo continuam iguais.

## Dados de exemplo

| Quem | Para testar |
|---|---|
| Ana Bibliotecária (`bibliotecario`) | bibliotecário não pode pegar livro |
| Bruno Leitor | histórico com empréstimo devolvido |
| Carla Leitora (3 ativos) | limite de 3 empréstimos |
| Capitães da Areia (0 cópias) | empréstimo sem cópia disponível |

## Mudou o schema?

Os nomes do banco só aparecem em `api/app/models/`. Se uma tabela ou coluna mudar, ajuste o model
correspondente; rotas, schemas e contrato continuam iguais. Atualize também [docs/BANCO.md](../docs/BANCO.md).
