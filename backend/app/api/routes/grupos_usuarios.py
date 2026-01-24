from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.grupos_usuarios import (
    GrupoUsuarioCreate,
    GrupoUsuarioUpdate,
    GrupoUsuarioOut,
    GrupoUsuarioBulkCreate,
    GrupoUsuarioBulkResult,
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


@router.post("/bulk", response_model=GrupoUsuarioBulkResult)
def criar_bulk(payload: GrupoUsuarioBulkCreate, db: Session = Depends(get_db)):
    """Cria vínculos em lote entre um grupo e múltiplos usuários. Retorna os ids criados e os pulados com razão."""
    resumo = crud_grupos_usuarios.criar_bulk(db, payload.grupo_id, payload.usuario_ids, payload.empresa_id)
    return resumo


@router.put("/{grupo_usuario_id}", response_model=GrupoUsuarioOut)
def atualizar(grupo_usuario_id: int, data: GrupoUsuarioUpdate, db: Session = Depends(get_db)):
    return crud_grupos_usuarios.atualizar(db, grupo_usuario_id, data)


@router.delete("/{grupo_usuario_id}")
def deletar(grupo_usuario_id: int, db: Session = Depends(get_db)):
    return crud_grupos_usuarios.deletar(db, grupo_usuario_id)
