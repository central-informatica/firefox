import os
import json
import base64
import datetime
import traceback

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session
from cryptography.hazmat.primitives.serialization import Encoding, pkcs12
from cryptography.hazmat.primitives import serialization
from cryptography.x509.oid import NameOID
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

from backend.app.core.config import MASTER_KEY
from backend.app.core.validar_token import validar_token
from backend.app.schemas.token import TokenContext
from backend.app.db.session import get_db
from backend.app.db.models import Certificados
from backend.app.api.deps import get_current_user
from backend.app.utils.crypto_utils import encrypt_pfx, decrypt_pfx
from backend.app.schemas.certificados import SignRequest,CertificadoPermitidoResponse, ValidarAcessoCertificadoResponse
from backend.app.crud.certificado import listar_certificados_permitidos as crud_listar_certificados_permitidos, validar_acesso_certificado

router = APIRouter(prefix="/certificados", tags=["certificados"])

def extrair_info_certificado(pfx_bytes: bytes, senha: str | None):
    """
    Lê o .pfx em memória e retorna:
    - proprietario (CN do subject)
    - emitido_por (CN do issuer)
    - validade_inicio (datetime)
    - valido_ate (datetime)
    """
    senha_bytes = senha.encode() if senha else None

    private_key, certificate, _ = pkcs12.load_key_and_certificates(
        pfx_bytes,
        senha_bytes
    )

    subject = certificate.subject
    issuer = certificate.issuer

    proprietario = subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
    emitido_por = issuer.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value

    validade_inicio = certificate.not_valid_before
    valido_ate = certificate.not_valid_after

    return proprietario, emitido_por, validade_inicio, valido_ate


@router.post("/")
async def upload_certificado(
    empresa_id: int | None = Form(None),
    senha: str = Form(""),
    arquivo: UploadFile = File(...),
    proprietario: str = Form(""),
    emitido_por: str = Form(""),
    validade_inicio: str = Form(""),
    valido_ate: str = Form(""),
    auto_create_empresa: bool = Form(False),
    manual_cnpj: str | None = Form(None),
    token_context: TokenContext = Depends(validar_token),
    db: Session = Depends(get_db),
):
    """
    Recebe um .pfx, extrai os dados principais, criptografa e grava no banco.
    """

    id_usuario = token_context.usuario_id

    if not arquivo.filename.lower().endswith(".pfx"):
        raise HTTPException(status_code=400, detail="Envie um arquivo .pfx válido")

    pfx_bytes = await arquivo.read()

    try:
        proprietario_auto, emitido_por_auto, validade_inicio_auto, valido_ate_auto = (
            extrair_info_certificado(pfx_bytes, senha)
        )
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Não foi possível ler o certificado. Verifique a senha informada.",
        )

    # If auto-create company was requested, attempt to resolve or create the company
    target_empresa_id = empresa_id

    if not target_empresa_id and auto_create_empresa:
        # try manual CNPJ first
        cnpj_digits = None
        if manual_cnpj:
            cnpj_digits = ''.join(filter(str.isdigit, manual_cnpj))
            if len(cnpj_digits) != 14:
                raise HTTPException(status_code=400, detail="CNPJ inválido. Deve conter 14 dígitos.")

        # If no manual CNPJ, attempt to extract from certificate subject/issuer
        if not cnpj_digits:
            import re
            try:
                _, certificate_obj, _ = pkcs12.load_key_and_certificates(pfx_bytes, senha.encode() if senha else None)
                subject_str = certificate_obj.subject.rfc4514_string()
                issuer_str = certificate_obj.issuer.rfc4514_string()
                match = re.search(r"(\d{14})", subject_str) or re.search(r"(\d{14})", issuer_str)
                if match:
                    cnpj_digits = match.group(1)
            except Exception:
                # If we cannot parse the certificate again, proceed without cnpj
                cnpj_digits = None

        # If we have a CNPJ, find or create the company
        from backend.app.db.models import Empresas, Usuarios
        from backend.app.schemas.empresas import EmpresaCreate
        from backend.app.crud.empresas import crud_empresas

        if cnpj_digits:
            existing = db.query(Empresas).filter(Empresas.cnpj == cnpj_digits).first()
            if existing:
                target_empresa_id = existing.empresa_id
            else:
                # create company with owner as razao_social
                current_user = db.query(Usuarios).filter(Usuarios.usuario_id == token_context.usuario_id).first()
                if not current_user:
                    raise HTTPException(status_code=400, detail="Usuário não encontrado para criação da empresa")

                empresa_data = EmpresaCreate(
                    razao_social=proprietario_auto or emitido_por_auto or "Empresa do certificado",
                    cnpj=cnpj_digits,
                )

                nova = crud_empresas.criar(db, empresa_data, current_user=current_user)
                target_empresa_id = nova.empresa_id
        else:
            # fallback: try to match by name
            from backend.app.db.models import Empresas
            nome_busca = (proprietario_auto or emitido_por_auto or "").strip()
            if nome_busca:
                existing = (
                    db.query(Empresas)
                    .filter(Empresas.razao_social.ilike(nome_busca))
                    .first()
                )
                if existing:
                    target_empresa_id = existing.empresa_id
                else:
                    raise HTTPException(status_code=400, detail=f"CNPJ não encontrado no certificado e nenhuma empresa com nome '{nome_busca}' existe. Forneça 'manual_cnpj' para criar a empresa automaticamente.")
            else:
                raise HTTPException(status_code=400, detail="CNPJ não encontrado no certificado. Forneça 'manual_cnpj' para criar a empresa automaticamente.")

    proprietario_final = proprietario or proprietario_auto
    emitido_por_final = emitido_por or emitido_por_auto

    if validade_inicio:
        validade_inicio_dt = datetime.datetime.fromisoformat(validade_inicio)
    else:
        validade_inicio_dt = validade_inicio_auto

    if valido_ate:
        valido_ate_dt = datetime.datetime.fromisoformat(valido_ate)
    else:
        valido_ate_dt = valido_ate_auto

    # Determine final empresa to use (either provided or created/found)
    final_empresa_id = target_empresa_id or empresa_id
    if not final_empresa_id:
        raise HTTPException(status_code=400, detail="É necessário informar 'empresa_id' ou habilitar 'auto_create_empresa' para que a empresa seja criada automaticamente.")

    encrypted_pfx = encrypt_pfx(pfx_bytes, MASTER_KEY)
    senha_bytes = senha.encode() if senha is not None else b""
    encrypted_senha = encrypt_pfx(senha_bytes, MASTER_KEY)

    
    cert = Certificados(
        empresa_id=final_empresa_id,
        criado_por=id_usuario,
        nome_arquivo=arquivo.filename,
        encrypted=json.dumps(encrypted_pfx),
        secret=json.dumps(encrypted_senha),
        proprietario=proprietario_final,
        emitido_por=emitido_por_final,
        validade_inicio=validade_inicio_dt,
        valido_ate=valido_ate_dt,
    )

    db.add(cert)
    db.commit()
    db.refresh(cert)

    return {
        "status": "ok",
        "message": f"Certificado {arquivo.filename} salvo com sucesso.",
        "certificado_id": cert.certificado_id,
    }


