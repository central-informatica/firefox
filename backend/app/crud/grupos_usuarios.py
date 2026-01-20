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


crud_grupos_usuarios = CRUDGruposUsuarios()
