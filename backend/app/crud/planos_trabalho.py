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
        plano = PlanosTrabalho(
            nome=data.nome,
            descricao=data.descricao,
            empresa_id=empresa_id,
        )

        db.add(plano)
        db.commit()
        db.refresh(plano)

        return plano


    def atualizar(self, db: Session, usuario_id: str, plano_id: str, data: PlanoTrabalhoUpdate):
        plano = self.getPlanoTrabalho(db, usuario_id=usuario_id, plano_id=plano_id)
        from sqlalchemy import inspect
        print("ANTES DO UPDATE:")
        print("plano:", plano)
        print("persistent:", inspect(plano).persistent)
        print("detached:", inspect(plano).detached)
        print("pending:", inspect(plano).pending)
        print("dirty:", inspect(plano).modified)

        if data.nome is not None:
            plano.nome = data.nome
        if data.descricao is not None:
            plano.descricao = data.descricao
        
        print("DEPOIS DO UPDATE:")
        print("dirty:", inspect(plano).modified)

        try:
            db.commit()
            db.refresh(plano)
            return plano
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Já existe um plano com este nome nesta empresa.")

    def deletar(self, db: Session, usuario_id: str, plano_id: str):
        plano = self.obter(db, usuario_id=usuario_id, plano_id=plano_id)

        db.delete(plano)
        db.commit()
        return {"status": "deleted"}


crud_planos_trabalho = CRUDPlanosTrabalho()