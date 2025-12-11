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

    def listar_por_empresa(self, db: Session, empresa_id: int):
        return db.query(GruposCertificados).filter(
            GruposCertificados.empresa_id == empresa_id
        ).all()

    def listar_por_grupo(self, db: Session, grupo_id: int):
        return db.query(GruposCertificados).filter(
            GruposCertificados.grupo_id == grupo_id
        ).all()

    def get(self, db: Session, grupo_cert_id: int):
        registro = db.query(GruposCertificados).filter(
            GruposCertificados.grupo_cert_id == grupo_cert_id
        ).first()

        if not registro:
            raise HTTPException(404, "Relação grupo/certificado não encontrada.")

        return registro

    def criar(self, db: Session, data: GrupoCertCreate):

        # Impedir duplicidade (unidade entre grupo e certificado)
        existente = db.query(GruposCertificados).filter(
            GruposCertificados.grupo_id == data.grupo_id,
            GruposCertificados.certificado_id == data.certificado_id
        ).first()

        if existente:
            raise HTTPException(
                400,
                "Este certificado já está vinculado a este grupo."
            )

        novo = GruposCertificados(
            empresa_id=data.empresa_id,
            grupo_id=data.grupo_id,
            certificado_id=data.certificado_id,
        )

        db.add(novo)
        db.commit()
        db.refresh(novo)
        return novo

    def atualizar(self, db: Session, grupo_cert_id: int, data: GrupoCertUpdate):
        registro = self.get(db, grupo_cert_id)

        updates = data.dict(exclude_unset=True)

        # Se grupo ou certificado mudar, verificar duplicidade novamente
        if ("grupo_id" in updates) or ("certificado_id" in updates):
            novo_grupo = updates.get("grupo_id", registro.grupo_id)
            novo_cert = updates.get("certificado_id", registro.certificado_id)

            existe = db.query(GruposCertificados).filter(
                GruposCertificados.grupo_id == novo_grupo,
                GruposCertificados.certificado_id == novo_cert,
                GruposCertificados.grupo_cert_id != grupo_cert_id
            ).first()

            if existe:
                raise HTTPException(
                    400,
                    "Já existe um vínculo entre este grupo e este certificado."
                )

        for campo, valor in updates.items():
            setattr(registro, campo, valor)

        db.commit()
        db.refresh(registro)
        return registro

    def deletar(self, db: Session, grupo_cert_id: int):
        registro = self.get(db, grupo_cert_id)
        db.delete(registro)
        db.commit()
        return {"status": "deleted"}


crud_grupos_certificados = CRUDGruposCertificados()
