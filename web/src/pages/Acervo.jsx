// BIBL-1: cadastrar e listar livros.
// BIBL-2 (parte de emprestar): escolher o leitor e clicar em Emprestar.
import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import {
  cadastrarLivro,
  emprestar,
  listarEmprestimos,
  listarLeitores,
  listarLivros,
} from '../api.js'
import { livroSchema } from '../schemas/livro.js'

export default function Acervo() {
  // Dados que vêm da API
  const [livros, setLivros] = useState([])
  const [leitores, setLeitores] = useState([])
  const [ativos, setAtivos] = useState([]) // empréstimos ainda não devolvidos
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

  // Busca os livros e os empréstimos ativos de novo
  // (usada ao abrir a tela e depois de cada ação).
  async function carregarLivros() {
    try {
      const [listaLivros, listaAtivos] = await Promise.all([
        listarLivros(),
        listarEmprestimos({ situacao: 'ativo' }),
      ])
      setLivros(listaLivros)
      setAtivos(listaAtivos)
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

  // O leitor escolhido já está com este livro (empréstimo ativo)?
  // Regra da tela: a mesma pessoa não pega duas cópias do mesmo título.
  function leitorJaTem(livro) {
    return ativos.some((e) => e.livro.id === livro.id && String(e.leitor.id) === leitorId)
  }

  const nomeDoLeitor = leitores.find((l) => String(l.id) === leitorId)?.nome

  async function aoEmprestar(livro) {
    setMensagem('')
    if (!leitorId) {
      setErroEmprestimo('Escolha um leitor antes de emprestar.')
      return
    }
    if (leitorJaTem(livro)) {
      setErroEmprestimo('Este leitor já está com este livro.')
      return
    }

    setEmprestandoId(livro.id)
    try {
      await emprestar(livro.id, leitorId)
      setMensagem(`"${livro.titulo}" emprestado para ${nomeDoLeitor}.`)
      setErroEmprestimo('')
    } catch (e) {
      // Ex.: "Livro sem cópias disponíveis." ou "Leitor já tem 3 empréstimos ativos."
      setErroEmprestimo(e.message)
    }
    await carregarLivros() // a quantidade de cópias na tela acompanha o banco
    setEmprestandoId(null)
  }

  const totalCopias = livros.reduce((soma, livro) => soma + livro.copiasDisponiveis, 0)

  return (
    <section>
      <h2>Acervo</h2>
      {!carregando && !erroLista && (
        <p className="frase">
          Há <span className="chip">{livros.length} {livros.length === 1 ? 'livro' : 'livros'}</span> no
          acervo, com{' '}
          <span className="chip">
            {totalCopias} {totalCopias === 1 ? 'cópia' : 'cópias'}
          </span>{' '}
          na estante agora.
        </p>
      )}

      <form className="formulario" onSubmit={handleSubmit(aoCadastrar)} noValidate>
        <label className="campo-largo">
          Título
          <input aria-invalid={Boolean(errors.titulo)} {...register('titulo')} />
          {errors.titulo && <span className="erro-campo">{errors.titulo.message}</span>}
        </label>
        <label>
          Autor
          <input {...register('autor')} />
        </label>
        <label className="campo-curto">
          Ano
          <input
            type="number"
            aria-invalid={Boolean(errors.ano)}
            {...register('ano', { valueAsNumber: true })}
          />
          {errors.ano && <span className="erro-campo">{errors.ano.message}</span>}
        </label>
        <label className="campo-curto">
          Cópias
          <input
            type="number"
            aria-invalid={Boolean(errors.copiasDisponiveis)}
            {...register('copiasDisponiveis', { valueAsNumber: true })}
          />
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
          Emprestar para
          <select value={leitorId} onChange={(e) => setLeitorId(e.target.value)}>
            <option value="">Escolha um leitor</option>
            {leitores.map((leitor) => (
              <option key={leitor.id} value={leitor.id}>
                {leitor.nome}
              </option>
            ))}
          </select>
        </label>
      </div>

      {/* Linha reservada para as mensagens: a lista não pula quando elas aparecem. */}
      <div className="mensagens">
        {erroEmprestimo && (
          <p className="aviso" role="alert">
            {erroEmprestimo}
          </p>
        )}
        {mensagem && <p className="sucesso">{mensagem}</p>}
      </div>

      {carregando && livros.length === 0 && <p className="vazio">Carregando...</p>}
      {erroLista && (
        <p className="erro" role="alert">
          {erroLista}
        </p>
      )}
      {!carregando && !erroLista && livros.length === 0 && (
        <p className="vazio">Nenhum livro cadastrado ainda. Cadastre o primeiro acima.</p>
      )}

      {livros.length > 0 && (
        <ul className="lista">
          {livros.map((livro) => (
            <li key={livro.id}>
              <div className="principal">
                <span className="titulo">{livro.titulo}</span>
                <span className="detalhe">
                  {livro.autor ? `${livro.autor} · ` : ''}
                  <span className="mono">{livro.ano}</span>
                </span>
              </div>
              <span className={`numero mono ${livro.copiasDisponiveis === 0 ? 'zerado' : ''}`}>
                {livro.copiasDisponiveis} {livro.copiasDisponiveis === 1 ? 'cópia' : 'cópias'}
              </span>
              <div className="acao">
                {leitorJaTem(livro) ? (
                  <span className="selo com-leitor">Com {nomeDoLeitor}</span>
                ) : livro.copiasDisponiveis === 0 ? (
                  <span className="selo">Sem cópias</span>
                ) : (
                  <button
                    className="pequeno"
                    onClick={() => aoEmprestar(livro)}
                    disabled={emprestandoId === livro.id}
                  >
                    Emprestar
                  </button>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
