"""
Certificate routes - proxies to Cofre microservice.

Certificate operations (upload, list, sign) are delegated to the Cofre service (port 8002).
Business logic (access control, grupo membership) remains in XSecurity-Vault.
"""

import base64
import datetime
import uuid
from typing import Any

from cryptography.hazmat.primitives.serialization import pkcs12
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.api.deps import check_auth, check_auth_with_ip, get_organization_id_from_data, get_user_id_from_data
from backend.app.core.exceptions import (
    CertificateNotFoundError,
    CertificateSigningError,
    CofreServiceError,
)
from backend.app.crud.guards import exigir_acesso_empresa
from backend.app.db.models import Certificados, Feriados, GlobalUrls, GruposCertificados, GruposCertificadosUrls, GruposUsuarios, RegrasAcesso
from backend.app.db.session import get_db
from backend.app.services.cofre_client import cofre_client

router = APIRouter(prefix="/certificados", tags=["Certificados"])

# Maximum certificate file size (10 MB)
# PFX/P12 certificates are typically under 10KB, but may include full chains
MAX_CERT_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


# -----------------------------------------------------------------------------
# Request/Response Models
# -----------------------------------------------------------------------------


class SignRequest(BaseModel):
    """Request to sign data with certificate."""

    data: str  # Base64-encoded data to sign
    url: str   # URL where the certificate will be used (must be in allowed list)


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


class CertificateDerItem(BaseModel):
    """Single certificate DER data item."""

    id: str  # Local certificado_id (mapped from cofre)
    label: str
    cert_der_b64: str


class CertificateDerError(BaseModel):
    """Error info for certificates that failed access control."""

    id: str  # Local certificado_id
    reason: str  # Failure reason


class CertificateDerResponse(BaseModel):
    """Response with certificates and errors."""

    certificates: list[CertificateDerItem]
    errors: list[CertificateDerError]


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


def _is_feriado_hoje(db: Session, empresa_id: str, today) -> bool:
    """
    Check if today is a holiday for the given empresa.

    Handles both exact date matches and recurring holidays (same month/day).
    """
    from sqlalchemy import extract

    # Check exact date match (non-recurrent)
    feriado_exato = db.query(Feriados).filter(
        Feriados.empresa_id == empresa_id,
        Feriados.data == today,
        Feriados.recorrente == False
    ).first()

    if feriado_exato:
        return True

    # Check recurrent holidays (same month and day, any year)
    feriado_recorrente = db.query(Feriados).filter(
        Feriados.empresa_id == empresa_id,
        Feriados.recorrente == True,
        extract('month', Feriados.data) == today.month,
        extract('day', Feriados.data) == today.day
    ).first()

    return feriado_recorrente is not None


def _regra_permite_acesso(
    regra: RegrasAcesso,
    weekday: int,
    current_time,
    today,
    db: Session,
    empresa_id: str
) -> bool:
    """
    Check if a single access rule allows access at the current day/time.

    Args:
        regra: The access rule to check
        weekday: Current day of week (1=Monday, 7=Sunday)
        current_time: Current time
        today: Current date
        db: Database session
        empresa_id: Company ID for holiday check

    Returns:
        True if this rule allows access, False otherwise
    """
    # Check tipo_dia (day type)
    tipo_dia = regra.tipo_dia
    if hasattr(tipo_dia, 'value'):
        tipo_dia = tipo_dia.value

    if tipo_dia == "corridos":
        dia_ok = True
    elif tipo_dia == "uteis":
        dia_ok = weekday <= 5  # Monday-Friday
    elif tipo_dia == "especificos":
        dia_ok = weekday in (regra.dias_especificos or [])
    else:
        dia_ok = False

    if not dia_ok:
        return False

    # Check horarios (time windows)
    horario_ok = False
    for janela in regra.horarios:
        inicio = datetime.datetime.strptime(janela["inicio"], "%H:%M").time()
        fim = datetime.datetime.strptime(janela["fim"], "%H:%M").time()
        if inicio <= current_time <= fim:
            horario_ok = True
            break

    if not horario_ok:
        return False

    # Check feriado (holiday blocking)
    if regra.bloquear_em_feriado:
        if _is_feriado_hoje(db, empresa_id, today):
            return False

    return True


def verificar_regras_acesso(
    db: Session,
    usuario_id: str,
    certificado_id: str,
    empresa_id: str
) -> bool:
    """
    Verify if the user can access the certificate based on access rules.

    Checks:
    - Access rules (regras_acesso) for the user's grupos
    - Current day (tipo_dia, dias_especificos)
    - Current time (horarios)
    - Holidays (feriados + bloquear_em_feriado)

    Returns:
        True if access is allowed

    Raises:
        HTTPException 403: If access is denied
    """
    now = datetime.datetime.now()
    current_weekday = now.isoweekday()  # 1=Monday, 7=Sunday
    current_time = now.time()
    today = now.date()

    # 1. Get grupos the user belongs to that have access to this certificate
    grupo_certs = (
        db.query(GruposCertificados)
        .join(GruposUsuarios, GruposUsuarios.grupo_id == GruposCertificados.grupo_id)
        .filter(
            GruposCertificados.certificado_id == certificado_id,
            GruposUsuarios.usuario_id == usuario_id,
        )
        .all()
    )

    if not grupo_certs:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario nao tem acesso a este certificado via grupo",
        )

    grupo_ids = [gc.grupo_id for gc in grupo_certs]

    # 2. Get regras_acesso for these grupos
    regras = db.query(RegrasAcesso).filter(
        RegrasAcesso.grupo_id.in_(grupo_ids)
    ).all()

    if not regras:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: nenhuma regra de acesso definida para os grupos do usuario. Solicite ao administrador que configure as regras de acesso.",
        )

    # 3. Check if ANY rule allows access
    for regra in regras:
        if _regra_permite_acesso(regra, current_weekday, current_time, today, db, empresa_id):
            return True

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Acesso negado: fora do horario ou dia permitido",
    )


