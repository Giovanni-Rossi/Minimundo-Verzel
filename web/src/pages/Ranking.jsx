// BIBL-3: livros mais emprestados.
import { useEffect, useState } from 'react'
import { listarRanking } from '../api.js'

export default function Ranking() {
  // A API já manda a lista ordenada, do mais emprestado para o menos.
  const [ranking, setRanking] = useState([])
  const [carregando, setCarregando] = useState(true)
  const [erro, setErro] = useState('')

  // Ao abrir a tela: busca o ranking.
  useEffect(() => {
    async function carregar() {
      try {
        setRanking(await listarRanking())
      } catch (e) {
        setErro(e.message)
      }
      setCarregando(false)
    }
    carregar()
  }, [])

  // O primeiro colocado tem a barra cheia; os outros, proporcional a ele.
  const maiorTotal = ranking.length > 0 ? ranking[0].totalEmprestimos : 0

  return (
    <section>
      <h2>Mais emprestados</h2>
      {ranking.length > 0 && (
        <p className="frase">
          <span className="chip">{ranking[0].titulo}</span> é o mais procurado, com{' '}
          <span className="chip">
            {maiorTotal} {maiorTotal === 1 ? 'empréstimo' : 'empréstimos'}
          </span>
          .
        </p>
      )}

      {carregando && <p className="vazio">Carregando...</p>}
      {erro && (
        <p className="erro" role="alert">
          {erro}
        </p>
      )}
      {!carregando && !erro && ranking.length === 0 && (
        <p className="vazio">Nenhum livro foi emprestado ainda.</p>
      )}

      {ranking.length > 0 && (
        <ol className="lista">
          {ranking.map((item, indice) => (
            <li key={item.livroId}>
              <span className="posicao mono">{indice + 1}</span>
              <div className="principal">
                <span className="titulo">{item.titulo}</span>
              </div>
              <span className="barra-total">
                <span style={{ width: `${(item.totalEmprestimos / maiorTotal) * 100}%` }} />
              </span>
              <span className="numero total mono">
                {item.totalEmprestimos} {item.totalEmprestimos === 1 ? 'empréstimo' : 'empréstimos'}
              </span>
            </li>
          ))}
        </ol>
      )}
    </section>
  )
}
