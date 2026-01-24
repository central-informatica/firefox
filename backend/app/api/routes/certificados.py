"""
Certificate routes - proxies to Cofre microservice.

Certificate operations (upload, list, sign) are delegated to the Cofre service (port 8002).
Business logic (access control, grupo membership) remains in XSecurity-Vault.
"""

import base64
import datetime
from typing import Any

from cryptography.hazmat.primitives.serialization import pkcs12
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.api.deps import check_auth, get_organization_id_from_data, get_user_id_from_data
from backend.app.core.exceptions import (
    CertificateNotFoundError,
    CertificateSigningError,
    CofreServiceError,
)
from backend.app.crud.guards import exigir_acesso_empresa
from backend.app.db.models import Certificados, GruposCertificados, GruposUsuarios
from backend.app.db.session import get_db
from backend.app.services.cofre_client import cofre_client

router = APIRouter(prefix="/certificados", tags=["Certificados"])


# -----------------------------------------------------------------------------
# Request/Response Models
# -----------------------------------------------------------------------------


class SignRequest(BaseModel):
    """Request to sign data with certificate."""

    data: str  # Base64-encoded data to sign


class CertificateResponse(BaseModel):
    """Certificate response."""

    certificado_id: str
    cofre_cert_id: str | None = None
    empresa_id: str
    nome_arquivo: str
    proprietario: str | None = None
    emitido_por: str | None = None
    validade_inicio: str | None = None
    valido_ate: str | None = None
    criado_em: str | None = None


class CertificateUploadResponse(BaseModel):
    """Response for certificate upload."""

    status: str
    message: str
    certificate_id: str
    owner: str | None = None
    issuer: str | None = None
    valid_from: str | None = None
    valid_until: str | None = None


class SignResponse(BaseModel):
    """Sign response."""

    signature: str  # Base64-encoded signature


# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------


def verificar_acesso_certificado(
    db: Session,
    usuario_id: str,
    certificado_id: str,
) -> Certificados:
    """
    Verify user has access to certificate via grupo membership.

    User must be member of a grupo that has access to this certificate.
    Soft-deleted certificates are excluded.

    Returns:
        Certificados object if access is granted

    Raises:
        HTTPException 404: If certificate not found or deleted
        HTTPException 403: If user doesn't have access
    """
    # Get certificate (exclude soft-deleted)
    certificado = (
        db.query(Certificados)
        .filter(
            Certificados.certificado_id == certificado_id,
            Certificados.deleted_at.is_(None),
        )
        .first()
    )

    if not certificado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certificado nao encontrado",
        )

    # Check if user has access via grupo
    # User must be in a grupo that has this certificate assigned
    has_access = (
        db.query(GruposCertificados)
        .join(
            GruposUsuarios,
            GruposUsuarios.grupo_id == GruposCertificados.grupo_id,
        )
        .filter(
            GruposCertificados.certificado_id == certificado_id,
            GruposUsuarios.usuario_id == usuario_id,
        )
        .first()
    )

    if not has_access:
        # Also check if user is empresa owner/member
        try:
            exigir_acesso_empresa(db, certificado.empresa_id, usuario_id)
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem acesso a este certificado",
            )

    return certificado


# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------


@router.post("/", response_model=CertificateUploadResponse)
async def upload_certificate(
    arquivo: UploadFile = File(...),
    senha: str = Form(...),
    db: Session = Depends(get_db),
    user_data: dict[str, Any] = Depends(check_auth),
) -> CertificateResponse:
    """
    Upload certificate to Cofre for encryption and storage.

    Admin only - uses organization_id from user data.
    """
    # 1. Check if user is admin
    if not user_data.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem fazer upload de certificados",
        )

    usuario_id = get_user_id_from_data(user_data)

    # 2. Use organization_id from user_data as empresa_id
    organization_id = get_organization_id_from_data(user_data)
    if not organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário não pertence a nenhuma organização",
        )

    empresa_id = organization_id

    # 3. Read file content
    file_content = await arquivo.read()
    if not file_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Arquivo vazio",
        )

    # 4. Validate PFX password
    try:
        pkcs12.load_key_and_certificates(file_content, senha.encode() if senha else None)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha do certificado inválida",
        )

    # 5. Send to Cofre for encryption
    try:
        cofre_result = await cofre_client.upload_certificate(
            arquivo=file_content,
            senha=senha,
            metadata={
                "nome_arquivo": arquivo.filename,
                "empresa_id": empresa_id,
                "criado_por": usuario_id,
            },
        )
    except CofreServiceError as e:
        raise HTTPException(
            status_code=e.status_code or 500,
            detail=e.message,
        )

    # 6. Store local reference
    # Note: encrypted and secret fields are now handled by Cofre
    # We store cofre_cert_id to reference the certificate in Cofre
    cert = Certificados(
        empresa_id=empresa_id,
        criado_por=usuario_id,
        nome_arquivo=arquivo.filename,
        # These fields will be deprecated but keep for backward compatibility
        encrypted="STORED_IN_COFRE",
        secret="STORED_IN_COFRE",
        # Metadata from Cofre (English field names) -> Database (Portuguese column names)
        proprietario=cofre_result.get("owner"),
        emitido_por=cofre_result.get("issuer"),
        validade_inicio=cofre_result.get("valid_from"),
        valido_ate=cofre_result.get("valid_until"),
        # Store Cofre certificate ID for signing/deletion operations
        cofre_cert_id=cofre_result.get("certificate_id"),
    )
    db.add(cert)
    db.commit()
    db.refresh(cert)

    return CertificateUploadResponse(
        status="ok",
        message=f"Certificate {arquivo.filename} uploaded successfully",
        certificate_id=str(cert.certificado_id),
        owner=cert.proprietario,
        issuer=cert.emitido_por,
        valid_from=str(cert.validade_inicio) if cert.validade_inicio else None,
        valid_until=str(cert.valido_ate) if cert.valido_ate else None,
    )


