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

    def listar_por_grupo(self, db: Session, grupo_id: int):
        return db.query(GruposUsuarios).filter(
            GruposUsuarios.grupo_id == grupo_id
        ).all()

    def get(self, db: Session, grupo_usuario_id: int):
        registro = db.query(GruposUsuarios).filter(
            GruposUsuarios.grupo_usuario_id == grupo_usuario_id
        ).first()

        if not registro:
            raise HTTPException(404, "Associação grupo/usuário não encontrada.")

        return registro

    def criar(self, db: Session, data: GrupoUsuarioCreate):
        novo = GruposUsuarios(
            grupo_id=data.grupo_id,
        )

        db.add(novo)
        db.commit()
        db.refresh(novo)
        return novo

    def atualizar(self, db: Session, grupo_usuario_id: int, data: GrupoUsuarioUpdate):
        registro = self.get(db, grupo_usuario_id)

        updates = data.dict(exclude_unset=True)

        for campo, valor in updates.items():
            setattr(registro, campo, valor)

        db.commit()
        db.refresh(registro)
        return registro

    def deletar(self, db: Session, grupo_usuario_id: int):
        registro = self.get(db, grupo_usuario_id)
        db.delete(registro)
        db.commit()
        return {"status": "deleted"}

    def criar_bulk(self, db: Session, grupo_id: int, usuario_ids: list[int], empresa_id: int | None = None):
        """Cria vínculos entre um grupo e múltiplos usuários. Retorna resumo com criados e pulados."""
        from backend.app.db.models import Usuarios, GruposUsuarios

        created = []
        skipped = []

        # Validar existência do grupo (opcional: assumimos que grupo existe em outro CRUD)
        # Validar cada usuário e criar vínculo se não existir
        for uid in usuario_ids:
            usuario = db.query(Usuarios).filter(Usuarios.usuario_id == uid).first()
            if not usuario:
                skipped.append({"usuario_id": uid, "reason": "user_not_found"})
                continue

            existente = db.query(GruposUsuarios).filter(
                GruposUsuarios.grupo_id == grupo_id,
                GruposUsuarios.usuario_id == uid
            ).first()

            if existente:
                skipped.append({"usuario_id": uid, "reason": "already_exists"})
                continue

            novo = GruposUsuarios(
                empresa_id=empresa_id if empresa_id is not None else (usuario.empresa_id if hasattr(usuario, 'empresa_id') else None),
                grupo_id=grupo_id,
                usuario_id=uid,
            )
            db.add(novo)
            created.append(uid)

        db.commit()
        return {"created": created, "skipped": skipped}


crud_grupos_usuarios = CRUDGruposUsuarios()
