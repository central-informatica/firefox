from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException
from backend.app.db.models import Empresas, EmpresaMembros, Usuarios
from backend.app.schemas.empresas import EmpresaCreate, EmpresaUpdate
from backend.app.api.deps import get_current_user


class CRUDEmpresas:

    def listar_paginado_do_usuario(
        self,
        db: Session,
        usuario_id: int,
        page: int = 1,
        limit: int = 10,
        search: str = "",
        sort: str = "",
    ):
        # 1) Base tenant filter:
        # - empresas onde é anfitrião
        # - ou empresas onde é membro (empresa_membros)
        query = (
            db.query(Empresas)
            .outerjoin(
                EmpresaMembros,
                EmpresaMembros.empresa_id == Empresas.empresa_id
            )
            .filter(
                or_(
                    Empresas.anfitria_usuario_id == usuario_id,
                    EmpresaMembros.usuario_id == usuario_id,
                )
            )
            .distinct()
        )

        # 2) Search
        if search:
            s = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Empresas.razao_social.ilike(s),
                    Empresas.fantasia.ilike(s),
                    Empresas.cnpj.ilike(s),
                )
            )

        # 3) Total
        total = query.count()

        # 4) Sort (whitelist)
        if sort:
            try:
                field, direction = sort.split(".")
            except ValueError:
                raise HTTPException(400, "Parâmetro sort inválido. Use campo.asc ou campo.desc")

            allowed = {
                "empresa_id": Empresas.empresa_id,
                "razao_social": Empresas.razao_social,
                "fantasia": Empresas.fantasia,
                "cnpj": Empresas.cnpj,
                "timezone": Empresas.timezone,
                "criado_em": Empresas.criado_em,
            }

            col = allowed.get(field)
            if not col:
                raise HTTPException(400, f"Campo de sort não permitido: {field}")

            if direction not in ("asc", "desc"):
                raise HTTPException(400, "Direção de sort inválida. Use asc ou desc")

            query = query.order_by(col.asc() if direction == "asc" else col.desc())
        else:
            query = query.order_by(Empresas.empresa_id.desc())

        # 5) Pagination
        items = (
            query
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )

        return items, total


    #def listar(self, db: Session):
    #    return db.query(Empresas).all()

    def get(self, db: Session, empresa_id: int):
        emp = db.query(Empresas).filter(Empresas.empresa_id == empresa_id).first()
        if not emp:
            raise HTTPException(404, "Empresa não encontrada")
        return emp

    def criar(self, db: Session, data: EmpresaCreate, current_user: Usuarios,):
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
            anfitria_usuario_id=current_user.usuarios.usuario_id,
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
