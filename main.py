from fastapi import FastAPI, UploadFile, Form, HTTPException, Header, Depends
import os
import json
import time
import traceback
from pydantic import BaseModel
import base64
from chave_mestra import gerar_chave
from crypto_utils import encrypt_pfx, decrypt_pfx
from dotenv import load_dotenv
from db_sqlite import getDb
from cryptography.hazmat.primitives.serialization import Encoding
from gerar_token_acesso import gerar_token
from fastapi.middleware.cors import CORSMiddleware
from Crypto.Signature import pkcs1_15
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.primitives import serialization

load_dotenv()

app = FastAPI()

origins = ["http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MASTER_KEY = gerar_chave(password=os.getenv('MASTER_KEY'))

STORAGE_DIR = "storage/certificados"
os.makedirs(STORAGE_DIR, exist_ok=True)

try:
    PRIVATE_KEY = RSA.import_key(open("./certificados/private_key.pem", "rb").read())
    print("🔐 PRIVATE_KEY carregada com sucesso!")
except Exception as e:
    print("❌ ERRO carregando PRIVATE_KEY:", e)
    PRIVATE_KEY = None  # type: ignore

@app.get("/")
def inicio():
    return {
        "status": "ok",
        "message": "funcionando"
    }
@app.post("/teste/h")
def teste_h():
    conexao = getDb()
    cursor = conexao.cursor()
    cursor.execute(
        "SELECT * FROM certificados"
    )
    certificados = cursor.fetchall()
    print(f'certificados: {certificados}')
    conexao.close()
    return {"certificados": certificados}


class SignRequest(BaseModel):
    data: str
    cert_id: str
    algorithm: str

def validar_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token inválido")
    token = authorization[7:]
    conexao = getDb()
    cursor = conexao.cursor()
    cursor.execute("select * from acesso where token = ?", (token,))
    acesso = cursor.fetchone()
    print(acesso)


    if not acesso:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")

    return acesso


@app.get("/api/certificates")
async def list_certificates():
    """Lista todos os certificados do usuário autenticado"""
    id_usuario = 1

    conexao = getDb()
    cursor = conexao.cursor()
    cursor.execute(
        "SELECT * FROM certificados WHERE id_usuario = ?",
        (id_usuario,)
    )
    certificados = cursor.fetchall()
    # certificados = [["1212", "meu certificado", "id certificado"], ["12", "meu certifi", "id certif"]]
    print(f'certificados: {certificados}')
    conexao.close()


    lista_certificados = []
    for certificado in certificados:
        print('certificado')
        print(certificado)
        encrypted_pfx = json.loads(certificado[3].replace("'", '"'))
        encrypted_senha = json.loads(certificado[4].replace("'", '"'))
        print(f'===tipo=== encrypted_pfx {type(encrypted_pfx)}')

        pfx_bytes = decrypt_pfx(encrypted_pfx, MASTER_KEY)
        senha_bytes = decrypt_pfx(encrypted_senha, MASTER_KEY)
        senha = senha_bytes.decode()
        # Extrair o certificado do PFX

        private_key, certificate, additional_certs = pkcs12.load_key_and_certificates(
            pfx_bytes,
            password=b"2705"  # A senha do certificado
        )

        # Converter certificado para DER
        cert_der = certificate.public_bytes(Encoding.DER)

        # Converter DER para base64
        cert_base64 = base64.b64encode(cert_der).decode()

        lista_certificados.append({
            "id": f"{certificado[0]}",
            "label": certificado[2],
            "data":  cert_base64

        })
    return {"certificates": lista_certificados} #type: ignore

@app.post("/api/sign")
async def sign_digest(payload: SignRequest):
    """Assina um digest usando o certificado do usuário"""
    id_usuario = 1

    try:
        # Busca o certificado do usuário
        conexao = getDb()
        cursor = conexao.cursor()
        cursor.execute(
            "SELECT encrypted, secret FROM certificados WHERE cert_id = ? AND id_usuario = ?",
            (payload.cert_id, id_usuario)
        )
        cert_data = cursor.fetchone()
        conexao.close()

        if not cert_data:
            raise HTTPException(status_code=404, detail="Certificado não encontrado")

        # Descriptografa o certificado e a senha
        encrypted_pfx = json.loads(cert_data[0].replace("'", '"'))
        encrypted_senha = json.loads(cert_data[1].replace("'", '"'))

        pfx_bytes = decrypt_pfx(encrypted_pfx, MASTER_KEY)
        senha_bytes = decrypt_pfx(encrypted_senha, MASTER_KEY)
        senha = senha_bytes.decode()


        if not private_key:
            raise HTTPException(status_code=500, detail="Chave privada não encontrada no certificado")

        # Converte a chave privada para o formato RSA do PyCryptodome
        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )
        rsa_key = RSA.import_key(pem)

        # Decodifica o digest e assina
        digest_bytes = base64.b64decode(payload.data)
        h = SHA256.new(digest_bytes)
        signature = pkcs1_15.new(rsa_key).sign(h)

        return {
            "status": "ok",
            "signature_b64": base64.b64encode(signature).decode()
        }

    except HTTPException:
        raise
    except Exception as e:
        print("ERRO NA ASSINATURA:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao assinar: {str(e)}")
    
