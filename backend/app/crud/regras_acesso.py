from sqlalchemy.orm import Session
from fastapi import HTTPException
from backend.app.db.models import RegrasAcesso
from backend.app.schemas.regras_acesso import (
    RegraAcessoCreate,
    RegraAcessoUpdate,
)


class CRUDRegrasAcesso:

    def listar(self, db: Session):
        return db.query(RegrasAcesso).all()

    def listar_por_empresa(self, db: Session, empresa_id: int):
        return db.query(RegrasAcesso).filter(
            RegrasAcesso.empresa_id == empresa_id
        ).all()

    def listar_por_grupo(self, db: Session, grupo_id: int):
        return db.query(RegrasAcesso).filter(
            RegrasAcesso.grupo_id == grupo_id
        ).all()

    def get(self, db: Session, regra_id: int):
        regra = db.query(RegrasAcesso).filter(RegrasAcesso.regra_id == regra_id).first()
        if not regra:
            raise HTTPException(404, "Regra de acesso não encontrada")
        return regra

    def criar(self, db: Session, data: RegraAcessoCreate):

        nova = RegrasAcesso(
            empresa_id=data.empresa_id,
            grupo_id=data.grupo_id,
            tipo_dia=data.tipo_dia,
            dias_especificos=data.dias_especificos,
            horarios=data.horarios,   # SQLAlchemy lida com JSON automaticamente
        )

        db.add(nova)
        db.commit()
        db.refresh(nova)
        return nova

    def atualizar(self, db: Session, regra_id: int, data: RegraAcessoUpdate):
        regra = self.get(db, regra_id)

        updates = data.dict(exclude_unset=True)

        for campo, valor in updates.items():
            setattr(regra, campo, valor)

        db.commit()
        db.refresh(regra)
        return regra

    def deletar(self, db: Session, regra_id: int):
        regra = self.get(db, regra_id)
        db.delete(regra)
        db.commit()
        return {"status": "deleted"}


crud_regras_acesso = CRUDRegrasAcesso()
