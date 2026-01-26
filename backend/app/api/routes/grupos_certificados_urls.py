"""API routes for GruposCertificadosUrls.

Manages URL associations for grupo-certificado relationships.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.api.deps import check_auth_with_ip, get_organization_id_from_data
from backend.app.db.session import get_db
from backend.app.schemas.grupos_certificados_urls import (
    GrupoCertUrlCreate,
    GrupoCertUrlOut,
)
from backend.app.crud.grupos_certificados_urls import crud_grupos_certificados_urls


router = APIRouter(prefix="/grupos-certificados", tags=["Grupos Certificados URLs"])


@router.get("/{grupo_cert_id}/urls", response_model=list[GrupoCertUrlOut])
def listar_urls(
    grupo_cert_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(check_auth_with_ip)
):
    """List all URLs associated with a grupo-certificado."""
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Apenas administradores podem listar URLs de grupos-certificados")
    return crud_grupos_certificados_urls.listar_por_grupo_cert(db, str(grupo_cert_id))


@router.post("/{grupo_cert_id}/urls", response_model=GrupoCertUrlOut, status_code=201)
def adicionar_url(
    grupo_cert_id: UUID,
    data: GrupoCertUrlCreate,
    db: Session = Depends(get_db),
    current_user=Depends(check_auth_with_ip)
):
    """Add a URL to a grupo-certificado."""
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Apenas administradores podem adicionar URLs a grupos-certificados")
    empresa_id = get_organization_id_from_data(current_user)
    if not empresa_id:
        raise HTTPException(400, "Usuario nao esta associado a uma empresa")
    return crud_grupos_certificados_urls.criar(db, str(grupo_cert_id), data, empresa_id)


@router.delete("-urls/{grupo_cert_url_id}")
def remover_url(
    grupo_cert_url_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(check_auth_with_ip)
):
    """Remove a URL from a grupo-certificado."""
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Apenas administradores podem remover URLs de grupos-certificados")
    return crud_grupos_certificados_urls.deletar(db, str(grupo_cert_url_id))