def _normalize_domain(domain: str) -> str:
    """
    Normalize a domain name to prevent homograph attacks.

    Uses IDNA encoding to convert Unicode domains to ASCII (Punycode),
    which ensures consistent comparison regardless of Unicode representation.

    Examples:
    - "example.com" -> "example.com"
    - "exаmple.com" (Cyrillic 'а') -> "xn--exmple-4uf.com"
    """
    try:
        # Encode to IDNA (Punycode) for Unicode normalization
        # This converts Unicode homoglyphs to their ASCII representation
        return domain.encode('idna').decode('ascii').lower()
    except (UnicodeError, UnicodeDecodeError):
        # If encoding fails, fall back to lowercase
        return domain.lower()


def verificar_url_permitida(
    db: Session,
    usuario_id: str,
    certificado_id: str,
    url: str
) -> bool:
    """
    Verify if the URL is allowed for the user's grupo-certificado relationship.

    Matching rules:
    - Request URL must be HTTPS
    - Only the domain is compared (not the full path)
    - Allowed URLs in database must also be HTTPS
    - Domains are normalized using IDNA encoding to prevent homograph attacks

    Returns:
        True if URL is allowed

    Raises:
        HTTPException 403: If URL is not allowed
    """
    from urllib.parse import urlparse

    # Parse the request URL
    parsed_url = urlparse(url)

    # Check if HTTPS
    if parsed_url.scheme != "https":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: apenas URLs HTTPS sao permitidas"
        )

    # Normalize the request domain using IDNA encoding to prevent homograph attacks
    request_domain = _normalize_domain(parsed_url.netloc)

    # Get grupo_cert entries for this user and certificate
    grupo_certs = (
        db.query(GruposCertificados)
        .join(GruposUsuarios, GruposUsuarios.grupo_id == GruposCertificados.grupo_id)
        .filter(
            GruposCertificados.certificado_id == certificado_id,
            GruposUsuarios.usuario_id == usuario_id,
        )
        .all()
    )

    if not grupo_certs:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario nao tem acesso a este certificado via grupo"
        )

    grupo_cert_ids = [gc.grupo_cert_id for gc in grupo_certs]

    # Get all allowed URLs for these grupo_certs
    urls_permitidas = (
        db.query(GlobalUrls)
        .join(GruposCertificadosUrls, GruposCertificadosUrls.global_urls_id == GlobalUrls.global_urls_id)
        .filter(
            GruposCertificadosUrls.grupo_cert_id.in_(grupo_cert_ids),
            GlobalUrls.inativo == False,
        )
        .all()
    )

    # Check if request domain matches any allowed domain
    for url_entry in urls_permitidas:
        if url_entry.url:
            allowed_parsed = urlparse(url_entry.url)
            # Only allow HTTPS URLs from database
            if allowed_parsed.scheme == "https":
                # Normalize allowed domain for consistent comparison
                allowed_domain = _normalize_domain(allowed_parsed.netloc)
                if request_domain == allowed_domain:
                    return True

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Acesso negado: dominio nao autorizado para este certificado. Solicite ao administrador que adicione o dominio a lista de URLs permitidas."
    )


# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------


@router.post("/", response_model=CertificateUploadResponse)
async def upload_certificate(
    arquivo: UploadFile = File(...),
    senha: str = Form(...),
    empresa_id: str = Form(...),
    db: Session = Depends(get_db),
    user_data: dict[str, Any] = Depends(check_auth_with_ip),
) -> CertificateResponse:
    """
    Upload certificate to Cofre for encryption and storage.

    Admin only - empresa_id must be provided explicitly.
    """
    # 1. Check if user is admin
    if not user_data.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem fazer upload de certificados",
        )

    usuario_id = get_user_id_from_data(user_data)

    # 2. Validate empresa_id format (must be valid UUID)
    try:
        uuid.UUID(empresa_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="empresa_id deve ser um UUID válido",
        )

    # 3. Read file content with size limit check
    file_content = await arquivo.read()
    if not file_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Arquivo vazio",
        )

    # Check file size to prevent DoS attacks
    if len(file_content) > MAX_CERT_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Arquivo muito grande. Tamanho maximo permitido: {MAX_CERT_SIZE_BYTES // (1024 * 1024)} MB",
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
    user_data: dict[str, Any] = Depends(check_auth_with_ip),
) -> list[CertificateResponse]:
    """
    List certificates.

    Admin only - If empresa_id is provided, lists certificates for that empresa.
    Otherwise, lists all certificates the user has access to.

    Args:
        include_deleted: If True, includes soft-deleted certificates in the results.
    """
    # Check if user is admin
    if not user_data.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem listar certificados",
        )

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


