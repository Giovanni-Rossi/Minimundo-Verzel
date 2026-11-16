// Formatação de dados para exibir nas telas.

// "2026-11-16T19:30:00Z" -> "16/11/2026"
export function formatarData(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('pt-BR')
}

export const nomeSituacao = { ativo: 'Ativo', devolvido: 'Devolvido' }
