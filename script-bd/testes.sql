
BEGIN;

CREATE FUNCTION pg_temp.tenta(comando TEXT) RETURNS TEXT AS $$
DECLARE
  linhas INTEGER;
BEGIN
  EXECUTE comando;
  GET DIAGNOSTICS linhas = ROW_COUNT;
  RETURN 'aceito: ' || linhas || ' linha(s)';
EXCEPTION WHEN OTHERS THEN
  RETURN 'bloqueado: ' || SQLERRM;
END;
$$ LANGUAGE plpgsql;

WITH resultado AS MATERIALIZED (
  SELECT n, teste, esperado, pg_temp.tenta(comando) AS obtido
  FROM (VALUES
    (1, 'Ana (3 ativos) pega o 4º livro', 'bloqueado',
     $q$INSERT INTO emprestimos (livro_id, leitor_id)
        SELECT l.id, u.id FROM livros l, usuarios u
        WHERE l.titulo = 'O Alquimista' AND u.email = 'ana@biblioteca.local'$q$),

    (2, 'Bibliotecária pega livro', 'bloqueado',
     $q$INSERT INTO emprestimos (livro_id, leitor_id)
        SELECT l.id, u.id FROM livros l, usuarios u
        WHERE l.titulo = 'O Alquimista' AND u.email = 'marta@biblioteca.local'$q$),

    (3, 'Bruno (1 ativo) pega livro', 'aceito: 1',
     $q$INSERT INTO emprestimos (livro_id, leitor_id)
        SELECT l.id, u.id FROM livros l, usuarios u
        WHERE l.titulo = 'O Alquimista' AND u.email = 'bruno@biblioteca.local'$q$),

    (4, 'Empréstimo ATIVO com data de devolução', 'bloqueado',
     $q$INSERT INTO emprestimos (livro_id, leitor_id, status, data_devolucao)
        SELECT l.id, u.id, 'ATIVO', localtimestamp FROM livros l, usuarios u
        WHERE l.titulo = 'O Cortiço' AND u.email = 'carla@biblioteca.local'$q$),

    (5, 'Empréstimo DEVOLVIDO sem data de devolução', 'bloqueado',
     $q$INSERT INTO emprestimos (livro_id, leitor_id, status)
        SELECT l.id, u.id, 'DEVOLVIDO' FROM livros l, usuarios u
        WHERE l.titulo = 'O Cortiço' AND u.email = 'carla@biblioteca.local'$q$),

    (6, 'Devolver mudando só a data (esqueceu o status)', 'bloqueado',
     $q$UPDATE emprestimos SET data_devolucao = localtimestamp
        WHERE status = 'ATIVO' AND leitor_id = (SELECT id FROM usuarios WHERE email = 'ana@biblioteca.local')
          AND livro_id = (SELECT id FROM livros WHERE titulo = 'Dom Casmurro')$q$),

    (7, 'Ana devolve Dom Casmurro (status + data juntos)', 'aceito: 1',
     $q$UPDATE emprestimos SET status = 'DEVOLVIDO', data_devolucao = localtimestamp
        WHERE status = 'ATIVO' AND leitor_id = (SELECT id FROM usuarios WHERE email = 'ana@biblioteca.local')
          AND livro_id = (SELECT id FROM livros WHERE titulo = 'Dom Casmurro')$q$),

    (8, 'Ana pega outro livro (agora tem 2 ativos)', 'aceito: 1',
     $q$INSERT INTO emprestimos (livro_id, leitor_id)
        SELECT l.id, u.id FROM livros l, usuarios u
        WHERE l.titulo = 'O Alquimista' AND u.email = 'ana@biblioteca.local'$q$),

    (9, 'Reabrir empréstimo devolvido de quem já tem 3 ativos', 'bloqueado',
     $q$UPDATE emprestimos SET status = 'ATIVO', data_devolucao = NULL
        WHERE status = 'DEVOLVIDO' AND leitor_id = (SELECT id FROM usuarios WHERE email = 'ana@biblioteca.local')$q$),

    (10, 'Gravar empréstimo já devolvido (histórico) de quem tem 3 ativos', 'aceito: 1',
     $q$INSERT INTO emprestimos (livro_id, leitor_id, data_emprestimo, status, data_devolucao)
        SELECT l.id, u.id, localtimestamp - interval '2 days', 'DEVOLVIDO', localtimestamp FROM livros l, usuarios u
        WHERE l.titulo = 'O Cortiço' AND u.email = 'ana@biblioteca.local'$q$),

    (11, 'Baixar cópia de livro com 0 cópias (Torto Arado)', 'aceito: 0',
     $q$UPDATE livros SET copias_disponiveis = copias_disponiveis - 1
        WHERE titulo = 'Torto Arado' AND copias_disponiveis > 0$q$),

    (12, 'Status inválido', 'bloqueado',
     $q$INSERT INTO emprestimos (livro_id, leitor_id, status)
        SELECT l.id, u.id, 'PERDIDO' FROM livros l, usuarios u
        WHERE l.titulo = 'O Cortiço' AND u.email = 'carla@biblioteca.local'$q$),

    (13, 'Cópias negativas no cadastro', 'bloqueado',
     $q$INSERT INTO livros (titulo, autor, ano_publicacao, copias_disponiveis) VALUES ('Teste', 'Autor', 2000, -1)$q$),

    (14, 'E-mail repetido (com maiúsculas)', 'bloqueado',
     $q$INSERT INTO usuarios (nome, email, senha_hash) VALUES ('Outra Ana', 'ANA@biblioteca.local', 'x')$q$),

    (15, 'Perfil inválido', 'bloqueado',
     $q$INSERT INTO usuarios (nome, email, senha_hash, perfil) VALUES ('X', 'x@teste.com', 'x', 'admin')$q$)
  ) AS casos (n, teste, esperado, comando)
)
SELECT n, teste, esperado, obtido,
       CASE WHEN obtido LIKE esperado || '%' THEN 'OK' ELSE 'FALHOU' END AS ok
FROM resultado
ORDER BY n;

ROLLBACK;

SELECT column_name FROM information_schema.columns
WHERE table_name = 'relatorio_emprestimos' ORDER BY ordinal_position;

SELECT * FROM relatorio_emprestimos ORDER BY data_emprestimo DESC;

-- filtros combinados: leitor + situação + período (data final inclusiva)
SELECT * FROM relatorio_emprestimos
WHERE leitor_id = (SELECT id FROM usuarios WHERE email = 'bruno@biblioteca.local')
  AND situacao = 'ativo'
  AND data_emprestimo >= current_date - 30
  AND data_emprestimo <  current_date + 1;

-- filtro sem resultado: deve voltar 0 linhas, sem erro (estado vazio)
SELECT * FROM relatorio_emprestimos WHERE situacao = 'devolvido' AND leitor_id = -1;

-- ranking (BIBL-3): conta ativos e devolvidos
SELECT l.id, l.titulo, count(*) AS total_emprestimos
FROM emprestimos e
JOIN livros l ON l.id = e.livro_id
GROUP BY l.id, l.titulo
ORDER BY total_emprestimos DESC, l.titulo;
