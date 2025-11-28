import os
import json
import base64
import time
import traceback

from fastapi import APIRouter, UploadFile, Form, HTTPException, Depends
from cryptography.hazmat.primitives.serialization import Encoding, pkcs12
from cryptography.hazmat.primitives import serialization
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

from backend.app.core.config import MASTER_KEY, STORAGE_DIR
from backend.app.core.security import validar_token
from backend.app.schemas.certificados import SignRequest
from backend.app.utils.crypto_utils import encrypt_pfx, decrypt_pfx
from backend.app.utils.db_sqlite import getDb

router = APIRouter(tags=["certificados"])


@router.post("/upload/certificado")
async def upload_certificado(
    arquivo: UploadFile,
    senha: str = Form(...),
    acesso=Depends(validar_token),
):
    """
    Recebe um .pfx, criptografa e grava no banco (tabela certificados).
    """
    print(f"token: {acesso[2]}")  # (id_acesso, id_usuario, token, ativo)

    if not arquivo.filename.lower().endswith(".pfx"):
        raise HTTPException(status_code=400, detail="Envie um arquivo .pfx válido")

    pfx_bytes = await arquivo.read()

    # criptografa o .pfx e a senha com a MASTER_KEY
    encrypted_data = encrypt_pfx(pfx_bytes, MASTER_KEY)
    senha_encrypted = encrypt_pfx(senha.encode(), MASTER_KEY)

    # Gera um cert_id simples baseado no timestamp
    cert_id = f"{int(time.time())}_{os.path.splitext(arquivo.filename)[0]}"

    # (opcional) salva em arquivo também
    os.makedirs(STORAGE_DIR, exist_ok=True)
    save_path = os.path.join(STORAGE_DIR, f"{cert_id}.json")
    with open(save_path, "w") as f:
        json.dump(
            {
                "encrypted": encrypted_data,
                "secret": senha_encrypted,
            },
            f,
        )

    # grava no banco
    conn = getDb()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO certificados(id_usuario, nome_arquivo, cert_id, encrypted, secret)
        VALUES (?, ?, ?, ?, ?)
        """,
        (acesso[1], arquivo.filename, cert_id, f"{encrypted_data}", f"{senha_encrypted}"),
    )
    conn.commit()
    conn.close()

    return {
        "status": "ok",
        "message": f"Certificado {arquivo.filename} salvo com sucesso.",
        "cert_id": cert_id,
    }


@router.get("/api/certificates")
async def list_certificates(acesso=Depends(validar_token)):
    """
    Lista os certificados do usuário autenticado.
    Retorna o certificado em DER base64 para o front.
    """
    id_usuario = acesso[1]

    conn = getDb()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, nome_arquivo, cert_id, encrypted, secret "
        "FROM certificados WHERE id_usuario = ?",
        (id_usuario,),
    )
    certificados = cursor.fetchall()
    conn.close()

    lista_certificados: list[dict] = []

    for cert_row in certificados:
        cert_id_db = cert_row[0]
        label = cert_row[1]

        encrypted_pfx = json.loads(cert_row[3].replace("'", '"'))
        encrypted_senha = json.loads(cert_row[4].replace("'", '"'))

        pfx_bytes = decrypt_pfx(encrypted_pfx, MASTER_KEY)
        senha_bytes = decrypt_pfx(encrypted_senha, MASTER_KEY)

        private_key, certificate, _ = pkcs12.load_key_and_certificates(
            pfx_bytes, password=senha_bytes
        )

        cert_der = certificate.public_bytes(Encoding.DER)
        cert_b64 = base64.b64encode(cert_der).decode()

        lista_certificados.append(
            {
                "id": f"{cert_id_db}",
                "label": label,
                "cert_der_b64": cert_b64,
            }
        )

    return lista_certificados


@router.post("/api/sign")
async def sign_digest(payload: SignRequest, acesso=Depends(validar_token)):
    """
    Assina um digest (hash) SHA256 em base64 usando o certificado do usuário.
    """
    id_usuario = acesso[1]
    try:
        conn = getDb()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT encrypted, secret FROM certificados WHERE id = ? AND id_usuario = ?",
            (payload.cert_id, id_usuario),
        )
        cert_data = cursor.fetchone()
        conn.close()

        if not cert_data:
            raise HTTPException(status_code=404, detail="Certificado não encontrado")

        encrypted_pfx = json.loads(cert_data[0].replace("'", '"'))
        encrypted_senha = json.loads(cert_data[1].replace("'", '"'))

        pfx_bytes = decrypt_pfx(encrypted_pfx, MASTER_KEY)
        senha_bytes = decrypt_pfx(encrypted_senha, MASTER_KEY)

        private_key, certificate, _ = pkcs12.load_key_and_certificates(
            pfx_bytes, password=senha_bytes
        )

        if not private_key:
            raise HTTPException(
                status_code=500, detail="Chave privada não encontrada no certificado"
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

    except HTTPException:
        raise
    except Exception as e:
        print("ERRO NA ASSINATURA:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Erro ao assinar")
