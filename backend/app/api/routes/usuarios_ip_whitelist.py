"""
API routes for UsuariosIpWhitelist.

Manages IP address whitelist entries per user per empresa.
Admin-only endpoints for configuring allowed IPs.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.api.deps import check_auth_with_ip, get_user_id_from_data, get_organization_id_from_data,check_auth
from backend.app.db.session import get_db
from backend.app.schemas.usuarios_ip_whitelist import (
    UsuarioIpWhitelistCreate,
    UsuarioIpWhitelistUpdate,
    UsuarioIpWhitelistOut,
)
from backend.app.crud.usuarios_ip_whitelist import crud_usuarios_ip_whitelist


router = APIRouter(prefix="/usuarios-ip-whitelist", tags=["IP Whitelist"])


def _verificar_admin(current_user: dict):
    """Verify user is admin, raise 403 if not."""
    if not current_user.get("is_admin"):
        raise HTTPException(403, "Apenas administradores podem gerenciar IPs")


@router.get("/empresa/{empresa_id}", response_model=list[UsuarioIpWhitelistOut])
def listar_por_empresa(
    empresa_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(check_auth_with_ip)
):
    """List all IP whitelist entries for an empresa (admin only)."""
    _verificar_admin(current_user)
    return crud_usuarios_ip_whitelist.listar_por_empresa(db, empresa_id)


@router.get("/usuario/{usuario_id}", response_model=list[UsuarioIpWhitelistOut])
def listar_por_usuario(
    usuario_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(check_auth_with_ip)
):
    """List all IP whitelist entries for a specific user in the current empresa."""
    _verificar_admin(current_user)
    empresa_id = get_organization_id_from_data(current_user)
    if not empresa_id:
        raise HTTPException(400, "Usuario nao esta associado a uma empresa")
    return crud_usuarios_ip_whitelist.listar_por_usuario(db, usuario_id, empresa_id)


@router.get("/{whitelist_id}", response_model=UsuarioIpWhitelistOut)
def obter(
    whitelist_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(check_auth_with_ip)
):
    """Get a specific IP whitelist entry."""
    _verificar_admin(current_user)
    return crud_usuarios_ip_whitelist.get(db, whitelist_id)


@router.post("/", response_model=UsuarioIpWhitelistOut, status_code=201)
def criar(
    data: UsuarioIpWhitelistCreate,
    db: Session = Depends(get_db),
    current_user=Depends(check_auth)
):
    """Create a new IP whitelist entry (admin only)."""
    _verificar_admin(current_user)
    criado_por = get_user_id_from_data(current_user)
    return crud_usuarios_ip_whitelist.criar(db, data, criado_por)


@router.put("/{whitelist_id}", response_model=UsuarioIpWhitelistOut)
def atualizar(
    whitelist_id: str,
    data: UsuarioIpWhitelistUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(check_auth_with_ip)
):
    """Update an IP whitelist entry (admin only)."""
    _verificar_admin(current_user)
    return crud_usuarios_ip_whitelist.atualizar(db, whitelist_id, data)


@router.delete("/{whitelist_id}")
def deletar(
    whitelist_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(check_auth_with_ip)
):
    """Delete an IP whitelist entry (admin only). Soft delete."""
    _verificar_admin(current_user)
    deleted_by = get_user_id_from_data(current_user)
    return crud_usuarios_ip_whitelist.deletar(db, whitelist_id, deleted_by)


@router.delete("/usuario/{usuario_id}")
def deletar_todos_por_usuario(
    usuario_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(check_auth_with_ip)
):
    """Delete all IP whitelist entries for a user (admin only). Soft delete."""
    _verificar_admin(current_user)
    empresa_id = get_organization_id_from_data(current_user)
    if not empresa_id:
        raise HTTPException(400, "Usuario nao esta associado a uma empresa")
    deleted_by = get_user_id_from_data(current_user)
    return crud_usuarios_ip_whitelist.deletar_todos_por_usuario(db, usuario_id, empresa_id, deleted_by)
