from sqlalchemy.orm import Session
from fastapi import HTTPException
from backend.app.db.models import RegrasAcessoIps, Grupos
from backend.app.schemas.regras_acesso_ips import (
    RegraAcessoIpsCreate,
    RegraAcessoIpsCreateBulk,
    RegraAcessoIpsUpdate,
)
from backend.app.enums.tipo_dia import TipoDiaEnum


class CRUDRegrasAcessoIps:

    def listar(self, db: Session):
        """Lista todas as regras de acesso IPs."""
        return db.query(RegrasAcessoIps).all()

    def listar_por_empresa(self, db: Session, empresa_id: str, page: int = 1, limit: int = 10, search: str = ""):
        """Lista regras de acesso IPs de uma empresa com paginação."""
        query = db.query(RegrasAcessoIps).filter(RegrasAcessoIps.empresa_id == empresa_id)

        if search:
            # Busca por IP
            query = query.filter(RegrasAcessoIps.ip_address.ilike(f"%{search}%"))

        total = query.count()
        offset = (page - 1) * limit
        items = query.order_by(RegrasAcessoIps.criado_em.desc()).offset(offset).limit(limit).all()

        return {
            "data": items,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit if limit > 0 else 0
        }

    def listar_por_grupo(self, db: Session, grupo_id: str):
        """Lista regras aplicadas a um grupo específico."""
        return (
            db.query(RegrasAcessoIps)
            .filter(RegrasAcessoIps.grupo_id == grupo_id)
            .all()
        )

    def listar_por_ip(self, db: Session, ip_address: str):
        """Lista regras aplicadas a um IP específico."""
        return (
            db.query(RegrasAcessoIps)
            .filter(RegrasAcessoIps.ip_address == ip_address)
            .all()
        )

    def get(self, db: Session, regra_id: str):
        """Busca uma regra pelo ID."""
        regra = (
            db.query(RegrasAcessoIps)
            .filter(RegrasAcessoIps.regra_id == regra_id)
            .first()
        )

        if not regra:
            raise HTTPException(404, "Regra de acesso IP não encontrada")

        return regra

    def criar(self, db: Session, data: RegraAcessoIpsCreate):
        """Cria uma nova regra de acesso IP."""

        # Validar que o grupo existe e pertence à empresa
        grupo = db.query(Grupos).filter(Grupos.grupo_id == data.grupo_id).first()
        if not grupo:
            raise HTTPException(404, "Grupo não encontrado")
        if str(grupo.empresa_id) != str(data.empresa_id):
            raise HTTPException(400, "O grupo não pertence à empresa informada")

        # Verificar se já existe uma regra para este grupo+IP
        existente = (
            db.query(RegrasAcessoIps)
            .filter(
                RegrasAcessoIps.grupo_id == data.grupo_id,
                RegrasAcessoIps.ip_address == data.ip_address
            )
            .first()
        )
        if existente:
            raise HTTPException(400, "Já existe uma regra de acesso para este grupo e IP")

        # Criação direta, tipos JSONB e ARRAY são aceitos naturalmente
        nova = RegrasAcessoIps(
            empresa_id=data.empresa_id,
            grupo_id=data.grupo_id,
            ip_address=data.ip_address,
            tipo_dia=data.tipo_dia,
            dias_especificos=data.dias_especificos,
            horarios=data.horarios,
            bloquear_em_feriado=data.bloquear_em_feriado or False,
            ativo=data.ativo if data.ativo is not None else True,
        )

        db.add(nova)
        db.commit()
        db.refresh(nova)
        return nova

    def criar_bulk(self, db: Session, data: RegraAcessoIpsCreateBulk):
        """Cria regras de acesso IP para múltiplos grupos."""

        criadas = []
        erros = []

        for grupo_id in data.grupo_ids:
            # Validar que o grupo existe e pertence à empresa
            grupo = db.query(Grupos).filter(Grupos.grupo_id == grupo_id).first()
            if not grupo:
                erros.append(f"Grupo {grupo_id} não encontrado")
                continue
            if str(grupo.empresa_id) != str(data.empresa_id):
                erros.append(f"Grupo {grupo.nome} não pertence à empresa informada")
                continue

            # Verificar se já existe uma regra para este grupo+IP
            existente = (
                db.query(RegrasAcessoIps)
                .filter(
                    RegrasAcessoIps.grupo_id == grupo_id,
                    RegrasAcessoIps.ip_address == data.ip_address
                )
                .first()
            )
            if existente:
                erros.append(f"Já existe regra para o grupo {grupo.nome}")
                continue

            # Criar a regra
            nova = RegrasAcessoIps(
                empresa_id=data.empresa_id,
                grupo_id=grupo_id,
                ip_address=data.ip_address,
                tipo_dia=data.tipo_dia,
                dias_especificos=data.dias_especificos,
                horarios=data.horarios,
                bloquear_em_feriado=data.bloquear_em_feriado or False,
                ativo=data.ativo if data.ativo is not None else True,
            )
            db.add(nova)
            criadas.append(nova)

        if criadas:
            db.commit()
            for regra in criadas:
                db.refresh(regra)

        return {
            "criadas": criadas,
            "total_criadas": len(criadas),
            "erros": erros if erros else None
        }

    def atualizar(self, db: Session, regra_id: str, data: RegraAcessoIpsUpdate):
        """Atualiza uma regra de forma parcial."""
        regra = self.get(db, regra_id)

        updates = data.model_dump(exclude_unset=True)

        # Se tipo_dia mudar, validar se dias_especificos permanece consistente
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

    def toggle_ativo(self, db: Session, regra_id: str):
        """Alterna o estado ativo/inativo de uma regra."""
        regra = self.get(db, regra_id)
        regra.ativo = not regra.ativo
        db.commit()
        db.refresh(regra)
        return regra

    def deletar(self, db: Session, regra_id: str):
        """Remove uma regra do banco."""
        regra = self.get(db, regra_id)
        db.delete(regra)
        db.commit()
        return {"status": "deleted"}


crud_regras_acesso_ips = CRUDRegrasAcessoIps()
