from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.grupos_usuarios import (
    GrupoUsuarioCreate,
    GrupoUsuarioUpdate,
    GrupoUsuarioOut,
)
from backend.app.crud.grupos_usuarios import crud_grupos_usuarios


router = APIRouter(prefix="/grupos-usuarios", tags=["Grupos Usuários"])


@router.get("/", response_model=list[GrupoUsuarioOut])
def listar(db: Session = Depends(get_db)):
    return crud_grupos_usuarios.listar(db)


@router.get("/grupo/{grupo_id}", response_model=list[GrupoUsuarioOut])
def listar_grupo(grupo_id: int, db: Session = Depends(get_db)):
    return crud_grupos_usuarios.listar_por_grupo(db, grupo_id)


@router.get("/{grupo_usuario_id}", response_model=GrupoUsuarioOut)
def obter(grupo_usuario_id: int, db: Session = Depends(get_db)):
    return crud_grupos_usuarios.get(db, grupo_usuario_id)


@router.post("/", response_model=GrupoUsuarioOut, status_code=201)
def criar(data: GrupoUsuarioCreate, db: Session = Depends(get_db)):
    return crud_grupos_usuarios.criar(db, data)


@router.put("/{grupo_usuario_id}", response_model=GrupoUsuarioOut)
def atualizar(grupo_usuario_id: int, data: GrupoUsuarioUpdate, db: Session = Depends(get_db)):
    return crud_grupos_usuarios.atualizar(db, grupo_usuario_id, data)


@router.delete("/{grupo_usuario_id}")
def deletar(grupo_usuario_id: int, db: Session = Depends(get_db)):
    return crud_grupos_usuarios.deletar(db, grupo_usuario_id)
