import { BookOpen, FileText, Library, Moon, Repeat, Sun, Trophy, Users } from 'lucide-react'
import { Link, NavLink, Navigate, Route, Routes, useLocation } from 'react-router-dom'
import Acervo from './pages/Acervo.jsx'
import Emprestimos from './pages/Emprestimos.jsx'
import Leitores from './pages/Leitores.jsx'
import Ranking from './pages/Ranking.jsx'
import Relatorio from './pages/Relatorio.jsx'
import { useTema } from './tema.js'

// Para criar uma tela nova: crie o arquivo em src/pages e adicione uma linha aqui.
const telas = [
  { caminho: '/acervo', nome: 'Acervo', componente: Acervo, icone: BookOpen },
  { caminho: '/emprestimos', nome: 'Empréstimos', componente: Emprestimos, icone: Repeat },
  { caminho: '/ranking', nome: 'Ranking', componente: Ranking, icone: Trophy },
  { caminho: '/relatorio', nome: 'Relatório', componente: Relatorio, icone: FileText },
  { caminho: '/leitores', nome: 'Leitores', componente: Leitores, icone: Users },
]

export default function App() {
  const { tema, alternarTema } = useTema()
  const { pathname } = useLocation()

  return (
    <div className="app">
      {/* Navegação: painel à esquerda no computador, cápsula no rodapé no celular */}
      <aside className="lateral">
        <Link to="/acervo" className="marca" aria-label="Biblioteca Comunitária, acervo">
          <Library size={18} strokeWidth={2.2} />
          BIBLIOTECA
        </Link>

        <nav aria-label="Navegação">
          {telas.map((tela) => (
            <NavLink key={tela.caminho} to={tela.caminho}>
              {({ isActive }) => (
                <>
                  <tela.icone size={18} strokeWidth={isActive ? 2.2 : 1.8} />
                  <span>{tela.nome}</span>
                </>
              )}
            </NavLink>
          ))}
        </nav>

        <button className="tema" onClick={alternarTema}>
          {tema === 'dark' ? <Sun size={17} /> : <Moon size={17} />}
          <span>{tema === 'dark' ? 'Tema claro' : 'Tema escuro'}</span>
        </button>
      </aside>

      {/* key={pathname}: a animação de entrada toca de novo a cada troca de tela */}
      <main className="conteudo" key={pathname}>
        <Routes>
          <Route path="/" element={<Navigate to="/acervo" replace />} />
          {telas.map((tela) => (
            <Route key={tela.caminho} path={tela.caminho} element={<tela.componente />} />
          ))}
        </Routes>
        <Rodape />
      </main>
    </div>
  )
}

function Rodape() {
  return (
    <footer className="rodape">
      <span>Biblioteca Comunitária · boas leituras</span>
    </footer>
  )
}
