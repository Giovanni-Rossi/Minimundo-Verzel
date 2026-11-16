-- =============================================================
-- Banco de dados · Biblioteca Comunitária (PostgreSQL / Neon)
-- Rode este arquivo inteiro no SQL Editor do Neon.
-- =============================================================

-- -------------------------------------------------------------
-- 1. TIPOS (enums)
-- -------------------------------------------------------------
CREATE TYPE perfil_usuario    AS ENUM ('leitor', 'bibliotecario');
CREATE TYPE status_emprestimo AS ENUM ('ATIVO', 'DEVOLVIDO');

-- -------------------------------------------------------------
-- 2. TABELAS
-- -------------------------------------------------------------

-- usuarios · BIBL-2, BIBL-4
CREATE TABLE usuarios (
  id          SERIAL PRIMARY KEY,
  nome        VARCHAR(120)   NOT NULL,
  email       VARCHAR(160)   NOT NULL UNIQUE,          -- login por e-mail
  senha_hash  VARCHAR(100)   NOT NULL,                 -- senha nunca em texto (bcrypt)
  perfil      perfil_usuario NOT NULL DEFAULT 'leitor',
  criado_em   TIMESTAMPTZ    NOT NULL DEFAULT now()
);

-- livros · BIBL-1, BIBL-2, BIBL-3
CREATE TABLE livros (
  id                 SERIAL PRIMARY KEY,
  titulo             VARCHAR(200) NOT NULL CHECK (btrim(titulo) <> ''),  -- título não pode ser vazio
  autor              VARCHAR(150) NOT NULL,
  ano_publicacao     SMALLINT     NOT NULL,             -- "não pode ser futuro" é validado na API
  copias_disponiveis INT          NOT NULL CHECK (copias_disponiveis >= 0),
  criado_em          TIMESTAMPTZ  NOT NULL DEFAULT now()
);

-- emprestimos · BIBL-2, BIBL-3, BIBL-4, BIBL-5
CREATE TABLE emprestimos (
  id              SERIAL PRIMARY KEY,
  livro_id        INT               NOT NULL REFERENCES livros(id),
  leitor_id       INT               NOT NULL REFERENCES usuarios(id),
  status          status_emprestimo NOT NULL DEFAULT 'ATIVO',
  data_emprestimo TIMESTAMPTZ       NOT NULL DEFAULT now(),
  data_devolucao  TIMESTAMPTZ,                          -- NULL = ativo · preenchida = devolvido
  -- status e data de devolução precisam combinar
  CONSTRAINT status_coerente CHECK (
    (status = 'ATIVO'     AND data_devolucao IS NULL) OR
    (status = 'DEVOLVIDO' AND data_devolucao IS NOT NULL)
  )
);

-- -------------------------------------------------------------
-- 3. ÍNDICES (deixam as consultas mais usadas rápidas)
-- -------------------------------------------------------------
CREATE INDEX idx_emprestimos_leitor_status ON emprestimos (leitor_id, status);  -- limite de 3 ativos
CREATE INDEX idx_emprestimos_livro         ON emprestimos (livro_id);           -- ranking
CREATE INDEX idx_emprestimos_data          ON emprestimos (data_emprestimo);    -- filtro por período

-- -------------------------------------------------------------
-- 4. VIEW do relatório · BIBL-4 e BIBL-5 (CSV usa a mesma)
-- -------------------------------------------------------------
CREATE VIEW relatorio_emprestimos AS
SELECT
  e.id,
  l.titulo           AS livro,
  u.nome             AS leitor,
  e.leitor_id,
  e.data_emprestimo,
  e.data_devolucao,
  e.status           AS situacao
FROM emprestimos e
JOIN livros   l ON l.id = e.livro_id
JOIN usuarios u ON u.id = e.leitor_id;

-- -------------------------------------------------------------
-- 5. DADOS DE TESTE (seed)
-- senha_hash abaixo é só um exemplo, não é uma senha real
-- -------------------------------------------------------------
INSERT INTO usuarios (nome, email, senha_hash, perfil) VALUES
  ('Ana Bibliotecária', 'ana@biblioteca.com',   '$2b$10$exemploexemploexemploexemploexemploexemploex', 'bibliotecario'),
  ('Bruno Leitor',      'bruno@email.com',      '$2b$10$exemploexemploexemploexemploexemploexemploex', 'leitor'),
  ('Carla Leitora',     'carla@email.com',      '$2b$10$exemploexemploexemploexemploexemploexemploex', 'leitor');

INSERT INTO livros (titulo, autor, ano_publicacao, copias_disponiveis) VALUES
  ('Dom Casmurro',        'Machado de Assis',          1899, 3),
  ('O Pequeno Príncipe',  'Antoine de Saint-Exupéry',  1943, 2),
  ('Capitães da Areia',   'Jorge Amado',               1937, 0),  -- para testar "sem cópia"
  ('Vidas Secas',         'Graciliano Ramos',          1938, 4),
  ('A Hora da Estrela',   'Clarice Lispector',         1977, 2);

-- Carla com 3 empréstimos ATIVOS (para testar o limite)
INSERT INTO emprestimos (livro_id, leitor_id) VALUES (1, 3), (2, 3), (4, 3);
UPDATE livros SET copias_disponiveis = copias_disponiveis - 1 WHERE id IN (1, 2, 4);

-- Bruno com 1 empréstimo já DEVOLVIDO (histórico)
INSERT INTO emprestimos (livro_id, leitor_id, status, data_emprestimo, data_devolucao)
VALUES (1, 2, 'DEVOLVIDO', now() - interval '10 days', now() - interval '3 days');
