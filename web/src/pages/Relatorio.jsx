// BIBL-4 (relatório com filtros) e BIBL-5 (exportação em CSV)
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { listarEmprestimos, listarLeitores, urlCsv } from '../api.js'
import { formatarData, nomeSituacao } from '../formatar.js'

const semFiltros = { leitorId: '', inicio: '', fim: '', situacao: '' }

export default function Relatorio() {
  const [leitores, setLeitores] = useState([])
  const [erroLeitores, setErroLeitores] = useState('')
  const [filtros, setFiltros] = useState(semFiltros)
  // Resultado da última busca, guardado junto com os filtros que o geraram.
  const [resposta, setResposta] = useState(null)

  useEffect(() => {
    listarLeitores()
      .then(setLeitores)
      .catch((e) => setErroLeitores(e.message))
  }, [])

  // Recarrega o relatório sempre que um filtro muda.
  useEffect(() => {
    // Se o usuário trocar o filtro antes da resposta chegar, ignora a resposta antiga.
    let atual = true
    listarEmprestimos(filtros)
      .then((dados) => atual && setResposta({ filtros, emprestimos: dados, erro: '' }))
      .catch((e) => atual && setResposta({ filtros, emprestimos: [], erro: e.message }))
    return () => {
      atual = false
    }
  }, [filtros])

  const carregando = resposta?.filtros !== filtros
  const emprestimos = carregando ? [] : resposta.emprestimos
  const erro = carregando ? '' : resposta.erro

  function mudarFiltro(evento) {
    const { name, value } = evento.target
    setFiltros((anteriores) => ({ ...anteriores, [name]: value }))
  }

  const temFiltro = Object.values(filtros).some(Boolean)
  // Com filtro inválido a API devolve JSON de erro em vez do arquivo, então não deixa exportar.
  const podeExportar = !carregando && !erro

  return (
    <section>
      <h2>Relatório de empréstimos</h2>

      <div className="formulario">
        <label>
          Leitor
          <select name="leitorId" value={filtros.leitorId} onChange={mudarFiltro}>
            <option value="">Todos</option>
            {leitores.map((leitor) => (
              <option key={leitor.id} value={leitor.id}>
                {leitor.nome}
              </option>
            ))}
          </select>
        </label>
        <label>
          De
          <input type="date" name="inicio" value={filtros.inicio} max={filtros.fim || undefined} onChange={mudarFiltro} />
        </label>
        <label>
          Até
          <input type="date" name="fim" value={filtros.fim} min={filtros.inicio || undefined} onChange={mudarFiltro} />
        </label>
        <label>
          Situação
          <select name="situacao" value={filtros.situacao} onChange={mudarFiltro}>
            <option value="">Todas</option>
            <option value="ativo">Ativo</option>
            <option value="devolvido">Devolvido</option>
          </select>
        </label>
        <button type="button" className="secundario" onClick={() => setFiltros(semFiltros)} disabled={!temFiltro}>
          Limpar filtros
        </button>
        {podeExportar ? (
          <a className="botao" href={urlCsv(filtros)} download="emprestimos.csv">
            Exportar CSV
          </a>
        ) : (
          <button type="button" disabled>
            Exportar CSV
          </button>
        )}
      </div>

      {erroLeitores && <p className="erro">{erroLeitores}</p>}
      {erro && <p className="erro">{erro}</p>}

      {carregando ? (
        <p className="vazio">Carregando…</p>
      ) : erro ? null : emprestimos.length === 0 ? (
        <p className="vazio">
          {temFiltro ? 'Nenhum empréstimo atende a esses filtros.' : 'Nenhum empréstimo registrado ainda.'}
        </p>
      ) : (
        <>
          <p className="resumo">
            {emprestimos.length} {emprestimos.length === 1 ? 'empréstimo' : 'empréstimos'}
          </p>
          <table>
            <thead>
              <tr>
                <th>Livro</th>
                <th>Leitor</th>
                <th>Data</th>
                <th>Devolução</th>
                <th>Situação</th>
              </tr>
            </thead>
            <tbody>
              {emprestimos.map((emprestimo) => (
                <tr key={emprestimo.id}>
                  <td>{emprestimo.livro.titulo}</td>
                  <td>
                    <Link to={`/leitores?id=${emprestimo.leitor.id}`}>{emprestimo.leitor.nome}</Link>
                  </td>
                  <td>{formatarData(emprestimo.dataEmprestimo)}</td>
                  <td>{formatarData(emprestimo.dataDevolucao)}</td>
                  <td>
                    <span className={`etiqueta ${emprestimo.situacao}`}>{nomeSituacao[emprestimo.situacao]}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </section>
  )
}
