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
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
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
    ativo: bool = True


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
    request: Request,
    arquivo: UploadFile = File(...),
    senha: str = Form(""),
    empresa_id: str = Form(None),
    auto_create_empresa: str = Form(None),
    manual_cnpj: str = Form(None),
    db: Session = Depends(get_db),
    user_data: dict[str, Any] = Depends(check_auth_with_ip),
) -> CertificateResponse:
    """
    Upload certificate to Cofre for encryption and storage.

    Admin only - empresa_id must be provided explicitly, or auto_create_empresa=true
    to create/find empresa automatically from certificate CNPJ.
    """
    # 1. Check if user is admin
    if not user_data.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem fazer upload de certificados",
        )

    usuario_id = get_user_id_from_data(user_data)
    should_auto_create = auto_create_empresa == "true"

    # 2. Validate empresa_id format (must be valid UUID) if provided
    if empresa_id:
        try:
            uuid.UUID(empresa_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="empresa_id deve ser um UUID válido",
            )
    elif not should_auto_create:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="empresa_id é obrigatório quando auto_create_empresa não está ativo",
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

    # 4. Validate PFX password and extract certificate info
    try:
        private_key, certificate, additional_certs = pkcs12.load_key_and_certificates(
            file_content, senha.encode() if senha else None
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha do certificado inválida",
        )

    # 5. Auto-create empresa if needed
    if should_auto_create and not empresa_id:
        import re
        from cryptography.x509.oid import NameOID
        from backend.app.services.auth_client import auth_client
        from backend.app.core.exceptions import AuthServiceError

        # Extract CNPJ from certificate subject
        # ICP-Brasil certificates may have CNPJ in various fields:
        # - serialNumber (most common for e-CNPJ)
        # - CN (Common Name)
        # - OU (Organizational Unit)
        # - O (Organization Name)
        cert_cnpj = None
        cert_name = None
        cn_value = None
        debug_info = {}  # Store extracted values for error messages

        def extract_cnpj_from_text(text):
            """Extract CNPJ (14 digits) from text, handling various formats."""
            if not text:
                return None
            # Remove ALL non-digit characters
            digits_only = re.sub(r'\D', '', text)
            # CNPJ has exactly 14 digits
            if len(digits_only) >= 14:
                # Find first sequence of 14 digits
                cnpj_match = re.search(r'\d{14}', digits_only)
                if cnpj_match:
                    return cnpj_match.group(0)
            return None

        if certificate:
            try:
                subject = certificate.subject

                # Try to get CN for certificate name
                cn_attrs = subject.get_attributes_for_oid(NameOID.COMMON_NAME)
                if cn_attrs:
                    cn_value = cn_attrs[0].value
                    cert_name = cn_value
                    debug_info['CN'] = cn_value

                # 1. First try serialNumber (ICP-Brasil standard for e-CNPJ)
                serial_attrs = subject.get_attributes_for_oid(NameOID.SERIAL_NUMBER)
                if serial_attrs:
                    serial_value = serial_attrs[0].value
                    debug_info['serialNumber'] = serial_value
                    cert_cnpj = extract_cnpj_from_text(serial_value)

                # 2. Try CN (Common Name) if serialNumber didn't work
                if not cert_cnpj and cn_value:
                    cert_cnpj = extract_cnpj_from_text(cn_value)

                # 3. Try OU (Organizational Unit)
                if not cert_cnpj:
                    ou_attrs = subject.get_attributes_for_oid(NameOID.ORGANIZATIONAL_UNIT_NAME)
                    for ou_attr in ou_attrs:
                        debug_info['OU'] = ou_attr.value
                        cert_cnpj = extract_cnpj_from_text(ou_attr.value)
                        if cert_cnpj:
                            break

                # 4. Try O (Organization Name)
                if not cert_cnpj:
                    org_attrs = subject.get_attributes_for_oid(NameOID.ORGANIZATION_NAME)
                    if org_attrs:
                        debug_info['O'] = org_attrs[0].value
                        cert_cnpj = extract_cnpj_from_text(org_attrs[0].value)

                # 5. Try Subject Alternative Names extension
                if not cert_cnpj:
                    try:
                        from cryptography.x509 import ExtensionOID, SubjectAlternativeName
                        san_ext = certificate.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
                        san = san_ext.value
                        for name in san:
                            name_str = str(name.value) if hasattr(name, 'value') else str(name)
                            debug_info['SAN'] = name_str
                            cert_cnpj = extract_cnpj_from_text(name_str)
                            if cert_cnpj:
                                break
                    except Exception:
                        pass  # SAN extension not present or error reading it

            except Exception:
                pass

        # Use manual_cnpj if provided (takes precedence over extracted)
        if manual_cnpj:
            manual_digits = re.sub(r'\D', '', manual_cnpj)  # Remove non-digits
            if len(manual_digits) == 14:
                cert_cnpj = manual_digits
            elif len(manual_digits) > 0:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"CNPJ inválido. Deve conter exatamente 14 dígitos. Fornecido: {len(manual_digits)} dígitos.",
                )

        if not cert_cnpj or len(cert_cnpj) != 14:
            detail_msg = "Não foi possível extrair o CNPJ do certificado."
            # Add debug info about what fields were found
            if debug_info:
                fields_found = []
                for field, value in debug_info.items():
                    # Truncate long values
                    display_val = value[:80] + "..." if len(str(value)) > 80 else value
                    fields_found.append(f"{field}='{display_val}'")
                if fields_found:
                    detail_msg += f" Campos encontrados: {'; '.join(fields_found)}."
            detail_msg += " Forneça o CNPJ manualmente (14 dígitos)."
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=detail_msg,
            )

        org_id = user_data.get("organization_id")
        if not org_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuário não está associado a uma organização",
            )

        # Get authorization header from session cookie
        auth_headers = {}
        session_token = request.cookies.get("session_token")
        if session_token:
            auth_headers["Authorization"] = f"Bearer {session_token}"

        # Search for existing empresa with this CNPJ via auth service
        try:
            # Paginate through companies to find one with matching CNPJ
            # Auth service has max limit of 100 per request
            existing_empresa = None
            offset = 0
            page_size = 100

            while existing_empresa is None:
                empresas_response = await auth_client.proxy_request(
                    method="GET",
                    path=f"/api/v1/organizations/{org_id}/companies",
                    params={"limit": page_size, "offset": offset},
                    headers=auth_headers,
                )

                empresas_list = empresas_response.get("companies", [])
                if not empresas_list:
                    break  # No more companies to check

                for emp in empresas_list:
                    emp_cnpj = re.sub(r'\D', '', emp.get("cnpj", "") or "")
                    if emp_cnpj == cert_cnpj:
                        existing_empresa = emp
                        break

                if len(empresas_list) < page_size:
                    break  # Last page reached

                offset += page_size

            if existing_empresa:
                empresa_id = str(existing_empresa.get("id"))
            else:
                # Create new empresa via auth service
                company_data = {
                    "name": cert_name or f"Empresa CNPJ {cert_cnpj}",
                    "cnpj": cert_cnpj,
                    "timezone": "America/Sao_Paulo",
                }

                new_empresa = await auth_client.proxy_request(
                    method="POST",
                    path=f"/api/v1/organizations/{org_id}/companies",
                    json=company_data,
                    headers=auth_headers,
                )
                empresa_id = str(new_empresa.get("id"))

                if not empresa_id:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Falha ao criar empresa automaticamente",
                    )

        except AuthServiceError as e:
            raise HTTPException(
                status_code=e.status_code or 500,
                detail=f"Erro ao buscar/criar empresa: {e.message}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao buscar/criar empresa: {str(e)}",
            )

    # 6. Send to Cofre for encryption
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

    # 7. Store local reference
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
    page: int = 1,
    limit: int = 10,
    search: str = "",
    sort: str = "",
    grupo_id: str | None = None,
    db: Session = Depends(get_db),
    user_data: dict[str, Any] = Depends(check_auth_with_ip),
) -> dict[str, Any]:
    """
    List certificates with pagination.

    Admin only - If empresa_id is provided, lists certificates for that empresa.
    Otherwise, lists all certificates the user has access to.

    Args:
        include_deleted: If True, includes soft-deleted certificates in the results.
        page: Page number (1-indexed)
        limit: Number of items per page
        search: Search term for filtering
        sort: Sort field and direction
        grupo_id: Filter by grupo ID
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

        # Filter by grupo if provided
        if grupo_id:
            query = query.join(
                GruposCertificados,
                GruposCertificados.certificado_id == Certificados.certificado_id,
            ).filter(GruposCertificados.grupo_id == grupo_id)

        # Apply search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                Certificados.nome_arquivo.ilike(search_term) |
                Certificados.proprietario.ilike(search_term)
            )

        # Get total count before pagination
        total = query.count()

        # Apply pagination
        offset = (page - 1) * limit
        certs = query.offset(offset).limit(limit).all()
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

        # Apply search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                Certificados.nome_arquivo.ilike(search_term) |
                Certificados.proprietario.ilike(search_term)
            )

        # Get total count before pagination
        total = query.distinct().count()

        # Apply pagination
        offset = (page - 1) * limit
        certs = query.distinct().offset(offset).limit(limit).all()

    data = [
        {
            "certificado_id": str(c.certificado_id),
            "cofre_cert_id": str(c.cofre_cert_id) if c.cofre_cert_id else None,
            "empresa_id": str(c.empresa_id),
            "nome_arquivo": c.nome_arquivo,
            "proprietario": c.proprietario,
            "emitido_por": c.emitido_por,
            "validade_inicio": str(c.validade_inicio) if c.validade_inicio else None,
            "valido_ate": str(c.valido_ate) if c.valido_ate else None,
            "criado_em": str(c.criado_em) if c.criado_em else None,
            "ativo": c.ativo,
        }
        for c in certs
    ]

    return {
        "data": data,
        "total": total,
        "page": page,
        "limit": limit,
    }


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
        ativo=cert.ativo,
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


@router.patch("/{certificado_id}/toggle-ativo")
async def toggle_certificate_status(
    certificado_id: str,
    db: Session = Depends(get_db),
    user_data: dict[str, Any] = Depends(check_auth_with_ip),
) -> dict[str, Any]:
    """
    Toggle certificate active status.

    Admin only - Toggles the 'ativo' field between True and False.
    """
    # Check if user is admin
    if not user_data.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem alterar o status do certificado",
        )

    usuario_id = get_user_id_from_data(user_data)

    # Get certificate (exclude deleted)
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

    # Toggle the ativo status
    cert.ativo = not cert.ativo
    db.commit()
    db.refresh(cert)

    return {
        "certificado_id": str(cert.certificado_id),
        "ativo": cert.ativo,
        "message": f"Certificado {'ativado' if cert.ativo else 'desativado'} com sucesso",
    }
