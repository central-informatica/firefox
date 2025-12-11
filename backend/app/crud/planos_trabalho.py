from sqlalchemy.orm import Session
from fastapi import HTTPException
from backend.app.db.models import PlanosTrabalho
from backend.app.schemas.planos_trabalho import (
    PlanoTrabalhoCreate,
    PlanoTrabalhoUpdate,
)


class CRUDPlanosTrabalho:

    def listar(self, db: Session):
        return db.query(PlanosTrabalho).all()

    def listar_por_empresa(self, db: Session, empresa_id: int):
        return db.query(PlanosTrabalho).filter(
            PlanosTrabalho.empresa_id == empresa_id
        ).all()

    def get(self, db: Session, plano_id: int):
        plano = db.query(PlanosTrabalho).filter(
            PlanosTrabalho.plano_id == plano_id
        ).first()

        if not plano:
            raise HTTPException(404, "Plano de trabalho não encontrado")

        return plano

    def criar(self, db: Session, data: PlanoTrabalhoCreate):

        # Evitar duplicidade: UNIQUE (empresa_id, nome)
        existente = db.query(PlanosTrabalho).filter(
            PlanosTrabalho.empresa_id == data.empresa_id,
            PlanosTrabalho.nome == data.nome
        ).first()

        if existente:
            raise HTTPException(
                400,
                "Já existe um plano de trabalho com este nome para esta empresa."
            )

        novo = PlanosTrabalho(
            empresa_id=data.empresa_id,
            nome=data.nome,
            descricao=data.descricao
        )

        db.add(novo)
        db.commit()
        db.refresh(novo)
        return novo

    def atualizar(self, db: Session, plano_id: int, data: PlanoTrabalhoUpdate):
        plano = self.get(db, plano_id)

        updates = data.dict(exclude_unset=True)

        # Verificar duplicidade se o nome for alterado
        if "nome" in updates:
            existe = db.query(PlanosTrabalho).filter(
                PlanosTrabalho.empresa_id == plano.empresa_id,
                PlanosTrabalho.nome == updates["nome"],
                PlanosTrabalho.plano_id != plano_id
            ).first()

            if existe:
                raise HTTPException(
                    400,
                    "Já existe outro plano de trabalho com este nome para esta empresa."
                )

        for campo, valor in updates.items():
            setattr(plano, campo, valor)

        db.commit()
        db.refresh(plano)
        return plano

    def deletar(self, db: Session, plano_id: int):
        plano = self.get(db, plano_id)
        db.delete(plano)
        db.commit()
        return {"status": "deleted"}


crud_planos_trabalho = CRUDPlanosTrabalho()
