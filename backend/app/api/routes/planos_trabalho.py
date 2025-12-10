from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.db.database import get_db

from backend.app.crud.planos_trabalho import (
    listar_planos_trabalho,
    get_planos_trabalho,
    criar_planos_trabalho,
    atualizar_planos_trabalho,
    deletar_planos_trabalho,
)

router = APIRouter(prefix="/planos_trabalho", tags=["Planos"])


@router.get("/")
def listar(db: Session = Depends(get_db)):
    planos_trabalho = listar_planos_trabalho(db)
    return [
        {
            "grupo_id": p.grupo_id,
            "empresa_id": p.empresa_id,
            "plano_id": p.plano_id,
            "nome": p.nome,
            "criado_em": p.criado_em,
        }
        for p in planos_trabalho
    ]


@router.get("/{plano_id}")
def obter(grupo_id: int, db: Session = Depends(get_db)):
    planos_trabalho = get_planos_trabalho(db, grupo_id)
    if not planos_trabalho:
        raise HTTPException(status_code=404, detail="Plano de trabalho não encontrado")
    return planos_trabalho


@router.post("/")
def criar(payload: dict, db: Session = Depends(get_db)):
    return criar_planos_trabalho(db, payload)


@router.put("/{planos_id}")
def atualizar(plano_id: int, payload: dict, db: Session = Depends(get_db)):
    planos_trabalho = atualizar_planos_trabalho(db, plano_id, payload)
    if not planos_trabalho:
        raise HTTPException(status_code=404, detail="Plano de trabalho não encontrado")
    return planos_trabalho


@router.delete("/{plano_id}")
def remover(plano_id: int, db: Session = Depends(get_db)):
    sucesso = deletar_planos_trabalho(db, plano_id)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Plano de trabalho não encontrado")
    return {"detail": "Plano de trabalho removido com sucesso"}