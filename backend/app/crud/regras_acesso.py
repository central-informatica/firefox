from sqlalchemy.orm import Session
from fastapi import HTTPException
from backend.app.db.models import RegrasAcesso
from backend.app.schemas.regras_acesso import (
    RegraAcessoCreate,
    RegraAcessoUpdate,
)
from backend.app.enums.tipo_dia import TipoDiaEnum


class CRUDRegrasAcesso:

    def listar(self, db: Session):
        """Lista todas as regras de acesso."""
        return db.query(RegrasAcesso).all()

    def listar_por_grupo(self, db: Session, grupo_id: int):
        """Lista regras aplicadas a um grupo específico."""
        return (
            db.query(RegrasAcesso)
            .filter(RegrasAcesso.grupo_id == grupo_id)
            .all()
        )

    def get(self, db: Session, regra_id: int):
        """Busca uma regra pelo ID."""
        regra = (
            db.query(RegrasAcesso)
            .filter(RegrasAcesso.regra_id == regra_id)
            .first()
        )

        if not regra:
            raise HTTPException(404, "Regra de acesso não encontrada")

        return regra

    def criar(self, db: Session, data: RegraAcessoCreate):
        """Cria uma nova regra de acesso."""

        # Criação direta, tipos JSONB e ARRAY são aceitos naturalmente
        nova = RegrasAcesso(
            grupo_id=data.grupo_id,
            tipo_dia=data.tipo_dia,  # Enum Python → Enum PG automaticamente
            dias_especificos=data.dias_especificos,
            horarios=data.horarios,
        )

        db.add(nova)
        db.commit()
        db.refresh(nova)
        return nova

    def atualizar(self, db: Session, regra_id: int, data: RegraAcessoUpdate):
        """Atualiza uma regra de forma parcial."""
        regra = self.get(db, regra_id)

        updates = data.dict(exclude_unset=True)

        # Se tipo_dia mudar,
        # validar se dias_especificos permanece consistente
        if "tipo_dia" in updates:
            novo_tipo = updates["tipo_dia"]

            if novo_tipo == TipoDiaEnum.especificos:
                # Exige lista de dias
                if (
                    "dias_especificos" not in updates
                    and not regra.dias_especificos
                ):
                    raise HTTPException(
                        400,
                        "dias_especificos é obrigatório quando tipo_dia = 'especificos'",
                    )

        # Aplicar updates
        for campo, valor in updates.items():
            setattr(regra, campo, valor)

        db.commit()
        db.refresh(regra)
        return regra

    def deletar(self, db: Session, regra_id: int):
        """Remove uma regra do banco."""
        regra = self.get(db, regra_id)
        db.delete(regra)
        db.commit()
        return {"status": "deleted"}


crud_regras_acesso = CRUDRegrasAcesso()
