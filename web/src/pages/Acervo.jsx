// BIBL-1: cadastrar e listar livros.
// BIBL-2 (parte de emprestar): escolher o leitor e clicar em Emprestar.
import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { cadastrarLivro, emprestar, listarLeitores, listarLivros } from '../api.js'
import { livroSchema } from '../schemas/livro.js'

export default function Acervo() {
  // Dados que vêm da API
  const [livros, setLivros] = useState([])
  const [leitores, setLeitores] = useState([])
  const [carregando, setCarregando] = useState(true)
  const [erroLista, setErroLista] = useState('')

  // Formulário de cadastro: o react-hook-form guarda os valores e os erros,
  // e o zod (livroSchema) confere as regras antes de enviar.
  const {
    register,
    handleSubmit,
    reset,
    setError,
    formState: { errors, isSubmitting },
  } = useForm({
    resolver: zodResolver(livroSchema),
    defaultValues: { titulo: '', autor: '', ano: '', copiasDisponiveis: '' },
  })

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

  // Só é chamada se o formulário passou nas regras do livroSchema.
  // "livro" já vem pronto: título sem espaços sobrando e números como número.
  async function aoCadastrar(livro) {
    try {
      await cadastrarLivro(livro)
      reset() // limpa o formulário
      await carregarLivros() // o livro novo aparece sem recarregar a página
    } catch (e) {
      // A API recusou: mostra a mensagem dela abaixo do formulário.
      setError('root', { message: e.message })
    }
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

      <form className="formulario" onSubmit={handleSubmit(aoCadastrar)} noValidate>
        <label className="campo-largo">
          Título
          <input {...register('titulo')} />
          {errors.titulo && <span className="erro-campo">{errors.titulo.message}</span>}
        </label>
        <label>
          Autor
          <input {...register('autor')} />
        </label>
        <label className="campo-curto">
          Ano
          <input type="number" {...register('ano', { valueAsNumber: true })} />
          {errors.ano && <span className="erro-campo">{errors.ano.message}</span>}
        </label>
        <label className="campo-curto">
          Cópias
          <input type="number" {...register('copiasDisponiveis', { valueAsNumber: true })} />
          {errors.copiasDisponiveis && (
            <span className="erro-campo">{errors.copiasDisponiveis.message}</span>
          )}
        </label>
        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Salvando...' : 'Cadastrar'}
        </button>
        {errors.root && (
          <p className="erro linha-inteira" role="alert">
            {errors.root.message}
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
