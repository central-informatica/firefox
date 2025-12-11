from sqlalchemy.orm import Session
from fastapi import HTTPException
#from backend.app.models.empresa_membros import EmpresaMembro
from backend.app.db.models import EmpresaMembro
from backend.app.schemas.empresa_membros import EmpresaMembroCreate, EmpresaMembroUpdate

class CRUDEmpresaMembro:

    def get(self, db: Session, membro_id: int):
        membro = db.query(EmpresaMembro).filter(EmpresaMembro.membro_id == membro_id).first()
        if not membro:
            raise HTTPException(404, "Membro não encontrado")
        return membro

    def get_by_empresa(self, db: Session, empresa_id: int):
        return db.query(EmpresaMembro).filter(EmpresaMembro.empresa_id == empresa_id).all()

    def create(self, db: Session, data: EmpresaMembroCreate):
        # Respeita UNIQUE (empresa_id, usuario_id)
        existente = db.query(EmpresaMembro).filter(
            EmpresaMembro.empresa_id == data.empresa_id,
            EmpresaMembro.usuario_id == data.usuario_id,
        ).first()

        if existente:
            raise HTTPException(400, "Usuário já é membro desta empresa")

        membro = EmpresaMembro(
            empresa_id=data.empresa_id,
            usuario_id=data.usuario_id,
            papel=data.papel,
        )
        db.add(membro)
        db.commit()
        db.refresh(membro)
        return membro

    def update(self, db: Session, membro_id: int, data: EmpresaMembroUpdate):
        membro = self.get(db, membro_id)

        if data.papel:
            membro.papel = data.papel

        db.commit()
        db.refresh(membro)
        return membro

    def delete(self, db: Session, membro_id: int):
        membro = self.get(db, membro_id)
        db.delete(membro)
        db.commit()
        return {"status": "deleted"}

crud_empresa_membros = CRUDEmpresaMembro()
