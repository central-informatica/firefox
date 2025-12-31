from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from backend.app.api.deps import get_current_user
from backend.app.db.session import get_db
from backend.app.crud.usuarios import (
    listar_empresas_do_usuario,
    listar_usuarios_empresa_paginado,
    get_usuario,
    criar_usuario,
    atualizar_usuario,
    deletar_usuario,
)
from backend.app.db.models import Usuarios
from backend.app.schemas.usuarios import (
    UsuarioCreate,
    UsuarioUpdate,
    UsuarioOut,
    EmpresaDoUsuarioOut,
    UsuariosPaginadoOut
)

router = APIRouter(prefix="/usuarios", tags=["Usuários"])

@router.get("/{usuario_id}", response_model=UsuarioOut)
def obter_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = get_usuario(db, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario

# Lista as empresas do usuário
@router.get("/{user_id}/empresas", response_model=list[EmpresaDoUsuarioOut])
def get_empresas_usuario(user_id: int, db: Session = Depends(get_db)):
    empresas = listar_empresas_do_usuario(db, user_id)

    # Mantém o mesmo formato que você já retornava antes
    return [
        EmpresaDoUsuarioOut(
            empresa_id=e.empresa_id,
            razao_social=e.razao_social,
            fantasia=e.fantasia,
            cnpj=e.cnpj,
            timezone=e.timezone,
        )
        for e in empresas
    ]

# Lista usuários por Empresa
@router.get(
    "/empresas/{empresa_id}/usuarios",
    response_model=UsuariosPaginadoOut, description="Lista os usuários por empresa"
)
def listar_usuarios_empresa(
    empresa_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: str = Query("", min_length=0),
    sort: str = Query("", min_length=0),
    db: Session = Depends(get_db),
):
    return listar_usuarios_empresa_paginado(
        db=db,
        empresa_id=empresa_id,
        page=page,
        limit=limit,
        search=search,
        sort=sort,
    )

@router.post("/", response_model=UsuarioOut, status_code=201)
def criar_novo_usuario(payload: UsuarioCreate, db: Session = Depends(get_db)):
    # Passamos um dict pro CRUD existente, mantendo compatibilidade
    dados = payload.dict()
    return criar_usuario(db, dados)


@router.put("/{usuario_id}", response_model=UsuarioOut)
def atualizar_usuario_route(
    usuario_id: int,
    payload: UsuarioUpdate,
    empresa_id: Optional[int] = Query(None, ge=1),
    db: Session = Depends(get_db),
    usuario_logado: Usuarios = Depends(get_current_user),
):
    dados = payload.dict(exclude_unset=True)
    usuario = atualizar_usuario(db, empresa_id, usuario_id, dados, usuario_logado)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario


@router.delete("/{usuario_id}")
def remover_usuario(usuario_id: int, db: Session = Depends(get_db)):
    sucesso = deletar_usuario(db, usuario_id)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return {"detail": "Usuário removido com sucesso"}
