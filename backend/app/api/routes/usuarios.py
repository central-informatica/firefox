from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.db.database import get_db
from backend.app.db.models import Empresas, EmpresaMembros

router = APIRouter(prefix="/usuarios", tags=["Usuários"])

@router.get("/{user_id}/empresas")
def get_empresas_do_usuario(user_id: int, db: Session = Depends(get_db)):
    empresas = (
        db.query(Empresas)
        .join(EmpresaMembros, EmpresaMembros.empresa_id == Empresas.empresa_id)
        .filter(EmpresaMembros.usuario_id == user_id)
        .all()
    )
    return empresas
