from sqlalchemy.orm import Session
from fastapi import HTTPException
from backend.app.db.models import RegrasAcessoHosts
from backend.app.schemas.regras_acesso_hosts import (
    RegraAcessoHostCreate,
    RegraAcessoHostUpdate,
)
from backend.app.enums.tipo_dia import TipoDiaEnum


class CRUDRegrasAcessoHosts:

    def listar(self, db: Session):
        return db.query(RegrasAcessoHosts).all()

    def listar_por_grupo(self, db: Session, grupo_id: str):
        return (
            db.query(RegrasAcessoHosts)
            .filter(RegrasAcessoHosts.grupo_id == grupo_id)
            .all()
        )

    def get(self, db: Session, regra_id: str):
        regra = (
            db.query(RegrasAcessoHosts)
            .filter(RegrasAcessoHosts.regra_id == regra_id)
            .first()
        )
        if not regra:
            raise HTTPException(404, "Regra de acesso (host) não encontrada")
        return regra

    def criar(self, db: Session, data: RegraAcessoHostCreate):

        nova = RegrasAcessoHosts(
            grupo_id=data.grupo_id,
            tipo_dia=data.tipo_dia,
            dias_especificos=data.dias_especificos,
            horarios=data.horarios,
            urls=data.urls,
        )

        db.add(nova)
        db.commit()
        db.refresh(nova)
        return nova

    def atualizar(self, db: Session, regra_id: str, data: RegraAcessoHostUpdate):
        regra = self.get(db, regra_id)

        updates = data.dict(exclude_unset=True)

        # Validação extra para tipo_dia/especificos
        if "tipo_dia" in updates:
            novo_tipo = updates["tipo_dia"]
            if novo_tipo == TipoDiaEnum.especificos:
                if (
                    "dias_especificos" not in updates
                    and not regra.dias_especificos
                ):
                    raise HTTPException(
                        400,
                        "dias_especificos é obrigatório quando tipo_dia = 'especificos'"
                    )

        for campo, valor in updates.items():
            setattr(regra, campo, valor)

        db.commit()
        db.refresh(regra)
        return regra

    def deletar(self, db: Session, regra_id: str):
        regra = self.get(db, regra_id)
        db.delete(regra)
        db.commit()
        return {"status": "deleted"}


crud_regras_acesso_hosts = CRUDRegrasAcessoHosts()
