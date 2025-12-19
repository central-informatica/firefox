from sqlalchemy.orm import Session
from fastapi import HTTPException
from backend.app.db.models import EmpresaConvites
from backend.app.schemas.empresa_convites import (
    EmpresaConviteCreate,
    EmpresaConviteUpdate
)
from datetime import datetime


class CRUDEmpresaConvites:

    def listar(self, db: Session):
        return db.query(EmpresaConvites).all()

    def get(self, db: Session, convite_id: int):
        convite = db.query(EmpresaConvites).filter(
            EmpresaConvites.convite_id == convite_id
        ).first()

        if not convite:
            raise HTTPException(404, "Convite não encontrado")

        return convite

    def criar(self, db: Session, data: EmpresaConviteCreate):

        # Evita convites duplicados para o mesmo e-mail
        existente = db.query(EmpresaConvites).filter(
            EmpresaConvites.empresa_id == data.empresa_id,
            EmpresaConvites.email_convidado == data.email_convidado,
            EmpresaConvites.status == "pendente"
        ).first()

        if existente:
            raise HTTPException(
                400, "Já existe um convite pendente para este e-mail."
            )

        novo = EmpresaConvites(
            empresa_id=data.empresa_id,
            email_convidado=data.email_convidado,
        )

        db.add(novo)
        db.commit()
        db.refresh(novo)
        return novo

    def atualizar(self, db: Session, convite_id: int, data: EmpresaConviteUpdate):
        convite = self.get(db, convite_id)

        if data.status:
            convite.status = data.status

        if data.convidado_usuario_id:
            convite.convidado_usuario_id = data.convidado_usuario_id

        db.commit()
        db.refresh(convite)
        return convite

    def deletar(self, db: Session, convite_id: int):
        convite = self.get(db, convite_id)
        db.delete(convite)
        db.commit()
        return {"status": "deleted"}


crud_empresa_convites = CRUDEmpresaConvites()
