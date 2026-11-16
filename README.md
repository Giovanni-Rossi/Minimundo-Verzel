# Minimundo-Verzel

Sistema de controle de acervo para a **Biblioteca Comunitária** do bairro.

## Sumário

- [O minimundo](#o-minimundo)
- [Regras de funcionamento da biblioteca](#regras-de-funcionamento-da-biblioteca)
- [Histórias](#histórias)
  - [BIBL-1 — Cadastro e listagem de livros](#bibl-1--cadastro-e-listagem-de-livros)
  - [BIBL-2 — Empréstimo e devolução de livros](#bibl-2--empréstimo-e-devolução-de-livros)
  - [BIBL-3 — Ranking de livros mais emprestados](#bibl-3--ranking-de-livros-mais-emprestados)
  - [BIBL-4 — Relatório de empréstimos](#bibl-4--relatório-de-empréstimos)
  - [BIBL-5 — Exportação do relatório de empréstimos](#bibl-5--exportação-do-relatório-de-empréstimos)

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

- [ ] É possível cadastrar um livro com título, autor, ano e quantidade de cópias.
- [ ] Após o cadastro, o livro aparece na listagem sem recarregar a página manualmente.
- [ ] A tela principal exibe a lista de livros com seus dados.
- [ ] Cadastro com título vazio é recusado e a mensagem de erro é exibida na tela.
- [ ] Cadastro com ano no futuro é recusado e a mensagem de erro é exibida na tela.
- [ ] Cadastro com quantidade de cópias negativa é recusado e a mensagem de erro é exibida na tela.

### BIBL-2 — Empréstimo e devolução de livros

> Como **usuário da biblioteca**, quero **pegar livros emprestados e devolvê-los**, para **consumir o acervo respeitando a disponibilidade de cópias**.

Ao emprestar, a quantidade de cópias disponíveis do livro diminui em 1. Ao devolver, aumenta em 1. Um usuário não pode manter mais de 3 empréstimos ativos ao mesmo tempo.

**Critérios de aceite**

- [ ] Emprestar um livro com cópia disponível registra o empréstimo e diminui as cópias em 1.
- [ ] A tela reflete a nova quantidade de cópias após o empréstimo.
- [ ] Emprestar um livro com 0 cópias disponíveis é recusado e o usuário é avisado na tela.
- [ ] Devolver um livro emprestado encerra o empréstimo e aumenta as cópias em 1.
- [ ] Um usuário com 3 empréstimos ativos é impedido de emprestar um quarto livro e é avisado do limite na tela.

### BIBL-3 — Ranking de livros mais emprestados

> Como **bibliotecário**, quero **ver quais livros são os mais emprestados**, para **entender a demanda do acervo**.

**Critérios de aceite**

- [ ] A visão de ranking exibe os livros ordenados pela quantidade de empréstimos.
- [ ] Cada item mostra o total de vezes que o livro foi emprestado.
- [ ] Quando nenhum livro foi emprestado ainda, a tela exibe um estado vazio tratado, sem erro.

### BIBL-4 — Relatório de empréstimos

> Como **bibliotecário**, quero **um relatório de empréstimos com filtros**, para **analisar a movimentação do acervo sob diferentes recortes**.

**Critérios de aceite**

- [ ] O relatório lista os empréstimos com o livro, o usuário, a data e a situação (ativo ou devolvido).
- [ ] É possível filtrar os empréstimos por usuário.
- [ ] É possível filtrar os empréstimos por período (data inicial e final).
- [ ] É possível filtrar os empréstimos por situação (ativo ou devolvido).
- [ ] Os filtros podem ser combinados e o relatório reflete todos os critérios aplicados ao mesmo tempo.
- [ ] Quando nenhum empréstimo atende aos filtros, a tela exibe um estado vazio tratado, sem erro.

### BIBL-5 — Exportação do relatório de empréstimos

> Como **bibliotecário**, quero **exportar o relatório de empréstimos em um arquivo**, para **compartilhar ou arquivar essa informação fora do sistema**.

**Critérios de aceite**

- [ ] É possível acionar, a partir do relatório, a exportação em formato CSV.
- [ ] O arquivo exportado contém uma linha por empréstimo com o livro, o usuário, a data e a situação.
- [ ] O arquivo inclui uma linha de cabeçalho identificando as colunas.
- [ ] A exportação reflete o mesmo conjunto de empréstimos atualmente filtrado no relatório.
- [ ] Exportar um relatório sem resultados gera um arquivo apenas com o cabeçalho, sem erro.

## Front-end (`web/`)

Feito em React + Vite, com `react-router-dom` para a navegação entre as telas.

**Como rodar**

```bash
cd web
npm install
npm run dev
```

A aplicação abre em `http://localhost:5173`. Por padrão ela procura a API em `http://localhost:3000`; para mudar, copie `web/.env.example` para `web/.env` e ajuste `VITE_API_URL`.

**Onde fica cada coisa**

| Arquivo                     | O que é                                                        |
| --------------------------- | -------------------------------------------------------------- |
| `src/App.jsx`               | Menu lateral e rotas das telas                                 |
| `src/api.js`                | Único arquivo que conversa com a API (uma função por rota)     |
| `src/index.css`             | Estilos compartilhados (tabela, formulário, botões, erro)      |
| `src/pages/Acervo.jsx`      | BIBL-1                                                         |
| `src/pages/Emprestimos.jsx` | BIBL-2                                                         |
| `src/pages/Ranking.jsx`     | BIBL-3                                                         |
| `src/pages/Relatorio.jsx`   | BIBL-4 e BIBL-5                                                |

Cada tela mora no seu próprio arquivo, para duas pessoas trabalharem sem conflito. As telas não usam `fetch` direto: chamam as funções de `api.js`, que lançam um erro com a mensagem da API quando ela recusa o pedido.