@router.get("/")
def listar_certificados(
    empresa_id: int,
    grupo_id: int | None = None,
    page: int = 1,
    limit: int = 10,
    search: str = "",
    sort: str = "",
    token_context: TokenContext = Depends(validar_token),
    db: Session = Depends(get_db),
):
    """
    Lista certificados da empresa, com paginação e filtro por nome de arquivo.
    """
    query = db.query(Certificados).filter(Certificados.empresa_id == empresa_id)

    # Filter by group if provided (join GruposCertificados)
    if grupo_id:
        from backend.app.db.models import GruposCertificados
        query = query.join(GruposCertificados, GruposCertificados.certificado_id == Certificados.certificado_id)
        query = query.filter(GruposCertificados.grupo_id == grupo_id)

    if search:
        like = f"%{search}%"
        query = query.filter(Certificados.nome_arquivo.ilike(like))

    total = query.count()

    if sort == "nome":
        query = query.order_by(Certificados.nome_arquivo.asc())
    else:
        query = query.order_by(Certificados.criado_em.desc())

    registros = (
        query.offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    data = []
    for c in registros:
        item = {
            "certificado_id": c.certificado_id,
            "empresa_id": c.empresa_id,
            "criado_por": c.criado_por,
            "nome_arquivo": c.nome_arquivo,
            "criado_em": c.criado_em.isoformat() if c.criado_em else None,
            "proprietario": c.proprietario,
            "emitido_por": c.emitido_por,
            "validade_inicio": c.validade_inicio.isoformat() if c.validade_inicio else None,
            "valido_ate": c.valido_ate.isoformat() if c.valido_ate else None,
        }
    
        try:
            item["criado_por_nome"] = c.usuarios.nome
        except Exception:
            item["criado_por_nome"] = None

        data.append(item)

    return {
        "data": data,
        "total": total,
    }

@router.get(
    "/listar_certificados_permitidos",
    response_model=list[CertificadoPermitidoResponse]
)
def listar_certificados_permitidos(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    
    certificados = crud_listar_certificados_permitidos(
        db=db,
        usuario_id=current_user.usuario_id,
    )
    print("Certificados permitidos encontrados:", len(certificados))
    return certificados


@router.get("/{certificado_id}/validar_acesso",response_model=ValidarAcessoCertificadoResponse,)
def validar_acesso(
    certificado_id: int,
    token_context: TokenContext = Depends(validar_token),
    db: Session = Depends(get_db),
):
    """
    Valida se o usuário autenticado tem acesso ao certificado especificado.
    Usa o usuario_id extraído do token de autenticação.
    """
    permitido = validar_acesso_certificado(
        db=db,
        usuario_id=token_context.usuario_id,
        certificado_id=certificado_id,
    )

    return {
        "certificado_id": certificado_id,
        "permitido": permitido,
    }

@router.get("/{certificado_id}")
def obter_certificado(
    certificado_id: int,
    token_context: TokenContext = Depends(validar_token),
    db: Session = Depends(get_db),
):
    cert = db.query(Certificados).filter(
        Certificados.certificado_id == certificado_id
    ).first()

    if not cert:
        raise HTTPException(status_code=404, detail="Certificado não encontrado")

    return {
        "id": cert.certificado_id,
        "empresa_id": cert.empresa_id,
        "criado_por": cert.criado_por,
        "nome_arquivo": cert.nome_arquivo,
        "criado_em": cert.criado_em.isoformat() if cert.criado_em else None,
        "proprietario": cert.proprietario,
        "emitido_por": cert.emitido_por,
        "validade_inicio": cert.validade_inicio.isoformat() if cert.validade_inicio else None,
        "valido_ate": cert.valido_ate.isoformat() if cert.valido_ate else None,
    }


@router.delete("/{certificado_id}")
def excluir_certificado(
    certificado_id: int,
    token_context: TokenContext = Depends(validar_token),
    db: Session = Depends(get_db),
):
    """
    Remove um certificado do banco. (Opcional: remove o arquivo físico)
    Garante que o certificado pertence ao usuário logado.
    """
    id_usuario = token_context.usuario_id

    cert = db.query(Certificados).filter(
        Certificados.certificado_id == certificado_id
    ).first()

    if not cert:
        raise HTTPException(status_code=404, detail="Certificado não encontrado")

    if cert.criado_por != id_usuario:
        raise HTTPException(
            status_code=403,
            detail="Você não tem permissão para excluir este certificado."
        )

    file_path = os.path.join("storage/pfx", cert.nome_arquivo)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception:
            pass  # não impede a exclusão no banco

    db.delete(cert)
    db.commit()

    return {"success": True, "message": "Certificado excluído com sucesso."}

@router.get("/api/certificates")
async def list_certificates_for_sign(
    token_context: TokenContext = Depends(validar_token),
    db: Session = Depends(get_db),
):
    """
    Lista os certificados do usuário para uso em assinatura:
    retorna DER em base64.
    """
    id_usuario = token_context.usuario_id

    certificados = db.query(Certificados).filter(
        Certificados.criado_por == id_usuario
    ).all()

    lista = []

    for cert in certificados:
        try:
            encrypted_pfx = json.loads(cert.encrypted)
            encrypted_senha = json.loads(cert.secret)

            pfx_bytes = decrypt_pfx(encrypted_pfx, MASTER_KEY)
            senha_bytes = decrypt_pfx(encrypted_senha, MASTER_KEY)

            private_key, certificate, _ = pkcs12.load_key_and_certificates(
                pfx_bytes,
                senha_bytes,
            )

            cert_der = certificate.public_bytes(Encoding.DER)
            cert_b64 = base64.b64encode(cert_der).decode()

            lista.append(
                {
                    "id": cert.certificado_id,
                    "label": cert.nome_arquivo,
                    "cert_der_b64": cert_b64,
                }
            )
        except Exception:
            traceback.print_exc()
            continue

    return lista


@router.post("/api/sign")
async def sign_digest(
    payload: SignRequest,
    token_context: TokenContext = Depends(validar_token),
    db: Session = Depends(get_db),
):
    """
    Recebe o hash (em base64) e o cert_id, recupera o certificado,
    descriptografa e assina usando SHA256 com RSA.
    """
    id_usuario = token_context.usuario_id

    cert = db.query(Certificados).filter(
        Certificados.certificado_id == payload.cert_id,
        Certificados.criado_por == id_usuario,
    ).first()

    if not cert:
        raise HTTPException(status_code=404, detail="Certificado não encontrado")

    try:
        encrypted_pfx = json.loads(cert.encrypted)
        encrypted_senha = json.loads(cert.secret)

        pfx_bytes = decrypt_pfx(encrypted_pfx, MASTER_KEY)
        senha_bytes = decrypt_pfx(encrypted_senha, MASTER_KEY)

        private_key, certificate, _ = pkcs12.load_key_and_certificates(
            pfx_bytes,
            senha_bytes,
        )

        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )

        rsa_key = RSA.import_key(pem)

        digest_bytes = base64.b64decode(payload.data)
        h = SHA256.new(digest_bytes)
        signature = pkcs1_15.new(rsa_key).sign(h)

        return {
            "status": "ok",
            "signature_b64": base64.b64encode(signature).decode(),
        }

    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Erro ao assinar o conteúdo")
