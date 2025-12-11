from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.db.session import get_db

from backend.app.crud.grupos import (
    listar_grupos,
    get_grupo,
    criar_grupo,
    atualizar_grupo,
    deletar_grupo,
)

router = APIRouter(prefix="/grupos", tags=["Grupos"])


@router.get("/")
def listar(db: Session = Depends(get_db)):
    grupos = listar_grupos(db)
    return [
        {
            "grupo_id": g.grupo_id,
            "nome": g.nome,
            "descricao": g.descricao,
        }
        for g in grupos
    ]


@router.get("/{grupo_id}")
def obter(grupo_id: int, db: Session = Depends(get_db)):
    grupo = get_grupo(db, grupo_id)
    if not grupo:
        raise HTTPException(status_code=404, detail="Grupo não encontrado")
    return grupo


@router.post("/")
def criar(payload: dict, db: Session = Depends(get_db)):
    return criar_grupo(db, payload)


@router.put("/{grupo_id}")
def atualizar(grupo_id: int, payload: dict, db: Session = Depends(get_db)):
    grupo = atualizar_grupo(db, grupo_id, payload)
    if not grupo:
        raise HTTPException(status_code=404, detail="Grupo não encontrado")
    return grupo


@router.delete("/{grupo_id}")
def remover(grupo_id: int, db: Session = Depends(get_db)):
    sucesso = deletar_grupo(db, grupo_id)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Grupo não encontrado")
    return {"detail": "Grupo removido com sucesso"}