@app.post("/cadastro/usuario")
async def cad_user(nome: str = Form(...), senha: str = Form(...)):
    conexao = getDb()
    cursor = conexao.cursor()
    cursor.execute("INSERT INTO USUARIOS(nome, senha) VALUES(?, ?)", (nome, senha))
    conexao.commit()
    conexao.close()
    return {
        "status": "ok", "message": "usuario cadastrado"
    }

@app.post("/login")
async def login(nome: str = Form(...), senha: str = Form(...)):
    print(f'nome: {nome} | senha: {senha}')
    conexao = getDb()
    cursor = conexao.cursor()
    cursor.execute("select * from usuarios where nome = ? and senha = ?", (nome, senha))
    usuario = cursor.fetchone()
    
    if usuario:
        token_gerado = gerar_token()
        cursor.execute("insert into acesso(id_usuario, token, ativo) values (?, ?, ?)", (usuario[0], token_gerado, 1))
        conexao.commit()
        conexao.close()
        return {
            "status": "ok", "message": "usuario cadastrado", "usuario": usuario[0],
            "token": token_gerado
        }
    raise HTTPException(status_code=403, detail="Usuário não existe")

@app.post("/upload/certificado")
async def upload_certificado(arquivo: UploadFile, senha: str = Form(...), token: tuple = Depends(validar_token)):
    """Recebe um .pfx e armazena de forma criptografada"""
    print(f'token: {token[1]}')

    if not arquivo.filename.lower().endswith(".pfx"):
        raise HTTPException(status_code=400, detail="Envie um arquivo .pfx válido")

    pfx_bytes = await arquivo.read()
    encrypted_data = encrypt_pfx(pfx_bytes, MASTER_KEY)
    senha_encrypted = encrypt_pfx(senha.encode(), MASTER_KEY)

    # Gera um cert_id único baseado no timestamp e nome do arquivo
    cert_id = f"{int(time.time())}_{os.path.splitext(arquivo.filename)[0]}"

    save_path = os.path.join(STORAGE_DIR, f"{cert_id}.json")
    with open(save_path, "w") as f:
        json.dump({
            "filename": arquivo.filename,
            "cert_id": cert_id,
            "encrypted": encrypted_data,
            "senha": senha_encrypted
        }, f)

    conexao = getDb()
    cursor = conexao.cursor()
    cursor.execute(
        "INSERT INTO certificados(id_usuario, nome_arquivo, cert_id, encrypted, secret) VALUES (?, ?, ?, ?, ?)",
        (token[1], arquivo.filename, cert_id, f'{encrypted_data}', f'{senha_encrypted}')
    )
    conexao.commit()
    conexao.close()

    return {
        "status": "ok",
        "message": f"Certificado {arquivo.filename} salvo com segurança.",
        "cert_id": cert_id
    }
