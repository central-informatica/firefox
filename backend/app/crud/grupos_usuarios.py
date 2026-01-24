"""
CRUD operations for GruposUsuarios.

Note: User validation is now handled by the Auth microservice.
The usuario_id is trusted because it comes from the Auth service's validated session.
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException
from backend.app.db.models import GruposUsuarios
from backend.app.schemas.grupos_usuarios import (
    GrupoUsuarioCreate,
    GrupoUsuarioUpdate,
)


class CRUDGruposUsuarios:

    def listar(self, db: Session):
        return db.query(GruposUsuarios).all()

    def listar_por_grupo(self, db: Session, grupo_id: str):
        return db.query(GruposUsuarios).filter(
            GruposUsuarios.grupo_id == grupo_id
        ).all()

    def get(self, db: Session, grupo_usuario_id: str):
        registro = db.query(GruposUsuarios).filter(
            GruposUsuarios.grupo_usuario_id == grupo_usuario_id
        ).first()

        if not registro:
            raise HTTPException(404, "Associação grupo/usuário não encontrada.")

        return registro

    def criar(self, db: Session, data: GrupoUsuarioCreate):
        novo = GruposUsuarios(
            grupo_id=data.grupo_id,
            usuario_id=data.usuario_id,
            empresa_id=data.empresa_id,
        )

        db.add(novo)
        db.commit()
        db.refresh(novo)
        return novo

    def atualizar(self, db: Session, grupo_usuario_id: str, data: GrupoUsuarioUpdate):
        registro = self.get(db, grupo_usuario_id)

        updates = data.dict(exclude_unset=True)

        for campo, valor in updates.items():
            setattr(registro, campo, valor)

        db.commit()
        db.refresh(registro)
        return registro

    def deletar(self, db: Session, grupo_usuario_id: str):
        registro = self.get(db, grupo_usuario_id)
        db.delete(registro)
        db.commit()
        return {"status": "deleted"}

    def criar_bulk(self, db: Session, grupo_id: str, usuario_ids: list[str], empresa_id: str | None = None):
        """
        Create links between a grupo and multiple usuarios.

        Note: User validation is now handled by Auth service.
        The usuario_ids are trusted because they come from the Auth service.

        Returns:
            Dict with 'created' (list of created usuario_ids) and 'skipped' (list of dicts with reason)
        """
        created = []
        skipped = []

        for uid in usuario_ids:
            # Check if link already exists
            existente = db.query(GruposUsuarios).filter(
                GruposUsuarios.grupo_id == grupo_id,
                GruposUsuarios.usuario_id == uid
            ).first()

            if existente:
                skipped.append({"usuario_id": uid, "reason": "already_exists"})
                continue

            novo = GruposUsuarios(
                empresa_id=empresa_id,
                grupo_id=grupo_id,
                usuario_id=uid,
            )
            db.add(novo)
            created.append(uid)

        db.commit()
        return {"created": created, "skipped": skipped}


crud_grupos_usuarios = CRUDGruposUsuarios()
