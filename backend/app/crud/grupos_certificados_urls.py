"""CRUD operations for GruposCertificadosUrls."""

from sqlalchemy.orm import Session
from fastapi import HTTPException

from backend.app.db.models import GruposCertificadosUrls, GruposCertificados
from backend.app.schemas.grupos_certificados_urls import GrupoCertUrlCreate


class CRUDGruposCertificadosUrls:

    def listar_por_grupo_cert(self, db: Session, grupo_cert_id: str):
        """List all URLs for a grupo-certificado."""
        return db.query(GruposCertificadosUrls).filter(
            GruposCertificadosUrls.grupo_cert_id == grupo_cert_id
        ).all()

    def get(self, db: Session, grupo_cert_url_id: str):
        """Get a specific grupo-certificado URL by ID."""
        registro = db.query(GruposCertificadosUrls).filter(
            GruposCertificadosUrls.grupo_cert_url_id == grupo_cert_url_id
        ).first()

        if not registro:
            raise HTTPException(404, "Relacao grupo-certificado/URL nao encontrada.")

        return registro

    def criar(self, db: Session, grupo_cert_id: str, data: GrupoCertUrlCreate, empresa_id: str):
        """Add a URL to a grupo-certificado."""
        # Verify grupo_cert exists
        grupo_cert = db.query(GruposCertificados).filter(
            GruposCertificados.grupo_cert_id == grupo_cert_id
        ).first()

        if not grupo_cert:
            raise HTTPException(404, "Relacao grupo-certificado nao encontrada.")

        # Check for duplicate
        existing = db.query(GruposCertificadosUrls).filter(
            GruposCertificadosUrls.grupo_cert_id == grupo_cert_id,
            GruposCertificadosUrls.global_urls_id == data.global_urls_id
        ).first()

        if existing:
            raise HTTPException(409, "Esta URL ja esta associada a este grupo-certificado.")

        novo = GruposCertificadosUrls(
            grupo_cert_id=grupo_cert_id,
            global_urls_id=data.global_urls_id,
            empresa_id=empresa_id,
        )

        db.add(novo)
        db.commit()
        db.refresh(novo)
        return novo

    def deletar(self, db: Session, grupo_cert_url_id: str):
        """Remove a URL from a grupo-certificado."""
        registro = self.get(db, grupo_cert_url_id)
        db.delete(registro)
        db.commit()
        return {"status": "deleted"}

    def listar_urls_acessiveis_por_usuario(self, db: Session, usuario_id: str, empresa_id: str):
        """List all URLs accessible by a user based on their group memberships."""
        from sqlalchemy import select
        from backend.app.db.models import GruposUsuarios, GlobalUrls

        # Subquery: grupos the user belongs to
        user_grupos = select(GruposUsuarios.grupo_id).where(
            GruposUsuarios.usuario_id == usuario_id,
            GruposUsuarios.empresa_id == empresa_id
        ).scalar_subquery()

        # Subquery: grupo_cert_ids for those grupos
        grupo_certs = select(GruposCertificados.grupo_cert_id).where(
            GruposCertificados.grupo_id.in_(user_grupos),
            GruposCertificados.empresa_id == empresa_id
        ).scalar_subquery()

        # Query URLs with GlobalUrls join
        results = db.query(
            GruposCertificadosUrls.grupo_cert_url_id,
            GruposCertificadosUrls.grupo_cert_id,
            GruposCertificadosUrls.global_urls_id,
            GlobalUrls.url
        ).join(
            GlobalUrls, GruposCertificadosUrls.global_urls_id == GlobalUrls.global_urls_id
        ).filter(
            GruposCertificadosUrls.grupo_cert_id.in_(grupo_certs),
            GlobalUrls.inativo == False
        ).all()

        return results


crud_grupos_certificados_urls = CRUDGruposCertificadosUrls()
