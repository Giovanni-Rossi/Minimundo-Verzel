// BIBL-2 (parte de devolver): lista os empréstimos ativos e permite devolver.
import { useEffect, useState } from 'react'
import { devolver, listarEmprestimos } from '../api.js'
import { formatarData } from '../formatar.js'

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
      {!carregando && !erroLista && emprestimos.length > 0 && (
        <p className="frase">
          <span className="chip">
            {emprestimos.length} {emprestimos.length === 1 ? 'livro está' : 'livros estão'}
          </span>{' '}
          com leitores agora.
        </p>
      )}

      {/* Linha reservada para as mensagens: a lista não pula quando elas aparecem. */}
      <div className="mensagens">
        {erroDevolucao && (
          <p className="aviso" role="alert">
            {erroDevolucao}
          </p>
        )}
        {mensagem && <p className="sucesso">{mensagem}</p>}
      </div>

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
        <ul className="lista">
          {emprestimos.map((emprestimo) => (
            <li key={emprestimo.id}>
              <div className="principal">
                <span className="titulo">{emprestimo.livro.titulo}</span>
                <span className="detalhe">
                  {emprestimo.leitor.nome} · desde{' '}
                  <span className="mono">{formatarData(emprestimo.dataEmprestimo)}</span>
                </span>
              </div>
              <div className="acao">
                <button
                  className="secundario pequeno"
                  onClick={() => aoDevolver(emprestimo)}
                  disabled={devolvendoId === emprestimo.id}
                >
                  {devolvendoId === emprestimo.id ? 'Devolvendo...' : 'Devolver'}
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
