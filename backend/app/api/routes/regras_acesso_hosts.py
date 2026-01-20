from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.regras_acesso_hosts import (
    RegraAcessoHostCreate,
    RegraAcessoHostUpdate,
    RegraAcessoHostOut,
)
from backend.app.crud.regras_acesso_hosts import crud_regras_acesso_hosts


router = APIRouter(prefix="/regras-acesso-hosts", tags=["Regras de Acesso (Hosts)"])


@router.get("/", response_model=list[RegraAcessoHostOut])
def listar(db: Session = Depends(get_db)):
    return crud_regras_acesso_hosts.listar(db)


@router.get("/grupo/{grupo_id}", response_model=list[RegraAcessoHostOut])
def listar_grupo(grupo_id: int, db: Session = Depends(get_db)):
    return crud_regras_acesso_hosts.listar_por_grupo(db, grupo_id)


@router.get("/{regra_id}", response_model=RegraAcessoHostOut)
def obter(regra_id: int, db: Session = Depends(get_db)):
    return crud_regras_acesso_hosts.get(db, regra_id)


@router.post("/", response_model=RegraAcessoHostOut, status_code=201)
def criar(data: RegraAcessoHostCreate, db: Session = Depends(get_db)):
    return crud_regras_acesso_hosts.criar(db, data)


@router.put("/{regra_id}", response_model=RegraAcessoHostOut)
def atualizar(regra_id: int, data: RegraAcessoHostUpdate, db: Session = Depends(get_db)):
    return crud_regras_acesso_hosts.atualizar(db, regra_id, data)


@router.delete("/{regra_id}")
def deletar(regra_id: int, db: Session = Depends(get_db)):
    return crud_regras_acesso_hosts.deletar(db, regra_id)
