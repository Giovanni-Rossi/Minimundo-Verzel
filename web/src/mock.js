// Dados fixos para usar o front sem o back-end (VITE_MOCK=true no web/.env.local).
// Imita a API do contrato openapi-biblioteca.yaml, com as mesmas regras e mensagens de erro.
// Tudo fica em memória: recarregar a página volta aos dados iniciais.

const leitores = [
  { id: 1, nome: 'Ana' },
  { id: 2, nome: 'Bruno' },
  { id: 3, nome: 'Carla' },
  { id: 4, nome: 'Diego' },
  { id: 5, nome: 'Elisa' },
]

const livros = [
  { id: 1, titulo: 'Dom Casmurro', autor: 'Machado de Assis', ano: 1899, copiasDisponiveis: 2 },
  { id: 2, titulo: 'O Cortiço', autor: 'Aluísio Azevedo', ano: 1890, copiasDisponiveis: 1 },
  { id: 3, titulo: 'Memórias Póstumas de Brás Cubas', autor: 'Machado de Assis', ano: 1881, copiasDisponiveis: 3 },
  { id: 4, titulo: 'Capitães da Areia', autor: 'Jorge Amado', ano: 1937, copiasDisponiveis: 0 },
  { id: 5, titulo: 'A Hora da Estrela', autor: 'Clarice Lispector', ano: 1977, copiasDisponiveis: 2 },
  { id: 6, titulo: 'Vidas Secas', autor: 'Graciliano Ramos', ano: 1938, copiasDisponiveis: 1 },
  { id: 7, titulo: 'Grande Sertão: Veredas', autor: 'João Guimarães Rosa', ano: 1956, copiasDisponiveis: 2 },
]

// [livroId, leitorId, data do empréstimo, data da devolução | null]
// Carla (3) está no limite de 3 ativos; Elisa (5) nunca pegou nada.
const emprestimosIniciais = [
  [1, 1, '2026-09-28', '2026-10-10'],
  [4, 2, '2026-10-02', '2026-10-20'],
  [1, 2, '2026-10-05', '2026-10-19'],
  [6, 4, '2026-10-12', '2026-10-30'],
  [2, 1, '2026-10-15', '2026-11-01'],
  [1, 4, '2026-10-21', '2026-11-04'],
  [4, 1, '2026-10-25', '2026-11-08'],
  [3, 2, '2026-11-02', null],
  [4, 3, '2026-11-03', null],
  [1, 3, '2026-11-06', null],
  [5, 3, '2026-11-09', null],
  [7, 1, '2026-11-12', null],
  [4, 4, '2026-11-14', null],
]

const emprestimos = emprestimosIniciais.map(([livroId, leitorId, inicio, fim], i) => ({
  id: i + 1,
  livroId,
  leitorId,
  dataEmprestimo: `${inicio}T12:00:00Z`,
  dataDevolucao: fim ? `${fim}T12:00:00Z` : null,
}))

// Muda a cada cadastro/empréstimo/devolução, para o CSV não ficar desatualizado.
let versao = 0

const proximoId = (lista) => Math.max(0, ...lista.map((item) => item.id)) + 1
const situacaoDe = (e) => (e.dataDevolucao ? 'devolvido' : 'ativo')

// Formato do contrato: { id, livro: { id, titulo }, leitor: { id, nome }, ... }
function expandir(e) {
  const livro = livros.find((l) => l.id === e.livroId)
  const leitor = leitores.find((l) => l.id === e.leitorId)
  return {
    id: e.id,
    livro: { id: livro.id, titulo: livro.titulo },
    leitor: { ...leitor },
    dataEmprestimo: e.dataEmprestimo,
    dataDevolucao: e.dataDevolucao,
    situacao: situacaoDe(e),
  }
}

const DATA = /^\d{4}-\d{2}-\d{2}$/

// Mesmos filtros do GET /emprestimos e do CSV.
function filtrar(params) {
  const leitorId = params.get('leitorId')
  const inicio = params.get('inicio')
  const fim = params.get('fim')
  const situacao = params.get('situacao')

  if (leitorId && !/^[1-9]\d*$/.test(leitorId)) throw new Error('Leitor inválido.')
  if (inicio && !DATA.test(inicio)) throw new Error('Data inicial inválida. Use AAAA-MM-DD.')
  if (fim && !DATA.test(fim)) throw new Error('Data final inválida. Use AAAA-MM-DD.')
  if (inicio && fim && inicio > fim) throw new Error('Data inicial não pode ser depois da final.')
  if (situacao && !['ativo', 'devolvido'].includes(situacao)) throw new Error('Situação inválida.')

  return emprestimos
    .filter((e) => !leitorId || e.leitorId === Number(leitorId))
    .filter((e) => !inicio || e.dataEmprestimo.slice(0, 10) >= inicio)
    .filter((e) => !fim || e.dataEmprestimo.slice(0, 10) <= fim)
    .filter((e) => !situacao || situacaoDe(e) === situacao)
    .sort((a, b) => b.dataEmprestimo.localeCompare(a.dataEmprestimo))
    .map(expandir)
}

