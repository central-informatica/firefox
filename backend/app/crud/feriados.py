from sqlalchemy.orm import Session
from fastapi import HTTPException
from backend.app.db.models import Feriados
from backend.app.schemas.feriados import FeriadoCreate, FeriadoUpdate


class CRUDFeriados:

    def listar(self, db: Session):
        return db.query(Feriados).all()

    def get(self, db: Session, feriado_id: str):
        feriado = db.query(Feriados).filter(Feriados.feriado_id == feriado_id).first()
        if not feriado:
            raise HTTPException(404, "Feriado não encontrado")
        return feriado

    def criar(self, db: Session, data: FeriadoCreate):

        # Evitar duplicidade caso não seja recorrente
        existente = db.query(Feriados).filter(
            Feriados.data == data.data
        ).first()

        if existente:
            raise HTTPException(400, "Já existe um feriado cadastrado nesta data.")

        novo = Feriados(
            data=data.data,
            nome=data.nome,
            recorrente=data.recorrente,
            empresa_id=data.empresa_id,
        )

        db.add(novo)
        db.commit()
        db.refresh(novo)
        return novo

    def atualizar(self, db: Session, feriado_id: str, data: FeriadoUpdate):
        feriado = self.get(db, feriado_id)

        updates = data.dict(exclude_unset=True)

        # Se a data está sendo alterada, verificar duplicidade
        if "data" in updates:
            existe = db.query(Feriados).filter(
                Feriados.data == updates["data"],
                Feriados.feriado_id != feriado_id
            ).first()

            if existe:
                raise HTTPException(400, "Já existe um feriado nesta nova data.")

        for campo, valor in updates.items():
            setattr(feriado, campo, valor)

        db.commit()
        db.refresh(feriado)
        return feriado

    def deletar(self, db: Session, feriado_id: str):
        feriado = self.get(db, feriado_id)
        db.delete(feriado)
        db.commit()
        return {"status": "deleted"}


crud_feriados = CRUDFeriados()
