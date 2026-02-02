from sqlalchemy.orm import Session
from fastapi import HTTPException
from backend.app.db.models import Ramos
from backend.app.schemas.ramos import RamoCreate, RamoUpdate


class CRUDRamos:

    def listar_todos(self, db: Session):
        """Lista todos os ramos de atuação."""
        return db.query(Ramos).order_by(Ramos.ramo).all()

    def listar_paginado(
        self,
        db: Session,
        page: int = 1,
        limit: int = 10,
        search: str = "",
        sort: str = "",
    ):
        query = db.query(Ramos)

        if search:
            s = f"%{search.strip()}%"
            query = query.filter(Ramos.ramo.ilike(s))

        total = query.count()

        if sort:
            try:
                field, direction = sort.split(".")
            except ValueError:
                raise HTTPException(400, "Parâmetro sort inválido. Use campo.asc ou campo.desc")

            allowed = {
                "ramos_id": Ramos.ramos_id,
                "ramo": Ramos.ramo,
            }

            col = allowed.get(field)
            if not col:
                raise HTTPException(400, f"Campo de sort não permitido: {field}")

            if direction not in ("asc", "desc"):
                raise HTTPException(400, "Direção de sort inválida. Use asc ou desc")

            query = query.order_by(col.asc() if direction == "asc" else col.desc())
        else:
            query = query.order_by(Ramos.ramo.asc())

        items = (
            query
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )

        return items, total

    def get(self, db: Session, ramos_id: str):
        ramo = db.query(Ramos).filter(Ramos.ramos_id == ramos_id).first()
        if not ramo:
            raise HTTPException(404, "Ramo não encontrado")
        return ramo

    def criar(self, db: Session, data: RamoCreate):
        novo = Ramos(ramo=data.ramo)
        db.add(novo)
        db.commit()
        db.refresh(novo)
        return novo

    def atualizar(self, db: Session, ramos_id: str, data: RamoUpdate):
        ramo = self.get(db, ramos_id)

        if data.ramo is not None:
            ramo.ramo = data.ramo

        db.commit()
        db.refresh(ramo)
        return ramo

    def deletar(self, db: Session, ramos_id: str):
        ramo = self.get(db, ramos_id)
        db.delete(ramo)
        db.commit()
        return {"status": "deleted"}


crud_ramos = CRUDRamos()