function rotear(metodo, caminho, corpo) {
  const url = new URL(caminho, 'http://mock')
  const rota = `${metodo} ${url.pathname}`

  if (rota === 'GET /livros') return livros.map((l) => ({ ...l }))

  if (rota === 'POST /livros') {
    const { titulo, autor, ano, copiasDisponiveis } = corpo
    if (!titulo || !String(titulo).trim()) throw new Error('Título é obrigatório.')
    if (!Number.isInteger(ano)) throw new Error('Ano inválido.')
    if (ano > new Date().getFullYear()) throw new Error('Ano não pode ser no futuro.')
    if (!Number.isInteger(copiasDisponiveis)) throw new Error('Cópias inválidas.')
    if (copiasDisponiveis < 0) throw new Error('Cópias não podem ser negativas.')
    const livro = { id: proximoId(livros), titulo: String(titulo).trim(), autor: String(autor ?? ''), ano, copiasDisponiveis }
    livros.push(livro)
    return { ...livro }
  }

  if (rota === 'GET /livros/ranking') {
    const totais = new Map()
    for (const e of emprestimos) totais.set(e.livroId, (totais.get(e.livroId) ?? 0) + 1)
    return [...totais]
      .map(([livroId, totalEmprestimos]) => ({
        livroId,
        titulo: livros.find((l) => l.id === livroId).titulo,
        totalEmprestimos,
      }))
      .sort((a, b) => b.totalEmprestimos - a.totalEmprestimos || a.titulo.localeCompare(b.titulo))
  }

  if (rota === 'GET /leitores') return leitores.map((l) => ({ ...l }))

  if (rota === 'GET /emprestimos') return filtrar(url.searchParams)

  if (rota === 'POST /emprestimos') {
    const { livroId, leitorId } = corpo
    const livro = livros.find((l) => l.id === livroId)
    if (!livro) throw new Error('Livro não encontrado.')
    if (!leitores.some((l) => l.id === leitorId)) throw new Error('Leitor não encontrado.')
    if (livro.copiasDisponiveis <= 0) throw new Error('Livro sem cópias disponíveis.')
    const ativos = emprestimos.filter((e) => e.leitorId === leitorId && !e.dataDevolucao).length
    if (ativos >= 3) throw new Error('Leitor já tem 3 empréstimos ativos.')
    livro.copiasDisponiveis -= 1
    const novo = { id: proximoId(emprestimos), livroId, leitorId, dataEmprestimo: new Date().toISOString(), dataDevolucao: null }
    emprestimos.push(novo)
    return expandir(novo)
  }

  const devolucao = url.pathname.match(/^\/emprestimos\/(\d+)\/devolucao$/)
  if (metodo === 'POST' && devolucao) {
    const emprestimo = emprestimos.find((e) => e.id === Number(devolucao[1]))
    if (!emprestimo) throw new Error('Empréstimo não encontrado.')
    if (emprestimo.dataDevolucao) throw new Error('Empréstimo já devolvido.')
    emprestimo.dataDevolucao = new Date().toISOString()
    livros.find((l) => l.id === emprestimo.livroId).copiasDisponiveis += 1
    return expandir(emprestimo)
  }

  throw new Error('Rota não encontrada.')
}

// Usado pelo chamar() do api.js no lugar do fetch. Devolve os dados ou lança Error com a mensagem.
export async function responder(caminho, opcoes = {}) {
  // Pequeno atraso para parecer uma API de verdade (e dar para ver o "Carregando…")
  await new Promise((resolver) => setTimeout(resolver, 250))
  const corpo = opcoes.body ? JSON.parse(opcoes.body) : {}
  const metodo = opcoes.method || 'GET'
  const dados = rotear(metodo, caminho, corpo)
  if (metodo !== 'GET') versao++
  return dados
}

function campoCsv(valor) {
  const texto = String(valor)
  return /[",\n]/.test(texto) ? `"${texto.replaceAll('"', '""')}"` : texto
}

// BIBL-5 sem servidor: monta o CSV aqui e devolve um link blob: para download.
// filtros chega no formato de query string ("?leitorId=1&situacao=ativo").
let linkAnterior = { chave: null, url: null }
export function urlCsv(filtros) {
  const chave = `${versao}${filtros}`
  if (linkAnterior.chave === chave) return linkAnterior.url
  let linhas = []
  try {
    linhas = filtrar(new URLSearchParams(filtros)).map((e) =>
      [e.livro.titulo, e.leitor.nome, e.dataEmprestimo.slice(0, 10), e.situacao].map(campoCsv).join(','),
    )
  } catch {
    // Filtro inválido: a tela já desabilita o botão nesse caso
  }
  const csv = '﻿' + ['livro,leitor,data,situacao', ...linhas].join('\r\n') + '\r\n'
  if (linkAnterior.url) URL.revokeObjectURL(linkAnterior.url)
  linkAnterior = { chave, url: URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' })) }
  return linkAnterior.url
}
