from sqlalchemy.orm import Session
from fastapi import HTTPException
from backend.app.db.models import Empresas
from backend.app.schemas.empresas import EmpresaCreate, EmpresaUpdate


class CRUDEmpresas:

    def listar(self, db: Session):
        return db.query(Empresas).all()

    def get(self, db: Session, empresa_id: int):
        emp = db.query(Empresas).filter(Empresas.empresa_id == empresa_id).first()
        if not emp:
            raise HTTPException(404, "Empresa não encontrada")
        return emp

    def criar(self, db: Session, data: EmpresaCreate):
        # Verificar duplicidade de CNPJ
        existente = (
            db.query(Empresas)
              .filter(Empresas.cnpj == data.cnpj)
              .first()
        )

        if existente:
            raise HTTPException(400, "Já existe uma empresa cadastrada com este CNPJ.")

        nova = Empresas(
            razao_social=data.razao_social,
            fantasia=data.fantasia,
            cnpj=data.cnpj,
            anfitria_usuario_id=data.anfitria_usuario_id,
            timezone=data.timezone,
        )

        db.add(nova)
        db.commit()
        db.refresh(nova)
        return nova

    def atualizar(self, db: Session, empresa_id: int, data: EmpresaUpdate):
        empresa = self.get(db, empresa_id)

        if data.razao_social is not None:
            empresa.razao_social = data.razao_social

        if data.fantasia is not None:
            empresa.fantasia = data.fantasia

        if data.timezone is not None:
            empresa.timezone = data.timezone

        db.commit()
        db.refresh(empresa)
        return empresa

    def deletar(self, db: Session, empresa_id: int):
        empresa = self.get(db, empresa_id)
        db.delete(empresa)
        db.commit()
        return {"status": "deleted"}


crud_empresas = CRUDEmpresas()
