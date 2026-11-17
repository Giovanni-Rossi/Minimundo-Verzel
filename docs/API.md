# API (referência rápida)

O contrato completo está em [`openapi-biblioteca.yaml`](../openapi-biblioteca.yaml). Com a API
rodando, a documentação interativa fica em `/docs` (Swagger), por exemplo
`http://localhost:8000/docs`.

## Convenções

- JSON em **camelCase** (`copiasDisponiveis`, `dataEmprestimo`).
- Datas em ISO 8601. Filtros `inicio` e `fim` em `AAAA-MM-DD`; `fim` é **inclusivo**.
- Todo erro tem o mesmo formato: `{"erro": "mensagem para mostrar na tela"}`.

| Status | Quando |
|---|---|
| `400` | dado inválido (validação) ou filtro inválido |
| `404` | livro, leitor ou empréstimo não encontrado |
| `409` | regra de negócio: sem cópia, limite de 3, já devolvido |
| `501` | rota ainda não implementada (não ocorre na versão atual) |

## Rotas

| História | Método e rota | Sucesso | Erros |
|---|---|---|---|
| BIBL-1 | `GET /livros` | `200` lista de `Livro` | — |
| BIBL-1 | `POST /livros` | `201` `Livro` | `400` |
| BIBL-2 | `POST /emprestimos` | `201` `Emprestimo` | `404`, `409` |
| BIBL-2 | `POST /emprestimos/{id}/devolucao` | `200` `Emprestimo` | `404`, `409` |
| BIBL-3 | `GET /livros/ranking` | `200` lista de `ItemRanking` | — |
| BIBL-4 | `GET /emprestimos?leitorId&inicio&fim&situacao` | `200` lista de `Emprestimo` | `400` |
| BIBL-5 | `GET /emprestimos/export.csv?` (mesmos filtros) | `200` `text/csv` | `400` (em JSON) |
| apoio | `GET /leitores` | `200` lista de `Leitor` | — |

## Mensagens de erro

| Rota | Mensagem |
|---|---|
| `POST /livros` | `Título é obrigatório.` · `Ano não pode ser no futuro.` · `Cópias não podem ser negativas.` |
| `POST /emprestimos` | `Livro não encontrado.` · `Leitor não encontrado.` · `Livro sem cópias disponíveis.` · `Leitor já tem 3 empréstimos ativos.` |
| `POST /emprestimos/{id}/devolucao` | `Empréstimo não encontrado.` · `Empréstimo já devolvido.` |
| `GET /emprestimos` e CSV | `Data inicial não pode ser depois da data final.` |
| Qualquer rota (JSON ou parâmetro mal formado) | `Campo inválido: <campo>.` |

## Formatos

```jsonc
// Livro
{ "id": 1, "titulo": "Dom Casmurro", "autor": "Machado de Assis", "ano": 1899, "copiasDisponiveis": 3 }

// Leitor
{ "id": 2, "nome": "Bruno Leitor" }

// Emprestimo
{
  "id": 10,
  "livro":  { "id": 1, "titulo": "Dom Casmurro" },
  "leitor": { "id": 2, "nome": "Bruno Leitor" },
  "dataEmprestimo": "2026-11-16T19:30:00Z",
  "dataDevolucao": null,
  "situacao": "ativo"            // ou "devolvido"
}

// ItemRanking
{ "livroId": 1, "titulo": "Dom Casmurro", "totalEmprestimos": 5 }
```

## Comportamento de cada visão

- **Ranking (BIBL-3):** conta empréstimos ativos e devolvidos, do maior total para o menor; empate
  ordenado pelo título; livro nunca emprestado não aparece; sem empréstimos devolve `[]`.
- **Relatório (BIBL-4):** filtros opcionais e combinados; do empréstimo mais recente para o mais
  antigo; a situação é decidida por `dataDevolucao` (vazia = ativo); sem resultado devolve `[]`.
- **CSV (BIBL-5):** mesma consulta do relatório. Cabeçalho `livro,leitor,data,situacao`, UTF-8 com
  BOM (o Excel abre os acentos), vírgulas e aspas escapadas; sem resultado, só o cabeçalho.

## Exemplos

```bash
API=http://localhost:8000

curl $API/livros
curl -X POST $API/livros -H 'Content-Type: application/json' \
  -d '{"titulo":"Iracema","autor":"José de Alencar","ano":1865,"copiasDisponiveis":2}'

curl -X POST $API/emprestimos -H 'Content-Type: application/json' -d '{"livroId":1,"leitorId":2}'
curl -X POST $API/emprestimos/1/devolucao

curl $API/livros/ranking
curl "$API/emprestimos?leitorId=2&inicio=2026-11-01&fim=2026-11-30&situacao=ativo"
curl -o emprestimos.csv "$API/emprestimos/export.csv?situacao=devolvido"
```
