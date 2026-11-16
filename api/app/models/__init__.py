"""Tabelas do banco. Importar este pacote registra todas elas no Base.metadata.

As tabelas levam o sufixo Model para não colidir com os schemas do contrato
(LivroModel é a tabela; Livro é o JSON da API).
"""

from app.models.emprestimo import EmprestimoModel
from app.models.leitor import LeitorModel
from app.models.livro import LivroModel
from app.models.situacao import Situacao

__all__ = ["EmprestimoModel", "LeitorModel", "LivroModel", "Situacao"]
