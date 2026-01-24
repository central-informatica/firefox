from sqlalchemy.orm import Session
from fastapi import HTTPException
from backend.app.db.models import GruposCertificados
from backend.app.schemas.grupos_certificados import (
    GrupoCertCreate,
    GrupoCertUpdate,
)


class CRUDGruposCertificados:

    def listar(self, db: Session):
        return db.query(GruposCertificados).all()

    def listar_por_grupo(self, db: Session, grupo_id: str):
        return db.query(GruposCertificados).filter(
            GruposCertificados.grupo_id == grupo_id
        ).all()

    def get(self, db: Session, grupo_cert_id: str):
        registro = db.query(GruposCertificados).filter(
            GruposCertificados.grupo_cert_id == grupo_cert_id
        ).first()

        if not registro:
            raise HTTPException(404, "Relação grupo/certificado não encontrada.")

        return registro

    def criar(self, db: Session, data: GrupoCertCreate):
        novo = GruposCertificados(
            grupo_id=data.grupo_id,
        )

        db.add(novo)
        db.commit()
        db.refresh(novo)
        return novo

    def atualizar(self, db: Session, grupo_cert_id: str, data: GrupoCertUpdate):
        registro = self.get(db, grupo_cert_id)

        updates = data.dict(exclude_unset=True)

        for campo, valor in updates.items():
            setattr(registro, campo, valor)

        db.commit()
        db.refresh(registro)
        return registro

    def deletar(self, db: Session, grupo_cert_id: str):
        registro = self.get(db, grupo_cert_id)
        db.delete(registro)
        db.commit()
        return {"status": "deleted"}


crud_grupos_certificados = CRUDGruposCertificados()
