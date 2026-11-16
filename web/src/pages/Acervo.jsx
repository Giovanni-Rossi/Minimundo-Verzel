// BIBL-1: cadastrar e listar livros.
// BIBL-2 (parte de emprestar): escolher o leitor e clicar em Emprestar.
import { useEffect, useState } from 'react'
import { cadastrarLivro, emprestar, listarLeitores, listarLivros } from '../api.js'

const FORMULARIO_VAZIO = { titulo: '', autor: '', ano: '', copiasDisponiveis: '' }

// Checagem rápida antes de enviar. Quem decide de verdade é a API:
// se ela recusar, a mensagem dela também aparece na tela.
function validar(form) {
  if (!form.titulo.trim()) return 'Título é obrigatório.'
  if (form.ano === '') return 'Ano é obrigatório.'
  if (Number(form.ano) > new Date().getFullYear()) return 'Ano não pode ser no futuro.'
  if (form.copiasDisponiveis === '') return 'Quantidade de cópias é obrigatória.'
  if (Number(form.copiasDisponiveis) < 0) return 'Cópias não podem ser negativas.'
  return ''
}

export default function Acervo() {
  // Dados que vêm da API
  const [livros, setLivros] = useState([])
  const [leitores, setLeitores] = useState([])
  const [carregando, setCarregando] = useState(true)
  const [erroLista, setErroLista] = useState('')

  // Formulário de cadastro
  const [form, setForm] = useState(FORMULARIO_VAZIO)
  const [erroCadastro, setErroCadastro] = useState('')
  const [salvando, setSalvando] = useState(false)

  // Empréstimo
  const [leitorId, setLeitorId] = useState('')
  const [erroEmprestimo, setErroEmprestimo] = useState('')
  const [mensagem, setMensagem] = useState('')
  const [emprestandoId, setEmprestandoId] = useState(null)

  // Busca a lista de livros de novo (usada ao abrir a tela e depois de cada ação).
  async function carregarLivros() {
    try {
      setLivros(await listarLivros())
      setErroLista('')
    } catch (e) {
      setErroLista(e.message)
    }
  }

  // Ao abrir a tela: busca livros e leitores.
  useEffect(() => {
    async function carregarTudo() {
      await carregarLivros()
      try {
        setLeitores(await listarLeitores())
      } catch (e) {
        setErroEmprestimo(e.message)
      }
      setCarregando(false)
    }
    carregarTudo()
  }, [])

  function mudarCampo(evento) {
    setForm({ ...form, [evento.target.name]: evento.target.value })
  }

  async function aoCadastrar(evento) {
    evento.preventDefault() // não deixa o navegador recarregar a página

    const problema = validar(form)
    if (problema) {
      setErroCadastro(problema)
      return
    }

    setSalvando(true)
    try {
      await cadastrarLivro({
        titulo: form.titulo.trim(),
        autor: form.autor.trim(),
        ano: Number(form.ano),
        copiasDisponiveis: Number(form.copiasDisponiveis),
      })
      setForm(FORMULARIO_VAZIO)
      setErroCadastro('')
      await carregarLivros() // o livro novo aparece sem recarregar a página
    } catch (e) {
      setErroCadastro(e.message)
    }
    setSalvando(false)
  }

  async function aoEmprestar(livro) {
    setMensagem('')
    if (!leitorId) {
      setErroEmprestimo('Escolha um leitor antes de emprestar.')
      return
    }

    setEmprestandoId(livro.id)
    try {
      await emprestar(livro.id, leitorId)
      const leitor = leitores.find((l) => String(l.id) === leitorId)
      setMensagem(`"${livro.titulo}" emprestado para ${leitor?.nome ?? 'o leitor'}.`)
      setErroEmprestimo('')
    } catch (e) {
      // Ex.: "Livro sem cópias disponíveis." ou "Leitor já tem 3 empréstimos ativos."
      setErroEmprestimo(e.message)
    }
    await carregarLivros() // a quantidade de cópias na tela acompanha o banco
    setEmprestandoId(null)
  }

  return (
    <section>
      <h2>Acervo</h2>

      <form className="formulario" onSubmit={aoCadastrar} noValidate>
        <label className="campo-largo">
          Título
          <input name="titulo" value={form.titulo} onChange={mudarCampo} />
        </label>
        <label>
          Autor
          <input name="autor" value={form.autor} onChange={mudarCampo} />
        </label>
        <label className="campo-curto">
          Ano
          <input name="ano" type="number" value={form.ano} onChange={mudarCampo} />
        </label>
        <label className="campo-curto">
          Cópias
          <input
            name="copiasDisponiveis"
            type="number"
            value={form.copiasDisponiveis}
            onChange={mudarCampo}
          />
        </label>
        <button type="submit" disabled={salvando}>
          {salvando ? 'Salvando...' : 'Cadastrar'}
        </button>
        {erroCadastro && (
          <p className="erro linha-inteira" role="alert">
            {erroCadastro}
          </p>
        )}
      </form>

      <div className="barra">
        <label>
          Leitor que vai pegar o livro
          <select value={leitorId} onChange={(e) => setLeitorId(e.target.value)}>
            <option value="">Escolha um leitor</option>
            {leitores.map((leitor) => (
              <option key={leitor.id} value={leitor.id}>
                {leitor.nome}
              </option>
            ))}
          </select>
        </label>
        {erroEmprestimo && (
          <p className="aviso" role="alert">
            {erroEmprestimo}
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
      {!carregando && !erroLista && livros.length === 0 && (
        <p className="vazio">Nenhum livro cadastrado ainda.</p>
      )}

      {livros.length > 0 && (
        <table>
          <thead>
            <tr>
              <th>Título</th>
              <th>Autor</th>
              <th>Ano</th>
              <th>Cópias</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {livros.map((livro) => (
              <tr key={livro.id}>
                <td>{livro.titulo}</td>
                <td>{livro.autor}</td>
                <td>{livro.ano}</td>
                <td>{livro.copiasDisponiveis}</td>
                <td>
                  <button
                    onClick={() => aoEmprestar(livro)}
                    disabled={livro.copiasDisponiveis === 0 || emprestandoId === livro.id}
                  >
                    {livro.copiasDisponiveis === 0 ? 'Indisponível' : 'Emprestar'}
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
