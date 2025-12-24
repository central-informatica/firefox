import secrets
import base64
from datetime import datetime, timedelta
from typing import Dict
from argon2 import PasswordHasher
from argon2.low_level import Type
from sqlalchemy.orm import Session
from backend.app.db.models import Usuarios, EmpresaMembros, Empresas

TOKEN_HASHER = PasswordHasher(
    time_cost=2,           
    memory_cost=65536,     
    parallelism=4,         
    hash_len=32,         
    salt_len=16,         
    type=Type.ID         
)


def generate_opaque_token() -> tuple[str, str, str]:
    selector_bytes = secrets.token_bytes(32)
    selector = base64.urlsafe_b64encode(selector_bytes).decode('utf-8').rstrip('=')

    validator_bytes = secrets.token_bytes(32)
    validator = base64.urlsafe_b64encode(validator_bytes).decode('utf-8').rstrip('=')


    full_token = f"{selector}.{validator}"

    return full_token, selector, validator


def hash_validator(validator: str) -> str:
    return TOKEN_HASHER.hash(validator)


def verify_validator(validator_hash: str, validator: str) -> bool:
    
    try:
        TOKEN_HASHER.verify(validator_hash, validator)
        return True
    except Exception:
        return False


def build_permissions(db: Session, usuario_id: int) -> Dict:
    user = db.query(Usuarios).filter(Usuarios.usuario_id == usuario_id).first()
    if not user:
        raise ValueError(f"User with ID {usuario_id} not found")

    memberships = (
        db.query(EmpresaMembros, Empresas)
        .join(Empresas, EmpresaMembros.empresa_id == Empresas.empresa_id)
        .filter(EmpresaMembros.usuario_id == usuario_id)
        .all()
    )
    return {
        "usuario_nivel": user.nivel,
        "empresas": [
            {
                "empresa_id": m.EmpresaMembros.empresa_id,
                "papel": m.EmpresaMembros.papel,
                "razao_social": m.Empresas.razao_social,
                "cnpj": m.Empresas.cnpj
            }
            for m in memberships
        ],
        "metadata": {
            "cached_at": datetime.utcnow().isoformat() + "Z",
            "version": 1
        }
    }


def calculate_token_expiration(minutes: int = 15) -> datetime:
    return datetime.utcnow() + timedelta(minutes=minutes)
