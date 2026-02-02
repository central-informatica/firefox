from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from backend.app.db.models import PlanosTrabalho
from backend.app.schemas.planos_trabalho import PlanoTrabalhoCreate, PlanoTrabalhoUpdate
from backend.app.crud.guards import exigir_acesso_empresa


class CRUDPlanosTrabalho:
    def listar(self, db, empresa_id, page, limit, search=None, sort=None):
        query = db.query(PlanosTrabalho).filter(
            PlanosTrabalho.empresa_id == empresa_id
        )

        total = query.count()

        items = (
            query
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )
        return items, total

    def getPlanoTrabalho(self, db: Session, usuario_id: str, plano_id: str):
        plano = db.query(PlanosTrabalho).filter(PlanosTrabalho.plano_id == plano_id).first()
        if not plano:
            raise HTTPException(status_code=404, detail="Plano não encontrado.")

        exigir_acesso_empresa(db, empresa_id=plano.empresa_id, usuario_id=usuario_id)
        return plano

    def criar(
        self,
        db: Session,
        data: PlanoTrabalhoCreate,
        empresa_id: str,
        usuario_id: str,
    ):
        # Check for duplicate name within empresa
        existing = db.query(PlanosTrabalho).filter(
            PlanosTrabalho.empresa_id == empresa_id,
            PlanosTrabalho.nome == data.nome
        ).first()

        if existing:
            raise HTTPException(
                status_code=409,  # Conflict
                detail="Já existe um plano com este nome nesta empresa."
            )

        plano = PlanosTrabalho(
            nome=data.nome,
            descricao=data.descricao,
            empresa_id=empresa_id,
        )

        db.add(plano)

        try:
            db.commit()
            db.refresh(plano)
            return plano
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=409, detail="Já existe um plano com este nome nesta empresa.")


    def atualizar(self, db: Session, usuario_id: str, plano_id: str, data: PlanoTrabalhoUpdate):
        plano = self.getPlanoTrabalho(db, usuario_id=usuario_id, plano_id=plano_id)

        if data.nome is not None:
            # Check for duplicate name within empresa (excluding current plano)
            existing = db.query(PlanosTrabalho).filter(
                PlanosTrabalho.empresa_id == plano.empresa_id,
                PlanosTrabalho.nome == data.nome,
                PlanosTrabalho.plano_id != plano_id
            ).first()

            if existing:
                raise HTTPException(status_code=409, detail="Já existe um plano com este nome nesta empresa.")

            plano.nome = data.nome

        if data.descricao is not None:
            plano.descricao = data.descricao

        try:
            db.commit()
            db.refresh(plano)
            return plano
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=409, detail="Já existe um plano com este nome nesta empresa.")

    def deletar(self, db: Session, usuario_id: str, plano_id: str):
        plano = self.getPlanoTrabalho(db, usuario_id=usuario_id, plano_id=plano_id)

        db.delete(plano)
        db.commit()
        return {"status": "deleted"}


crud_planos_trabalho = CRUDPlanosTrabalho()