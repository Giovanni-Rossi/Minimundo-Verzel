// Regras do formulário de cadastro de livro (BIBL-1), no mesmo formato do contrato.
// As mensagens são as mesmas que a API devolve, para o usuário ver sempre o mesmo texto.
import { z } from 'zod'

export const livroSchema = z.object({
  titulo: z.string().trim().min(1, 'Título é obrigatório.'),
  autor: z.string().trim(),
  // Campo numérico vazio chega como NaN: a mensagem de "obrigatório" cobre esse caso.
  ano: z
    .number({ error: 'Ano é obrigatório.' })
    .int('Ano deve ser um número inteiro.')
    .max(new Date().getFullYear(), 'Ano não pode ser no futuro.'),
  copiasDisponiveis: z
    .number({ error: 'Quantidade de cópias é obrigatória.' })
    .int('Cópias devem ser um número inteiro.')
    .min(0, 'Cópias não podem ser negativas.'),
})
