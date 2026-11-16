// Único arquivo que conversa com a API.
// Segue o contrato em openapi-biblioteca.yaml (na raiz do repositório).
// As telas chamam as funções daqui e nunca usam fetch direto.

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Faz a chamada e devolve o JSON da resposta.
// Se a API recusar, lança um Error com a mensagem que ela mandou,
// para a tela mostrar: catch (e) { setErro(e.message) }
async function chamar(caminho, opcoes = {}) {
  let resposta
  try {
    resposta = await fetch(API_URL + caminho, {
      ...opcoes,
      headers: { 'Content-Type': 'application/json', ...opcoes.headers },
    })
  } catch {
    throw new Error('Não foi possível conectar com a API.')
  }

  if (resposta.status === 204) return null

  const dados = await resposta.json().catch(() => null)
  if (!resposta.ok) {
    throw new Error(dados?.erro || 'Algo deu errado. Tente de novo.')
  }
  return dados
}

// Transforma { leitorId: 1, situacao: '' } em "?leitorId=1" (ignora filtros vazios).
function montarFiltros(filtros = {}) {
  const params = new URLSearchParams()
  for (const [chave, valor] of Object.entries(filtros)) {
    if (valor) params.set(chave, valor)
  }
  const texto = params.toString()
  return texto ? `?${texto}` : ''
}

// BIBL-1
// Livro: { id, titulo, autor, ano, copiasDisponiveis }
export function listarLivros() {
  return chamar('/livros')
}

export function cadastrarLivro(livro) {
  return chamar('/livros', { method: 'POST', body: JSON.stringify(livro) })
}

// Leitores já vêm cadastrados no banco: [{ id, nome }]
export function listarLeitores() {
  return chamar('/leitores')
}

// BIBL-2
// Empréstimo: { id, livro: { id, titulo }, leitor: { id, nome },
//               dataEmprestimo, dataDevolucao, situacao: 'ativo' | 'devolvido' }
export function emprestar(livroId, leitorId) {
  return chamar('/emprestimos', {
    method: 'POST',
    body: JSON.stringify({ livroId, leitorId }),
  })
}

export function devolver(emprestimoId) {
  return chamar(`/emprestimos/${emprestimoId}/devolucao`, { method: 'POST' })
}

// BIBL-3 — [{ livroId, titulo, totalEmprestimos }]
export function listarRanking() {
  return chamar('/livros/ranking')
}

// BIBL-4 — filtros: { leitorId, inicio, fim, situacao } (datas em AAAA-MM-DD)
export function listarEmprestimos(filtros) {
  return chamar('/emprestimos' + montarFiltros(filtros))
}

// BIBL-5 — link do CSV com os mesmos filtros do relatório
export function urlCsv(filtros) {
  return API_URL + '/emprestimos/export.csv' + montarFiltros(filtros)
}
