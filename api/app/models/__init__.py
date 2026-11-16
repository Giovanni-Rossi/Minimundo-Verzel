"""Tabelas do banco. Importar este pacote registra todas elas no Base.metadata.

Este é o único lugar que conhece os nomes do banco do time de banco (tabelas, colunas,
tipos). Os atributos usam os nomes do contrato; quando a coluna se chama diferente,
o nome real aparece só aqui. Se o SQL do time de banco mudar, só esta pasta muda.

| Contrato (atributo)        | Banco (SQL do time de banco)        |
|----------------------------|-------------------------------------|
| LeitorModel                | tabela usuarios (perfil = leitor)   |
| LivroModel.ano             | coluna livros.ano_publicacao        |
| EmprestimoModel.situacao   | coluna emprestimos.status           |

As tabelas levam o sufixo Model para não colidir com os schemas de mesmo nome
(LivroModel é a tabela; Livro é o JSON da API).
"""

from app.models.emprestimo import EmprestimoModel
from app.models.leitor import LeitorModel
from app.models.livro import LivroModel
from app.models.perfil import PerfilUsuario
from app.models.situacao import Situacao

__all__ = ["EmprestimoModel", "LeitorModel", "LivroModel", "PerfilUsuario", "Situacao"]
