// Histórico de cada leitor (regras 3 e 4 do README):
// empréstimos ativos (máximo 3) e livros já devolvidos.
import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { listarEmprestimos, listarLeitores } from '../api.js'
import { formatarData } from '../formatar.js'

const LIMITE_ATIVOS = 3

export default function Leitores() {
  // O leitor escolhido fica na URL (/leitores?id=2), assim o Relatório pode linkar direto.
  const [parametros, setParametros] = useSearchParams()
  const leitorId = parametros.get('id') || ''

  const [leitores, setLeitores] = useState([])
  const [erroLeitores, setErroLeitores] = useState('')
  // Empréstimos do último leitor buscado, guardados junto com o id dele.
  const [resposta, setResposta] = useState(null)

  useEffect(() => {
    listarLeitores()
      .then(setLeitores)
      .catch((e) => setErroLeitores(e.message))
  }, [])

  useEffect(() => {
    if (!leitorId) return
    // Se trocar de leitor antes da resposta chegar, ignora a resposta antiga.
    let atual = true
    listarEmprestimos({ leitorId })
      .then((dados) => atual && setResposta({ leitorId, emprestimos: dados, erro: '' }))
      .catch((e) => atual && setResposta({ leitorId, emprestimos: [], erro: e.message }))
    return () => {
      atual = false
    }
  }, [leitorId])

  const carregando = resposta?.leitorId !== leitorId
  const emprestimos = carregando ? [] : resposta.emprestimos
  const erro = carregando ? '' : resposta.erro

  function escolherLeitor(evento) {
    const id = evento.target.value
    setParametros(id ? { id } : {})
  }

  // Mais recentes primeiro
  const ordenados = [...emprestimos].sort((a, b) => b.dataEmprestimo.localeCompare(a.dataEmprestimo))
  const ativos = ordenados.filter((e) => e.situacao === 'ativo')
  const devolvidos = ordenados.filter((e) => e.situacao === 'devolvido')
  const leitor = leitores.find((l) => String(l.id) === leitorId)

  return (
    <section>
      <h2>Leitores</h2>

      <div className="formulario">
        <label>
          Leitor
          <select value={leitorId} onChange={escolherLeitor}>
            <option value="">Escolha um leitor</option>
            {leitores.map((l) => (
              <option key={l.id} value={l.id}>
                {l.nome}
              </option>
            ))}
          </select>
        </label>
      </div>

      {erroLeitores && <p className="erro">{erroLeitores}</p>}
      {erro && <p className="erro">{erro}</p>}

      {!leitorId ? (
        <p className="vazio">Escolha um leitor para ver os empréstimos e o histórico dele.</p>
      ) : carregando ? (
        <p className="vazio">Carregando…</p>
      ) : erro ? null : (
        <>
          <h3>
            Com o leitor agora
            <span className="resumo">
              {' '}
              {ativos.length} de {LIMITE_ATIVOS}
            </span>
          </h3>
          {ativos.length >= LIMITE_ATIVOS && (
            <p className="aviso">
              {leitor?.nome ?? 'Este leitor'} atingiu o limite de {LIMITE_ATIVOS} empréstimos e precisa devolver um livro
              antes de pegar outro.
            </p>
          )}
          {ativos.length === 0 ? (
            <p className="vazio">Nenhum livro emprestado no momento.</p>
          ) : (
            <TabelaEmprestimos emprestimos={ativos} />
          )}

          <h3>Histórico de devoluções</h3>
          {devolvidos.length === 0 ? (
            <p className="vazio">Nenhum livro devolvido ainda.</p>
          ) : (
            <TabelaEmprestimos emprestimos={devolvidos} comDevolucao />
          )}
        </>
      )}
    </section>
  )
}

function TabelaEmprestimos({ emprestimos, comDevolucao = false }) {
  return (
    <table>
      <thead>
        <tr>
          <th>Livro</th>
          <th>Emprestado em</th>
          {comDevolucao && <th>Devolvido em</th>}
        </tr>
      </thead>
      <tbody>
        {emprestimos.map((emprestimo) => (
          <tr key={emprestimo.id}>
            <td>{emprestimo.livro.titulo}</td>
            <td>{formatarData(emprestimo.dataEmprestimo)}</td>
            {comDevolucao && <td>{formatarData(emprestimo.dataDevolucao)}</td>}
          </tr>
        ))}
      </tbody>
    </table>
  )
}
