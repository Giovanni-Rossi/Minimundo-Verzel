# Front-end · Biblioteca Comunitária

Interface da bibliotecária, feita em **React 19 + Vite**, com `react-router-dom` para as telas,
`react-hook-form` + `zod` no formulário de cadastro e ícones do `lucide-react`.
Conversa com a API seguindo o contrato [`openapi-biblioteca.yaml`](../openapi-biblioteca.yaml).

## Como rodar

```bash
cd web
npm install
npm run dev          # http://localhost:5173
```

Por padrão a tela procura a API em `http://localhost:8000`. Para mudar, copie `.env.example`
para `.env` (ou `.env.local`) e ajuste:

| Variável | Padrão | Para que serve |
|---|---|---|
| `VITE_API_URL` | `http://localhost:8000` | Endereço da API |
| `VITE_MOCK` | `false` | `true` usa os dados fixos de `src/mock.js` em vez da API |

> O Vite grava essas variáveis **no build**. Em produção, mudar o endereço da API exige rodar o
> build de novo.

### Scripts

| Comando | O que faz |
|---|---|
| `npm run dev` | Servidor de desenvolvimento com recarga automática |
| `npm run build` | Gera os arquivos de produção em `dist/` |
| `npm run preview` | Serve o `dist/` localmente para conferir o build |
| `npm run lint` | Verifica o código com o oxlint |

### Rodar sem o back-end

Crie `web/.env.local` com `VITE_MOCK=true` e rode `npm run dev`. O `api.js` passa a responder com
os dados de `src/mock.js`, com as mesmas regras e mensagens do contrato (inclusive o CSV). Os
dados ficam em memória: recarregar a página volta ao estado inicial.

## Telas

| Rota | Tela | História |
|---|---|---|
| `/acervo` | Cadastro e lista de livros (tela inicial) | BIBL-1 |
| `/emprestimos` | Emprestar e devolver | BIBL-2 |
| `/ranking` | Livros mais emprestados | BIBL-3 |
| `/relatorio` | Relatório com filtros e botão de exportar CSV | BIBL-4 e BIBL-5 |
| `/leitores` | Histórico de cada leitor | Regra 4 do minimundo |

Toda tela trata três estados: **carregando**, **vazio** e **erro** (com a mensagem da API).

## Onde fica cada coisa

| Arquivo | O que é |
|---|---|
| `src/main.jsx` | Liga o React e o `BrowserRouter` |
| `src/App.jsx` | Menu lateral, rotas das telas e botão de tema |
| `src/api.js` | **Único** arquivo que conversa com a API, uma função por rota do contrato |
| `src/mock.js` | Dados fixos que imitam a API (`VITE_MOCK=true`) |
| `src/schemas/livro.js` | Regras do formulário de livro (zod), com as mesmas mensagens da API |
| `src/formatar.js` | Formatação de datas e da situação para exibir |
| `src/tema.js` | Tema claro/escuro, salvo no navegador e com a preferência do sistema na primeira visita |
| `src/index.css` | Estilos compartilhados (tabela, formulário, botões, erro, temas) |
| `src/pages/*.jsx` | Uma tela por arquivo, para duas pessoas trabalharem sem conflito |

## Como as telas falam com a API

As telas nunca usam `fetch` direto: chamam as funções de `src/api.js`
(`listarLivros`, `cadastrarLivro`, `listarLeitores`, `emprestar`, `devolver`, `listarRanking`,
`listarEmprestimos`, `urlCsv`). Quando a API recusa um pedido, a função lança um `Error` com a
mensagem que veio em `{"erro": "..."}`, e a tela mostra:

```jsx
try {
  await emprestar(livroId, leitorId)
} catch (e) {
  setErro(e.message)   // ex.: "Leitor já tem 3 empréstimos ativos."
}
```

O formulário de livro valida antes de enviar (zod) com as mesmas mensagens da API, então o
usuário vê o mesmo texto venha o erro do navegador ou do servidor.

O link de exportação (`urlCsv(filtros)`) usa os mesmos filtros da tela do relatório, então o
arquivo traz exatamente o que está sendo exibido.

## Deploy

O `npm run build` gera arquivos estáticos em `dist/`. Qualquer servidor estático serve, desde que
as rotas do React Router voltem para o `index.html` (ex.: `try_files $uri /index.html` no nginx).
Configuração usada em produção: [docs/DEPLOY.md](../docs/DEPLOY.md).
