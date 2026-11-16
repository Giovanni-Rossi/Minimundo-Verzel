import { NavLink, Navigate, Route, Routes } from 'react-router-dom'
import Acervo from './pages/Acervo.jsx'
import Emprestimos from './pages/Emprestimos.jsx'
import Ranking from './pages/Ranking.jsx'
import Relatorio from './pages/Relatorio.jsx'

// Para criar uma tela nova: crie o arquivo em src/pages e adicione uma linha aqui.
const telas = [
  { caminho: '/acervo', nome: 'Acervo', componente: Acervo },
  { caminho: '/emprestimos', nome: 'Empréstimos', componente: Emprestimos },
  { caminho: '/ranking', nome: 'Ranking', componente: Ranking },
  { caminho: '/relatorio', nome: 'Relatório', componente: Relatorio },
]

export default function App() {
  return (
    <div className="app">
      <aside className="menu">
        <h1>
          Biblioteca
          <span>Comunitária</span>
        </h1>
        <nav>
          {telas.map((tela) => (
            <NavLink key={tela.caminho} to={tela.caminho}>
              {tela.nome}
            </NavLink>
          ))}
        </nav>
      </aside>

      <main className="conteudo">
        <Routes>
          <Route path="/" element={<Navigate to="/acervo" replace />} />
          {telas.map((tela) => (
            <Route key={tela.caminho} path={tela.caminho} element={<tela.componente />} />
          ))}
        </Routes>
      </main>
    </div>
  )
}
