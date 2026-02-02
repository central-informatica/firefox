from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.api.deps import check_auth_with_ip
from backend.app.db.session import get_db
from backend.app.schemas.regras_acesso import (
    RegraAcessoCreate,
    RegraAcessoUpdate,
    RegraAcessoOut,
)
from backend.app.crud.regras_acesso import crud_regras_acesso


router = APIRouter(prefix="/regras-acesso", tags=["Regras de Acesso"])


@router.get("/", response_model=list[RegraAcessoOut])
def listar(db: Session = Depends(get_db), current_user=Depends(check_auth_with_ip)):
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Apenas administradores podem listar regras de acesso")
    return crud_regras_acesso.listar(db)


@router.get("/grupo/{grupo_id}", response_model=list[RegraAcessoOut])
def listar_grupo(grupo_id: str, db: Session = Depends(get_db), current_user=Depends(check_auth_with_ip)):
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Apenas administradores podem listar regras de acesso")
    return crud_regras_acesso.listar_por_grupo(db, grupo_id)


@router.get("/{regra_id}", response_model=RegraAcessoOut)
def obter(regra_id: str, db: Session = Depends(get_db), current_user=Depends(check_auth_with_ip)):
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Apenas administradores podem visualizar regras de acesso")
    return crud_regras_acesso.get(db, regra_id)


@router.post("/", response_model=RegraAcessoOut, status_code=201)
def criar(data: RegraAcessoCreate, db: Session = Depends(get_db), current_user=Depends(check_auth_with_ip)):
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Apenas administradores podem criar regras de acesso")
    return crud_regras_acesso.criar(db, data)


@router.put("/{regra_id}", response_model=RegraAcessoOut)
def atualizar(regra_id: str, data: RegraAcessoUpdate, db: Session = Depends(get_db), current_user=Depends(check_auth_with_ip)):
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Apenas administradores podem atualizar regras de acesso")
    return crud_regras_acesso.atualizar(db, regra_id, data)


@router.delete("/{regra_id}")
def deletar(regra_id: str, db: Session = Depends(get_db), current_user=Depends(check_auth_with_ip)):
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Apenas administradores podem deletar regras de acesso")
    return crud_regras_acesso.deletar(db, regra_id)
