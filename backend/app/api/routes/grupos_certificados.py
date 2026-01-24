from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.api.deps import check_auth
from backend.app.db.session import get_db
from backend.app.schemas.grupos_certificados import (
    GrupoCertCreate,
    GrupoCertUpdate,
    GrupoCertOut,
)
from backend.app.crud.grupos_certificados import crud_grupos_certificados


router = APIRouter(prefix="/grupos-certificados", tags=["Grupos Certificados"])


@router.get("/", response_model=list[GrupoCertOut])
def listar(db: Session = Depends(get_db), current_user=Depends(check_auth)):
    return crud_grupos_certificados.listar(db)


@router.get("/grupo/{grupo_id}", response_model=list[GrupoCertOut])
def listar_grupo(grupo_id: str, db: Session = Depends(get_db), current_user=Depends(check_auth)):
    return crud_grupos_certificados.listar_por_grupo(db, grupo_id)


@router.get("/{grupo_cert_id}", response_model=GrupoCertOut)
def obter(grupo_cert_id: str, db: Session = Depends(get_db), current_user=Depends(check_auth)):
    return crud_grupos_certificados.get(db, grupo_cert_id)


@router.post("/", response_model=GrupoCertOut, status_code=201)
def criar(data: GrupoCertCreate, db: Session = Depends(get_db), current_user=Depends(check_auth)):
    return crud_grupos_certificados.criar(db, data)


@router.put("/{grupo_cert_id}", response_model=GrupoCertOut)
def atualizar(grupo_cert_id: str, data: GrupoCertUpdate, db: Session = Depends(get_db), current_user=Depends(check_auth)):
    return crud_grupos_certificados.atualizar(db, grupo_cert_id, data)


@router.delete("/{grupo_cert_id}")
def deletar(grupo_cert_id: str, db: Session = Depends(get_db), current_user=Depends(check_auth)):
    return crud_grupos_certificados.deletar(db, grupo_cert_id)
