// BIBL-2 (parte de devolver): lista os empréstimos ativos e permite devolver.
import { useEffect, useState } from 'react'
import { devolver, listarEmprestimos } from '../api.js'

// "2026-11-16T19:30:00Z" -> "16/11/2026"
function formatarData(dataIso) {
  return new Date(dataIso).toLocaleDateString('pt-BR')
}

export default function Emprestimos() {
  const [emprestimos, setEmprestimos] = useState([])
  const [carregando, setCarregando] = useState(true)
  const [erroLista, setErroLista] = useState('')
  const [erroDevolucao, setErroDevolucao] = useState('')
  const [mensagem, setMensagem] = useState('')
  const [devolvendoId, setDevolvendoId] = useState(null)

  // Busca só os empréstimos ativos (usada ao abrir a tela e depois de cada devolução).
  async function carregarAtivos() {
    try {
      setEmprestimos(await listarEmprestimos({ situacao: 'ativo' }))
      setErroLista('')
    } catch (e) {
      setErroLista(e.message)
    }
  }

  // Ao abrir a tela: busca os empréstimos ativos.
  useEffect(() => {
    async function carregarTudo() {
      await carregarAtivos()
      setCarregando(false)
    }
    carregarTudo()
  }, [])

  async function aoDevolver(emprestimo) {
    setMensagem('')
    setDevolvendoId(emprestimo.id)
    try {
      await devolver(emprestimo.id)
      setMensagem(`"${emprestimo.livro.titulo}" devolvido por ${emprestimo.leitor.nome}.`)
      setErroDevolucao('')
    } catch (e) {
      // Ex.: "Empréstimo já devolvido."
      setErroDevolucao(e.message)
    }
    await carregarAtivos() // o empréstimo devolvido sai da lista
    setDevolvendoId(null)
  }

  return (
    <section>
      <h2>Empréstimos ativos</h2>

      {erroDevolucao && (
        <p className="aviso" role="alert">
          {erroDevolucao}
        </p>
      )}
      {mensagem && <p className="sucesso">{mensagem}</p>}

      {carregando && <p className="vazio">Carregando...</p>}
      {erroLista && (
        <p className="erro" role="alert">
          {erroLista}
        </p>
      )}
      {!carregando && !erroLista && emprestimos.length === 0 && (
        <p className="vazio">Nenhum livro emprestado no momento.</p>
      )}

      {emprestimos.length > 0 && (
        <table>
          <thead>
            <tr>
              <th>Livro</th>
              <th>Leitor</th>
              <th>Emprestado em</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {emprestimos.map((emprestimo) => (
              <tr key={emprestimo.id}>
                <td>{emprestimo.livro.titulo}</td>
                <td>{emprestimo.leitor.nome}</td>
                <td>{formatarData(emprestimo.dataEmprestimo)}</td>
                <td>
                  <button
                    className="secundario"
                    onClick={() => aoDevolver(emprestimo)}
                    disabled={devolvendoId === emprestimo.id}
                  >
                    {devolvendoId === emprestimo.id ? 'Devolvendo...' : 'Devolver'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  )
}
