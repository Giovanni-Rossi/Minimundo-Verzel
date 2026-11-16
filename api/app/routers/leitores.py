from fastapi import APIRouter

from app.dependencias import LeitorServiceDep
from app.schemas import Leitor

router = APIRouter(prefix="/leitores", tags=["Leitores"])


@router.get(
    "",
    response_model=list[Leitor],
    operation_id="listarLeitores",
    summary="Listar leitores (semeados no banco)",
)
def listar_leitores(servico: LeitorServiceDep):
    return servico.listar_leitores()
