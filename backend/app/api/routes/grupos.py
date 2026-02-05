"""API routes for Grupos.

Manages grupos (user groups) within planos de trabalho.
Admin-only for write operations.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.api.deps import check_auth_with_ip
from backend.app.db.session import get_db
from backend.app.schemas.grupos import (
    GrupoCreate,
    GrupoUpdate,
    GrupoOut,
    GrupoCertificadoAdd,
    GrupoCertificadoRemove,
    GrupoUsuarioAdd,
)
from backend.app.crud.grupos import (
    listar_grupos_por_empresa,
    listar_certificados_do_grupo,
    get_grupo,
    criar_grupo,
    atualizar_grupo,
    deletar_grupo,
    adicionar_certificado_ao_grupo,
    remover_certificado_do_grupo,
)
from backend.app.crud.grupos_usuarios import crud_grupos_usuarios
from backend.app.schemas.grupos_usuarios import GrupoUsuarioCreate, GrupoUsuarioBulkCreate


router = APIRouter(prefix="/grupos", tags=["Grupos"])


def _verificar_admin(current_user: dict):
    """Verify user is admin, raise 403 if not."""
    if not current_user.get("is_admin"):
        raise HTTPException(403, "Apenas administradores podem gerenciar grupos")


# ---------------------------------------------------------------------------
# Grupos CRUD
# ---------------------------------------------------------------------------

@router.get("/empresa/{empresa_id}", response_model=list[GrupoOut])
def listar_grupos_empresa(
    empresa_id: str,
    plano_id: str | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(check_auth_with_ip),
):
    """List grupos by empresa (optionally filtered by plano)."""
    _verificar_admin(current_user)
    usuario_id = current_user.get("id") or current_user.get("usuario_id")
    return listar_grupos_por_empresa(
        db=db,
        empresa_id=empresa_id,
        usuario_id=usuario_id,
        plano_id=plano_id,
    )


@router.get("/{grupo_id}", response_model=GrupoOut)
def obter(
    grupo_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(check_auth_with_ip),
):
    """Get a specific grupo by ID."""
    _verificar_admin(current_user)
    grupo = get_grupo(db, grupo_id)
    if not grupo:
        raise HTTPException(status_code=404, detail="Grupo nao encontrado")
    return grupo


@router.post("/", response_model=GrupoOut, status_code=201)
def criar(
    data: GrupoCreate,
    db: Session = Depends(get_db),
    current_user=Depends(check_auth_with_ip),
):
    """Create a new grupo (admin only)."""
    _verificar_admin(current_user)
    return criar_grupo(db, data.model_dump())


@router.put("/{grupo_id}", response_model=GrupoOut)
def atualizar(
    grupo_id: str,
    data: GrupoUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(check_auth_with_ip),
):
    """Update a grupo (admin only)."""
    _verificar_admin(current_user)
    grupo = get_grupo(db, grupo_id)
    if not grupo:
        raise HTTPException(status_code=404, detail="Grupo nao encontrado")

    usuario_id = current_user.get("id") or current_user.get("usuario_id")
    return atualizar_grupo(
        db=db,
        grupo_id=grupo_id,
        empresa_id=str(grupo.empresa_id),
        usuario_id=usuario_id,
        dados=data.model_dump(exclude_unset=True)
    )


@router.delete("/{grupo_id}")
def remover(
    grupo_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(check_auth_with_ip),
):
    """Delete a grupo (admin only)."""
    _verificar_admin(current_user)
    sucesso = deletar_grupo(db, grupo_id)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Grupo nao encontrado")
    return {"detail": "Grupo removido com sucesso"}


# ---------------------------------------------------------------------------
# Grupos <-> Certificados
# ---------------------------------------------------------------------------

@router.get("/{grupo_id}/certificados")
def listar_certificados_grupo(
    grupo_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(check_auth_with_ip),
):
    """List certificados associated with a grupo."""
    _verificar_admin(current_user)
    return listar_certificados_do_grupo(db=db, grupo_id=grupo_id)


@router.post("/{grupo_id}/certificados", status_code=201)
def adicionar_certificado(
    grupo_id: str,
    data: GrupoCertificadoAdd,
    db: Session = Depends(get_db),
    current_user=Depends(check_auth_with_ip),
):
    """Add a certificado to a grupo (admin only)."""
    _verificar_admin(current_user)
    return adicionar_certificado_ao_grupo(
        db=db,
        grupo_id=grupo_id,
        certificado_id=data.certificado_id,
        empresa_id=data.empresa_id,
    )


@router.delete("/{grupo_id}/certificados")
def remover_certificado(
    grupo_id: str,
    data: GrupoCertificadoRemove,
    db: Session = Depends(get_db),
    current_user=Depends(check_auth_with_ip),
):
    """Remove a certificado from a grupo (admin only)."""
    _verificar_admin(current_user)
    ok = remover_certificado_do_grupo(
        db=db,
        grupo_id=grupo_id,
        certificado_id=data.certificado_id,
        empresa_id=data.empresa_id
    )
    if not ok:
        raise HTTPException(status_code=404, detail="Vinculo nao encontrado")
    return {"success": True}


# ---------------------------------------------------------------------------
# Grupos <-> Usuarios
# ---------------------------------------------------------------------------

@router.get("/{grupo_id}/usuarios")
def listar_usuarios_do_grupo(
    grupo_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(check_auth_with_ip),
):
    """List usuarios in a grupo."""
    _verificar_admin(current_user)
    registros = crud_grupos_usuarios.listar_por_grupo(db, grupo_id)
    usuarios = []
    for r in registros:
        usuarios.append({
            "grupo_usuario_id": str(r.grupo_usuario_id),
            "usuario_id": str(r.usuario_id),
            "empresa_id": str(r.empresa_id) if r.empresa_id else None,
        })
    return usuarios


@router.post("/{grupo_id}/usuarios", status_code=201)
def adicionar_usuario_ao_grupo(
    grupo_id: str,
    data: GrupoUsuarioAdd,
    db: Session = Depends(get_db),
    current_user=Depends(check_auth_with_ip),
):
    """Add a usuario to a grupo (admin only)."""
    _verificar_admin(current_user)

    grupo = get_grupo(db, grupo_id)
    if not grupo:
        raise HTTPException(status_code=404, detail="Grupo nao encontrado")

    create_data = GrupoUsuarioCreate(
        empresa_id=data.empresa_id,
        grupo_id=grupo_id,
        usuario_id=data.usuario_id
    )
    return crud_grupos_usuarios.criar(db, create_data)


@router.delete("/{grupo_id}/usuarios/{usuario_id}")
def remover_usuario_do_grupo(
    grupo_id: str,
    usuario_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(check_auth_with_ip),
):
    """Remove a usuario from a grupo (admin only)."""
    _verificar_admin(current_user)
    registros = crud_grupos_usuarios.listar_por_grupo(db, grupo_id)
    target = None
    for r in registros:
        if str(r.usuario_id) == usuario_id:
            target = r
            break
    if not target:
        raise HTTPException(status_code=404, detail="Vinculo nao encontrado")
    return crud_grupos_usuarios.deletar(db, target.grupo_usuario_id)


@router.post("/{grupo_id}/usuarios/bulk")
def adicionar_usuarios_em_lote(
    grupo_id: str,
    payload: GrupoUsuarioBulkCreate,
    db: Session = Depends(get_db),
    current_user=Depends(check_auth_with_ip),
):
    """Add multiple usuarios to a grupo (admin only)."""
    _verificar_admin(current_user)

    grupo = get_grupo(db, grupo_id)
    if not grupo:
        raise HTTPException(status_code=404, detail="Grupo nao encontrado")

    return crud_grupos_usuarios.criar_bulk(db, grupo_id, payload.usuario_ids, payload.empresa_id)