@router.get("/der", response_model=CertificateDerResponse)
async def get_certificates_der(
    db: Session = Depends(get_db),
    user_data: dict[str, Any] = Depends(check_auth_with_ip),
) -> CertificateDerResponse:
    """
    Get DER-encoded certificate data for all accessible certificates.

    Auto-discovers certificates based on:
    1. User's grupo membership (user in grupo that has certificate)
    2. Current day/time access rules (tipo_dia, horarios, feriados)

    No request body needed - endpoint discovers accessible certificates automatically.

    Returns:
    - certificates: List of accessible certificates with DER data
    - errors: List of certificates that failed access control with reasons
    """
    usuario_id = get_user_id_from_data(user_data)

    # 1. Find all certificates user can access via grupos
    # Query: User → GruposUsuarios → GruposCertificados → Certificados
    accessible_certs = (
        db.query(Certificados)
        .join(
            GruposCertificados,
            GruposCertificados.certificado_id == Certificados.certificado_id,
        )
        .join(
            GruposUsuarios,
            GruposUsuarios.grupo_id == GruposCertificados.grupo_id,
        )
        .filter(
            GruposUsuarios.usuario_id == usuario_id,
            Certificados.deleted_at.is_(None),
            Certificados.cofre_cert_id.isnot(None),
        )
        .distinct()
        .all()
    )

    if not accessible_certs:
        return CertificateDerResponse(certificates=[], errors=[])

    # 2. Filter by access rules (day/time/holiday)
    id_mapping: dict[str, str] = {}
    errors: list[CertificateDerError] = []

    for cert in accessible_certs:
        cert_id = str(cert.certificado_id)
        try:
            # Check access rules (day/time/holiday)
            verificar_regras_acesso(db, usuario_id, cert_id, str(cert.empresa_id))
            # Map local_id -> cofre_id
            id_mapping[cert_id] = str(cert.cofre_cert_id)
        except HTTPException as e:
            errors.append(CertificateDerError(
                id=cert_id,
                reason=e.detail
            ))

    if not id_mapping:
        return CertificateDerResponse(certificates=[], errors=errors)

    # 3. Proxy to Cofre with cofre_cert_ids
    try:
        cofre_response = await cofre_client.get_certificates_der(
            list(id_mapping.values())
        )
    except CertificateNotFoundError:
        # All requested certs not found in Cofre
        for local_id in id_mapping.keys():
            errors.append(CertificateDerError(
                id=local_id,
                reason="Certificado nao encontrado no Cofre"
            ))
        return CertificateDerResponse(certificates=[], errors=errors)
    except CofreServiceError as e:
        raise HTTPException(
            status_code=e.status_code or 500,
            detail=e.message,
        )

    # 4. Map cofre_id back to local_id in response
    reverse_mapping = {v: k for k, v in id_mapping.items()}

    certificates = []
    for item in cofre_response:
        cofre_id = item["id"]
        local_id = reverse_mapping.get(cofre_id)
        if local_id:
            certificates.append(CertificateDerItem(
                id=local_id,
                label=item["label"],
                cert_der_b64=item["cert_der_b64"]
            ))

    return CertificateDerResponse(certificates=certificates, errors=errors)


@router.get("/{certificado_id}")
async def get_certificate(
    certificado_id: str,
    db: Session = Depends(get_db),
    user_data: dict[str, Any] = Depends(check_auth_with_ip),
) -> CertificateResponse:
    """
    Get specific certificate by ID.

    Admin only.
    """
    # Check if user is admin
    if not user_data.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem visualizar certificados",
        )

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
    user_data: dict[str, Any] = Depends(check_auth_with_ip),
) -> SignResponse:
    """
    Sign data using certificate.

    Steps:
    1. Verify user has access to certificate via grupo
    2. Check access rules (regras_acesso, horarios, feriados)
    3. Check URL is allowed for this grupo-certificado
    4. Send to Cofre for signing
    """
    usuario_id = get_user_id_from_data(user_data)

    # 1. Verify certificate access
    cert = verificar_acesso_certificado(db, usuario_id, certificado_id)

    # 2. Check access rules (regras_acesso, horarios, feriados)
    verificar_regras_acesso(db, usuario_id, certificado_id, str(cert.empresa_id))

    # 3. Check URL is allowed
    verificar_url_permitida(db, usuario_id, certificado_id, data.url)

    # 4. Decode base64 data
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
    user_data: dict[str, Any] = Depends(check_auth_with_ip),
) -> dict[str, str]:
    """
    Soft delete certificate.

    Admin only - Marks the certificate as deleted without removing data from the database or Cofre.
    """
    # Check if user is admin
    if not user_data.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem remover certificados",
        )

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
