// Tema claro/escuro. A escolha fica guardada no navegador (localStorage)
// e vira o atributo data-theme no <html>, que o index.css usa para trocar as cores.
import { useEffect, useState } from 'react'

function temaInicial() {
  const salvo = localStorage.getItem('tema')
  if (salvo === 'light' || salvo === 'dark') return salvo
  // Primeira visita: segue a preferência do sistema.
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

export function useTema() {
  const [tema, setTema] = useState(temaInicial)

  useEffect(() => {
    document.documentElement.dataset.theme = tema
    localStorage.setItem('tema', tema)
  }, [tema])

  function alternarTema() {
    setTema(tema === 'dark' ? 'light' : 'dark')
  }

  return { tema, alternarTema }
}
