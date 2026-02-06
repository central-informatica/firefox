from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.api.deps import check_auth_with_ip
from backend.app.schemas.planos_trabalho import (
    PlanoTrabalhoCreate, PlanoTrabalhoUpdate, PlanoTrabalhoOut, PlanoTrabalhoPage
)
from backend.app.crud.planos_trabalho import crud_planos_trabalho
from backend.app.core.uuid_validator import validate_uuid

router = APIRouter(prefix="/planos-trabalho", tags=["Planos de Trabalho"])


def _verificar_admin(current_user: dict):
    """Verify user is admin, raise 403 if not."""
    if not current_user.get("is_admin"):
        raise HTTPException(403, "Apenas administradores podem gerenciar planos de trabalho")


@router.get("/")
def listar_planos_trabalho(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: str | None = None,
    sort: str | None = None,
    empresa_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user = Depends(check_auth_with_ip),
):
    _verificar_admin(current_user)
    if empresa_id is None:
        empresa_id = current_user["organization_id"]

    items, total = crud_planos_trabalho.listar(
        db=db,
        empresa_id=empresa_id,
        page=page,
        limit=limit,
        search=search,
        sort=sort,
    )

    return {
        "items": items,
        "total": total,
    }

@router.get("/{plano_id}", response_model=PlanoTrabalhoOut)
def getPlanoTrabalho(
    plano_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(check_auth_with_ip),
):
    _verificar_admin(current_user)
    plano_id = validate_uuid(plano_id, "plano_id")
    usuario_id = current_user["id"]
    return crud_planos_trabalho.getPlanoTrabalho(db, usuario_id=usuario_id, plano_id=plano_id)


@router.post("/", status_code=201)
def criar_plano_trabalho(
    data: PlanoTrabalhoCreate,
    db: Session = Depends(get_db),
    current_user = Depends(check_auth_with_ip),
):
    _verificar_admin(current_user)

    # Usa empresa_id do payload (selecionada pelo usuário)
    empresa_id = data.empresa_id
    if not empresa_id:
        raise HTTPException(
            status_code=400,
            detail="empresa_id é obrigatório"
        )

    return crud_planos_trabalho.criar(
        db=db,
        data=data,
        empresa_id=str(empresa_id),
        usuario_id=current_user["id"],
    )


@router.put("/{plano_id}", response_model=PlanoTrabalhoOut)
def atualizar_plano_trabalho(
    plano_id: str,
    data: PlanoTrabalhoUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(check_auth_with_ip),
):
    _verificar_admin(current_user)
    plano_id = validate_uuid(plano_id, "plano_id")
    usuario_id = current_user["id"]
    return crud_planos_trabalho.atualizar(db, usuario_id=usuario_id, plano_id=plano_id, data=data)


@router.delete("/{plano_id}")
def deletar_plano_trabalho(
    plano_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(check_auth_with_ip),
):
    _verificar_admin(current_user)
    plano_id = validate_uuid(plano_id, "plano_id")
    usuario_id = current_user["id"]
    crud_planos_trabalho.deletar(db, usuario_id=usuario_id, plano_id=plano_id)
    return {"ok": True}
