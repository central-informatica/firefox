from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.crud.usuarios import (
    listar_empresas_do_usuario,
    get_usuario,
    criar_usuario,
    atualizar_usuario,
    deletar_usuario,
)
from backend.app.schemas.usuarios import (
    UsuarioCreate,
    UsuarioUpdate,
    UsuarioOut,
    EmpresaDoUsuarioOut,
)

router = APIRouter(prefix="/usuarios", tags=["Usuários"])


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


@router.get("/{usuario_id}", response_model=UsuarioOut)
def obter_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = get_usuario(db, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario


@router.post("/", response_model=UsuarioOut, status_code=201)
def criar_novo_usuario(payload: UsuarioCreate, db: Session = Depends(get_db)):
    # Passamos um dict pro CRUD existente, mantendo compatibilidade
    dados = payload.dict()
    return criar_usuario(db, dados)


@router.put("/{usuario_id}", response_model=UsuarioOut)
def atualizar_usuario_route(
    usuario_id: int,
    payload: UsuarioUpdate,
    db: Session = Depends(get_db),
):
    dados = payload.dict(exclude_unset=True)
    usuario = atualizar_usuario(db, usuario_id, dados)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario


@router.delete("/{usuario_id}")
def remover_usuario(usuario_id: int, db: Session = Depends(get_db)):
    sucesso = deletar_usuario(db, usuario_id)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return {"detail": "Usuário removido com sucesso"}