@router.get("/")
async def list_certificates(
    empresa_id: str | None = None,
    include_deleted: bool = False,
    db: Session = Depends(get_db),
    user_data: dict[str, Any] = Depends(check_auth),
) -> list[CertificateResponse]:
    """
    List certificates.

    If empresa_id is provided, lists certificates for that empresa.
    Otherwise, lists all certificates the user has access to.

    Args:
        include_deleted: If True, includes soft-deleted certificates in the results.
    """
    usuario_id = get_user_id_from_data(user_data)

    if empresa_id:
        # Verify access to empresa
        exigir_acesso_empresa(db, empresa_id, usuario_id)

        query = db.query(Certificados).filter(Certificados.empresa_id == empresa_id)
        if not include_deleted:
            query = query.filter(Certificados.deleted_at.is_(None))
        certs = query.all()
    else:
        # Get certificates from all empresas user has access to
        # This includes certificates via grupo membership
        query = (
            db.query(Certificados)
            .join(
                GruposCertificados,
                GruposCertificados.certificado_id == Certificados.certificado_id,
                isouter=True,
            )
            .join(
                GruposUsuarios,
                GruposUsuarios.grupo_id == GruposCertificados.grupo_id,
                isouter=True,
            )
            .filter(GruposUsuarios.usuario_id == usuario_id)
        )
        if not include_deleted:
            query = query.filter(Certificados.deleted_at.is_(None))
        certs = query.distinct().all()

    return [
        CertificateResponse(
            certificado_id=str(c.certificado_id),
            cofre_cert_id=str(c.cofre_cert_id) if c.cofre_cert_id else None,
            empresa_id=str(c.empresa_id),
            nome_arquivo=c.nome_arquivo,
            proprietario=c.proprietario,
            emitido_por=c.emitido_por,
            validade_inicio=str(c.validade_inicio) if c.validade_inicio else None,
            valido_ate=str(c.valido_ate) if c.valido_ate else None,
            criado_em=str(c.criado_em) if c.criado_em else None,
        )
        for c in certs
    ]


@router.get("/{certificado_id}")
async def get_certificate(
    certificado_id: str,
    db: Session = Depends(get_db),
    user_data: dict[str, Any] = Depends(check_auth),
) -> CertificateResponse:
    """
    Get specific certificate by ID.
    """
    usuario_id = get_user_id_from_data(user_data)

    cert = verificar_acesso_certificado(db, usuario_id, certificado_id)

    return CertificateResponse(
        certificado_id=str(cert.certificado_id),
        cofre_cert_id=str(cert.cofre_cert_id) if cert.cofre_cert_id else None,
        empresa_id=str(cert.empresa_id),
        nome_arquivo=cert.nome_arquivo,
        proprietario=cert.proprietario,
        emitido_por=cert.emitido_por,
        validade_inicio=str(cert.validade_inicio) if cert.validade_inicio else None,
        valido_ate=str(cert.valido_ate) if cert.valido_ate else None,
        criado_em=str(cert.criado_em) if cert.criado_em else None,
    )


@router.post("/{certificado_id}/assinar", response_model=SignResponse)
async def sign_with_certificate(
    certificado_id: str,
    data: SignRequest,
    db: Session = Depends(get_db),
    user_data: dict[str, Any] = Depends(check_auth),
) -> SignResponse:
    """
    Sign data using certificate.

    Steps:
    1. Verify user has access to certificate via grupo
    2. Check access rules (regras_acesso) - TODO
    3. Send to Cofre for signing
    """
    usuario_id = get_user_id_from_data(user_data)

    # 1. Verify certificate access
    cert = verificar_acesso_certificado(db, usuario_id, certificado_id)

    # 2. TODO: Check access rules (regras_acesso, horarios, feriados)
    # This business logic remains in XSecurity-Vault

    # 3. Decode base64 data
    try:
        raw_data = base64.b64decode(data.data)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dados invalidos (esperado base64)",
        )

    # 4. Send to Cofre for signing
    if not cert.cofre_cert_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Certificado nao possui ID do Cofre associado",
        )

    try:
        signature = await cofre_client.sign_data(
            certificate_id=cert.cofre_cert_id,
            data=raw_data,
            user_context={
                "usuario_id": usuario_id,
                "empresa_id": str(cert.empresa_id),
            },
        )

        return SignResponse(signature=signature)

    except CertificateNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certificado nao encontrado no cofre",
        )
    except CertificateSigningError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.message,
        )
    except CofreServiceError as e:
        raise HTTPException(
            status_code=e.status_code or 500,
            detail=e.message,
        )


@router.delete("/{certificado_id}")
async def delete_certificate(
    certificado_id: str,
    db: Session = Depends(get_db),
    user_data: dict[str, Any] = Depends(check_auth),
) -> dict[str, str]:
    """
    Soft delete certificate.

    Marks the certificate as deleted without removing data from the database or Cofre.
    """
    usuario_id = get_user_id_from_data(user_data)

    # Get certificate (exclude already deleted)
    cert = (
        db.query(Certificados)
        .filter(
            Certificados.certificado_id == certificado_id,
            Certificados.deleted_at.is_(None),
        )
        .first()
    )

    if not cert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certificado nao encontrado",
        )

    # Verify user is empresa owner/member
    exigir_acesso_empresa(db, cert.empresa_id, usuario_id)

    # Soft delete: set deleted_at and deleted_by
    cert.deleted_at = datetime.datetime.now(datetime.timezone.utc)
    cert.deleted_by = usuario_id
    db.commit()

    return {"message": "Certificado removido com sucesso"}
