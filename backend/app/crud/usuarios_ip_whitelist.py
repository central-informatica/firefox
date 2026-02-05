"""
CRUD operations for UsuariosIpWhitelist.

Manages IP address whitelist entries per user per empresa.
"""

import datetime

from sqlalchemy.orm import Session
from fastapi import HTTPException
from backend.app.db.models import UsuariosIpWhitelist
from backend.app.schemas.usuarios_ip_whitelist import (
    UsuarioIpWhitelistCreate,
    UsuarioIpWhitelistUpdate,
)


class CRUDUsuariosIpWhitelist:

    def listar_por_empresa(self, db: Session, empresa_id: str):
        """List all whitelist entries for an empresa (excluding deleted)."""
        return db.query(UsuariosIpWhitelist).filter(
            UsuariosIpWhitelist.empresa_id == empresa_id,
            UsuariosIpWhitelist.deleted_at.is_(None)
        ).all()

    def listar_por_usuario(self, db: Session, usuario_id: str, empresa_id: str):
        """List all whitelist entries for a specific user in an empresa (excluding deleted)."""
        return db.query(UsuariosIpWhitelist).filter(
            UsuariosIpWhitelist.usuario_id == usuario_id,
            UsuariosIpWhitelist.empresa_id == empresa_id,
            UsuariosIpWhitelist.deleted_at.is_(None)
        ).all()

    def get(self, db: Session, whitelist_id: str):
        """Get a specific whitelist entry by ID (excluding deleted)."""
        entry = db.query(UsuariosIpWhitelist).filter(
            UsuariosIpWhitelist.whitelist_id == whitelist_id,
            UsuariosIpWhitelist.deleted_at.is_(None)
        ).first()

        if not entry:
            raise HTTPException(404, "Entrada de IP whitelist nao encontrada.")

        return entry

    def verificar_ip_permitido(
        self,
        db: Session,
        usuario_id: str,
        empresa_id: str,
        ip_address: str
    ) -> bool:
        """
        Check if a user+IP combination is allowed for the given empresa.

        Uses permissive mode: if no IPs are whitelisted for the user+empresa,
        all IPs are allowed. If at least one IP is whitelisted, only those IPs
        are allowed.

        Returns:
            True if the IP is allowed, False otherwise.
        """
        # First, check if there are ANY whitelist entries for this user+empresa
        any_entries = db.query(UsuariosIpWhitelist).filter(
            UsuariosIpWhitelist.usuario_id == usuario_id,
            UsuariosIpWhitelist.empresa_id == empresa_id,
            UsuariosIpWhitelist.deleted_at.is_(None)
        ).first()

        # If no entries exist, allow all IPs (permissive mode)
        if any_entries is None:
            return True

        # If entries exist, check if the specific IP is whitelisted
        entry = db.query(UsuariosIpWhitelist).filter(
            UsuariosIpWhitelist.usuario_id == usuario_id,
            UsuariosIpWhitelist.empresa_id == empresa_id,
            UsuariosIpWhitelist.ip_address == ip_address,
            UsuariosIpWhitelist.deleted_at.is_(None)
        ).first()

        return entry is not None

    def criar(self, db: Session, data: UsuarioIpWhitelistCreate, criado_por: str):
        """Create a new whitelist entry."""
        # Check for duplicate (excluding deleted)
        existing = db.query(UsuariosIpWhitelist).filter(
            UsuariosIpWhitelist.usuario_id == data.usuario_id,
            UsuariosIpWhitelist.empresa_id == data.empresa_id,
            UsuariosIpWhitelist.ip_address == data.ip_address,
            UsuariosIpWhitelist.deleted_at.is_(None)
        ).first()

        if existing:
            raise HTTPException(409, "Esta combinacao usuario/empresa/IP ja existe.")

        novo = UsuariosIpWhitelist(
            usuario_id=data.usuario_id,
            empresa_id=data.empresa_id,
            ip_address=data.ip_address,
            descricao=data.descricao,
            criado_por=criado_por,
        )

        db.add(novo)
        db.commit()
        db.refresh(novo)
        return novo

    def atualizar(self, db: Session, whitelist_id: str, data: UsuarioIpWhitelistUpdate):
        """Update a whitelist entry."""
        entry = self.get(db, whitelist_id)

        updates = data.model_dump(exclude_unset=True)

        # Check for duplicate if IP is being changed (excluding deleted)
        if "ip_address" in updates:
            existing = db.query(UsuariosIpWhitelist).filter(
                UsuariosIpWhitelist.usuario_id == entry.usuario_id,
                UsuariosIpWhitelist.empresa_id == entry.empresa_id,
                UsuariosIpWhitelist.ip_address == updates["ip_address"],
                UsuariosIpWhitelist.whitelist_id != whitelist_id,
                UsuariosIpWhitelist.deleted_at.is_(None)
            ).first()

            if existing:
                raise HTTPException(409, "Esta combinacao usuario/empresa/IP ja existe.")

        for campo, valor in updates.items():
            setattr(entry, campo, valor)

        db.commit()
        db.refresh(entry)
        return entry

    def deletar(self, db: Session, whitelist_id: str, deleted_by: str):
        """Soft delete a whitelist entry."""
        entry = self.get(db, whitelist_id)
        entry.deleted_at = datetime.datetime.now(datetime.timezone.utc)
        entry.deleted_by = deleted_by
        db.commit()
        return {"status": "deleted"}

    def deletar_todos_por_usuario(self, db: Session, usuario_id: str, empresa_id: str, deleted_by: str):
        """Soft delete all whitelist entries for a user in an empresa."""
        entries = db.query(UsuariosIpWhitelist).filter(
            UsuariosIpWhitelist.usuario_id == usuario_id,
            UsuariosIpWhitelist.empresa_id == empresa_id,
            UsuariosIpWhitelist.deleted_at.is_(None)
        ).all()

        now = datetime.datetime.now(datetime.timezone.utc)
        for entry in entries:
            entry.deleted_at = now
            entry.deleted_by = deleted_by

        db.commit()
        return {"deleted_count": len(entries)}


crud_usuarios_ip_whitelist = CRUDUsuariosIpWhitelist()
