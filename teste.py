import httpx
import ssl
import tempfile
import os
from fastapi import FastAPI, Form, HTTPException, Request, Response
from OpenSSL import crypto
from db_sqlite import getDb
from crypto_utils import decrypt_pfx
from chave_mestra import gerar_chave
from dotenv import load_dotenv
import asyncio
from typing import Dict
from datetime import datetime, timedelta

load_dotenv()

app = FastAPI()

MASTER_KEY = gerar_chave(password=os.getenv('MASTER_KEY'))

# Cache de certificados em memória (evita descriptografar toda hora)
# Estrutura: {user_id: {cert_id: (cert_path, key_path, expira_em)}}
CERT_CACHE: Dict[int, Dict[int, tuple]] = {}
CACHE_DURATION_MINUTES = 30

def validar_token(authorization: str):
    """Valida token"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token inválido")
    
    token = authorization[7:]
    conexao = getDb()
    cursor = conexao.cursor()
    cursor.execute("SELECT id_usuario FROM acesso WHERE token = ? AND ativo = 1", (token,))
    acesso = cursor.fetchone()
    conexao.close()
    
    if not acesso:
        raise HTTPException(status_code=401, detail="Token inválido")
    
    return acesso[0]

def limpar_cache_expirado():
    """Remove certificados expirados do cache"""
    agora = datetime.now()
    usuarios_para_remover = []
    
    for user_id, certs in CERT_CACHE.items():
        certs_para_remover = []
        for cert_id, (cert_path, key_path, expira_em) in certs.items():
            if agora > expira_em:
                # Remover arquivos temporários
                try:
                    if os.path.exists(cert_path):
                        os.unlink(cert_path)
                    if os.path.exists(key_path):
                        os.unlink(key_path)
                except:
                    pass
                certs_para_remover.append(cert_id)
        
        for cert_id in certs_para_remover:
            del certs[cert_id]
        
        if not certs:
            usuarios_para_remover.append(user_id)
    
    for user_id in usuarios_para_remover:
        del CERT_CACHE[user_id]

def get_certificado_cached(user_id: int, cert_id: int):
    """Obtém certificado do cache ou cria novo"""
    limpar_cache_expirado()
    
    # Verificar se está no cache
    if user_id in CERT_CACHE and cert_id in CERT_CACHE[user_id]:
        cert_path, key_path, expira_em = CERT_CACHE[user_id][cert_id]
        if datetime.now() < expira_em:
            return cert_path, key_path
    
    # Buscar do banco
    conexao = getDb()
    cursor = conexao.cursor()
    cursor.execute("""
        SELECT encrypted, secret 
        FROM certificados 
        WHERE id = ? AND id_usuario = ?
    """, (cert_id, user_id))
    
    cert_data = cursor.fetchone()
    conexao.close()
    
    if not cert_data:
        raise HTTPException(status_code=404, detail="Certificado não encontrado")
    
    # Descriptografar
    try:
        pfx_bytes = decrypt_pfx(cert_data[0], MASTER_KEY)
        senha_cert = decrypt_pfx(cert_data[1], MASTER_KEY).decode()
        p12 = crypto.load_pkcs12(pfx_bytes, senha_cert.encode())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar certificado: {str(e)}")
    
    # Criar arquivos temporários persistentes
    cert_pem = crypto.dump_certificate(crypto.FILETYPE_PEM, p12.get_certificate())
    cert_temp = tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.pem')
    cert_temp.write(cert_pem)
    cert_temp.flush()
    cert_temp.close()
    
    key_pem = crypto.dump_privatekey(crypto.FILETYPE_PEM, p12.get_privatekey())
    key_temp = tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.pem')
    key_temp.write(key_pem)
    key_temp.flush()
    key_temp.close()
    
    # Adicionar ao cache
    expira_em = datetime.now() + timedelta(minutes=CACHE_DURATION_MINUTES)
    if user_id not in CERT_CACHE:
        CERT_CACHE[user_id] = {}
    CERT_CACHE[user_id][cert_id] = (cert_temp.name, key_temp.name, expira_em)
    
    return cert_temp.name, key_temp.name


@app.post("/proxy/sefaz/generic")
async def proxy_sefaz_generic(request: Request):
    """
    Proxy transparente - aceita qualquer método HTTP
    Cliente chama: POST /proxy/sefaz/generic com:
    - url_sefaz: URL completa da SEFAZ
    - cert_id: ID do certificado
    - authorization: Token Bearer
    - body: corpo da requisição (opcional)
    - method: GET, POST, PUT, etc (padrão: POST)
    """
    
    form_data = await request.form()
    
    url_sefaz = form_data.get("url_sefaz")
    cert_id = int(form_data.get("cert_id"))
    authorization = form_data.get("authorization")
    body = form_data.get("body", "")
    method = form_data.get("method", "POST").upper()
    
    if not url_sefaz:
        raise HTTPException(status_code=400, detail="url_sefaz é obrigatório")
    
    # Validar token
    user_id = validar_token(authorization)
    
    # Obter certificado (com cache)
    cert_path, key_path = get_certificado_cached(user_id, cert_id)
    
    try:
        async with httpx.AsyncClient(
            cert=(cert_path, key_path),
            verify=True,
            timeout=30.0
        ) as client:
            
            # Fazer requisição conforme método
            if method == "GET":
                response = await client.get(url_sefaz)
            elif method == "POST":
                response = await client.post(
                    url_sefaz,
                    content=body,
                    headers={"Content-Type": "application/xml; charset=utf-8"}
                )
            else:
                raise HTTPException(status_code=400, detail=f"Método {method} não suportado")
            
            return {
                "status": "ok",
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "content": response.text
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")


@app.post("/sefaz/nfe/autorizar")
async def autorizar_nfe(
    uf: str = Form(...),
    ambiente: str = Form(...),
    xml_nfe: str = Form(...),
    cert_id: int = Form(...),
    authorization: str = Form(...)
):
    """
    Endpoint específico para autorização de NF-e
    Simplifica para o cliente não precisar saber a URL da SEFAZ
    """
    
    # Mapa de URLs (expansível)
    urls_nfe = {
        "homologacao": {
            "SP": "https://homologacao.nfe.fazenda.sp.gov.br/ws/nfeautorizacao4.asmx",
            "MG": "https://hnfe.fazenda.mg.gov.br/nfe2/services/NFeAutorizacao4",
            "RO": "https://hnfe.sefin.ro.gov.br/ws/NFeAutorizacao4/NFeAutorizacao4.asmx",
        },
        "producao": {
            "SP": "https://nfe.fazenda.sp.gov.br/ws/nfeautorizacao4.asmx",
            "MG": "https://nfe.fazenda.mg.gov.br/nfe2/services/NFeAutorizacao4",
            "RO": "https://nfe.sefin.ro.gov.br/ws/NFeAutorizacao4/NFeAutorizacao4.asmx",
        }
    }
    
    if ambiente not in urls_nfe or uf not in urls_nfe[ambiente]:
        raise HTTPException(status_code=400, detail="UF ou ambiente inválido")
    
    url_sefaz = urls_nfe[ambiente][uf]
    user_id = validar_token(authorization)
    
    # Usar cache de certificados
    cert_path, key_path = get_certificado_cached(user_id, cert_id)
    
    try:
        async with httpx.AsyncClient(
            cert=(cert_path, key_path),
            verify=True,
            timeout=30.0
        ) as client:
            
            response = await client.post(
                url_sefaz,
                content=xml_nfe,
                headers={
                    "Content-Type": "application/xml; charset=utf-8",
                    "SOAPAction": "http://www.portalfiscal.inf.br/nfe/wsdl/NFeAutorizacao4/nfeAutorizacaoLote"
                }
            )
            
            return {
                "status": "ok",
                "uf": uf,
                "ambiente": ambiente,
                "status_code": response.status_code,
                "xml_retorno": response.text
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao autorizar NF-e: {str(e)}")


@app.post("/sefaz/nfe/consultar")
async def consultar_nfe(
    uf: str = Form(...),
    ambiente: str = Form(...),
    chave_nfe: str = Form(...),
    cert_id: int = Form(...),
    authorization: str = Form(...)
):
    """Consulta protocolo de NF-e"""
    
    urls_consulta = {
        "homologacao": {
            "SP": "https://homologacao.nfe.fazenda.sp.gov.br/ws/nfeconsultaprotocolo4.asmx",
            "RO": "https://hnfe.sefin.ro.gov.br/ws/NFeConsultaProtocolo4/NFeConsultaProtocolo4.asmx",
        },
        "producao": {
            "SP": "https://nfe.fazenda.sp.gov.br/ws/nfeconsultaprotocolo4.asmx",
            "RO": "https://nfe.sefin.ro.gov.br/ws/NFeConsultaProtocolo4/NFeConsultaProtocolo4.asmx",
        }
    }
    
    if ambiente not in urls_consulta or uf not in urls_consulta[ambiente]:
        raise HTTPException(status_code=400, detail="UF ou ambiente inválido")
    
    # XML de consulta
    xml_consulta = f"""<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:nfe="http://www.portalfiscal.inf.br/nfe/wsdl/NFeConsultaProtocolo4">
    <soap:Body>
        <nfe:nfeDadosMsg>
            <consSitNFe xmlns="http://www.portalfiscal.inf.br/nfe" versao="4.00">
                <tpAmb>{1 if ambiente == 'producao' else 2}</tpAmb>
                <xServ>CONSULTAR</xServ>
                <chNFe>{chave_nfe}</chNFe>
            </consSitNFe>
        </nfe:nfeDadosMsg>
    </soap:Body>
</soap:Envelope>"""
    
    user_id = validar_token(authorization)
    cert_path, key_path = get_certificado_cached(user_id, cert_id)
    
    try:
        async with httpx.AsyncClient(
            cert=(cert_path, key_path),
            verify=True,
            timeout=30.0
        ) as client:
            
            response = await client.post(
                urls_consulta[ambiente][uf],
                content=xml_consulta,
                headers={"Content-Type": "application/xml; charset=utf-8"}
            )
            
            return {
                "status": "ok",
                "chave": chave_nfe,
                "xml_retorno": response.text
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar: {str(e)}")


@app.on_event("shutdown")
async def cleanup():
    """Limpa cache ao desligar"""
    for user_id, certs in CERT_CACHE.items():
        for cert_id, (cert_path, key_path, _) in certs.items():
            try:
                if os.path.exists(cert_path):
                    os.unlink(cert_path)
                if os.path.exists(key_path):
                    os.unlink(key_path)
            except:
                pass