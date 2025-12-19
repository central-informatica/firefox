from pydantic import BaseModel
from typing import Optional

class SignRequest(BaseModel):
    cert_id: str
    data: str 


class CertificadoBase(BaseModel):
    empresa_id: int
    senha: Optional[str] = None
    proprietario: Optional[str] = None
    emitido_por: Optional[str] = None
    validade_inicio: Optional[str] = None
    valido_ate: Optional[str] = None

class CertificadoCreate(CertificadoBase):
    pass

class CertificadoOut(CertificadoBase):
    id: int
    nome_arquivo: str
    criado_por: int
    criado_por_nome: str
    criado_em: str

    class Config:
        orm_mode = True

class CertificadoPermitidoResponse(BaseModel):
    certificado_id: int
    nome_arquivo: str
    empresa_id: int
    empresa_nome: str
    pode_acessar: bool

class ValidarAcessoCertificadoResponse(BaseModel):
    certificado_id: int
    permitido: bool