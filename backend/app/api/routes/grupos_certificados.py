from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.api.deps import check_auth_with_ip
from backend.app.db.session import get_db
from backend.app.db.models import Certificados, Grupos, GruposCertificados
from backend.app.schemas.grupos_certificados import (
    GrupoCertCreate,
    GrupoCertUpdate,
    GrupoCertOut,
)
from backend.app.crud.grupos_certificados import crud_grupos_certificados


router = APIRouter(prefix="/grupos-certificados", tags=["Grupos Certificados"])


@router.get("/", response_model=list[GrupoCertOut])
def listar(db: Session = Depends(get_db), current_user=Depends(check_auth_with_ip)):
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Apenas administradores podem listar grupos-certificados")
    return crud_grupos_certificados.listar(db)


@router.get("/empresa/{empresa_id}/detalhado")
def listar_detalhado_por_empresa(
    empresa_id: str,
    page: int = 1,
    limit: int = 10,
    search: str = "",
    db: Session = Depends(get_db),
    current_user: dict[str, Any] = Depends(check_auth_with_ip),
):
    """List certificate-group associations with detailed info for a specific empresa."""
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Apenas administradores podem listar grupos-certificados")

    # Query with joins to get detailed info
    query = (
        db.query(
            GruposCertificados.grupo_cert_id,
            GruposCertificados.grupo_id,
            GruposCertificados.certificado_id,
            GruposCertificados.empresa_id,
            Grupos.nome.label("grupo_nome"),
            Certificados.nome_arquivo.label("certificado_nome"),
            Certificados.proprietario.label("certificado_proprietario"),
            Certificados.valido_ate.label("certificado_valido_ate"),
            Certificados.validade_inicio.label("certificado_validade_inicio"),
        )
        .join(Grupos, Grupos.grupo_id == GruposCertificados.grupo_id)
        .join(Certificados, Certificados.certificado_id == GruposCertificados.certificado_id)
        .filter(
            GruposCertificados.empresa_id == empresa_id,
            Certificados.deleted_at.is_(None),
        )
    )

    # Apply search filter
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            Grupos.nome.ilike(search_term) |
            Certificados.nome_arquivo.ilike(search_term) |
            Certificados.proprietario.ilike(search_term)
        )

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (page - 1) * limit
    results = query.offset(offset).limit(limit).all()

    # Format response
    data = [
        {
            "grupo_cert_id": str(r.grupo_cert_id),
            "grupo_id": str(r.grupo_id),
            "certificado_id": str(r.certificado_id),
            "empresa_id": str(r.empresa_id),
            "grupo_nome": r.grupo_nome,
            "certificado_nome": r.certificado_nome,
            "certificado_proprietario": r.certificado_proprietario,
            "certificado_valido_ate": str(r.certificado_valido_ate) if r.certificado_valido_ate else None,
            "certificado_validade_inicio": str(r.certificado_validade_inicio) if r.certificado_validade_inicio else None,
        }
        for r in results
    ]

    return {
        "data": data,
        "total": total,
        "page": page,
        "limit": limit,
    }


@router.get("/grupo/{grupo_id}", response_model=list[GrupoCertOut])
def listar_grupo(grupo_id: str, db: Session = Depends(get_db), current_user=Depends(check_auth_with_ip)):
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Apenas administradores podem listar grupos-certificados")
    return crud_grupos_certificados.listar_por_grupo(db, grupo_id)


@router.get("/{grupo_cert_id}", response_model=GrupoCertOut)
def obter(grupo_cert_id: str, db: Session = Depends(get_db), current_user=Depends(check_auth_with_ip)):
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Apenas administradores podem visualizar grupos-certificados")
    return crud_grupos_certificados.get(db, grupo_cert_id)


@router.post("/", response_model=GrupoCertOut, status_code=201)
def criar(data: GrupoCertCreate, db: Session = Depends(get_db), current_user=Depends(check_auth_with_ip)):
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Apenas administradores podem criar grupos-certificados")
    return crud_grupos_certificados.criar(db, data)


@router.put("/{grupo_cert_id}", response_model=GrupoCertOut)
def atualizar(grupo_cert_id: str, data: GrupoCertUpdate, db: Session = Depends(get_db), current_user=Depends(check_auth_with_ip)):
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Apenas administradores podem atualizar grupos-certificados")
    return crud_grupos_certificados.atualizar(db, grupo_cert_id, data)


@router.delete("/{grupo_cert_id}")
def deletar(grupo_cert_id: str, db: Session = Depends(get_db), current_user=Depends(check_auth_with_ip)):
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Apenas administradores podem deletar grupos-certificados")
    return crud_grupos_certificados.deletar(db, grupo_cert_id)
