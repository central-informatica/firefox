"""
CRUD operations for GlobalUrls.

Note: empresa_id validation is now handled by the Auth microservice.
The empresa_id is trusted because it comes from the Auth service's /me endpoint.
"""

from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException
from backend.app.db.models import GlobalUrls
from backend.app.schemas.global_urls import GlobalUrlCreate, GlobalUrlUpdate


class CRUDGlobalUrls:

    def listar_paginado(
        self,
        db: Session,
        empresa_id: str,
        page: int = 1,
        limit: int = 10,
        search: str = "",
        sort: str = "",
    ):
        query = db.query(GlobalUrls).filter(GlobalUrls.empresa_id == empresa_id)

        if search:
            s = f"%{search.strip()}%"
            query = query.filter(GlobalUrls.url.ilike(s))

        total = query.count()

        if sort:
            try:
                field, direction = sort.split(".")
            except ValueError:
                raise HTTPException(400, "Parâmetro sort inválido. Use campo.asc ou campo.desc")

            allowed = {
                "global_urls_id": GlobalUrls.global_urls_id,
                "url": GlobalUrls.url,
                "criado_em": GlobalUrls.criado_em,
                "inativo": GlobalUrls.inativo,
            }

            col = allowed.get(field)
            if not col:
                raise HTTPException(400, f"Campo de sort não permitido: {field}")

            if direction not in ("asc", "desc"):
                raise HTTPException(400, "Direção de sort inválida. Use asc ou desc")

            query = query.order_by(col.asc() if direction == "asc" else col.desc())
        else:
            query = query.order_by(GlobalUrls.global_urls_id.desc())

        items = (
            query
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )

        return items, total

    def get(self, db: Session, global_urls_id: str):
        url = db.query(GlobalUrls).filter(GlobalUrls.global_urls_id == global_urls_id).first()
        if not url:
            raise HTTPException(404, "URL não encontrada")
        return url

    def criar(self, db: Session, data: GlobalUrlCreate):
        # Note: empresa_id validation is now handled by Auth service
        # The empresa_id is trusted because it comes from authenticated user's session

        nova = GlobalUrls(
            url=data.url,
            inativo=data.inativo,
            empresa_id=data.empresa_id,
        )

        db.add(nova)
        db.commit()
        db.refresh(nova)
        return nova

    def atualizar(self, db: Session, global_urls_id: str, data: GlobalUrlUpdate):
        url = self.get(db, global_urls_id)

        if data.url is not None:
            url.url = data.url

        if data.inativo is not None:
            url.inativo = data.inativo

        db.commit()
        db.refresh(url)
        return url

    def deletar(self, db: Session, global_urls_id: str):
        url = self.get(db, global_urls_id)
        db.delete(url)
        db.commit()
        return {"status": "deleted"}


crud_global_urls = CRUDGlobalUrls()
