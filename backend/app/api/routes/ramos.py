from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from backend.app.api.deps import check_auth
from backend.app.db.session import get_db
from backend.app.schemas.ramos import RamoCreate, RamoUpdate, RamoOut
from backend.app.schemas.common import Page
from backend.app.crud.ramos import crud_ramos

router = APIRouter(prefix="/ramos", tags=["Ramos"])


@router.get("/", response_model=List[RamoOut])
def listar_todos_ramos(
    db: Session = Depends(get_db),
    current_user=Depends(check_auth),
):
    """Lista todos os ramos de atuação (para selects)."""
    return crud_ramos.listar_todos(db)


@router.get("/paginado", response_model=Page[RamoOut])
def listar_ramos_paginado(
    db: Session = Depends(get_db),
    current_user=Depends(check_auth),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: str = "",
    sort: str = "",
):
    """Lista ramos de atuação com paginação."""
    items, total = crud_ramos.listar_paginado(
        db=db,
        page=page,
        limit=limit,
        search=search,
        sort=sort,
    )
    return {
        "data": items,
        "total": total,
    }


@router.post("/", response_model=RamoOut)
def criar_ramo(
    data: RamoCreate,
    db: Session = Depends(get_db),
    current_user=Depends(check_auth),
):
    """Cria um novo ramo de atuação."""
    return crud_ramos.criar(db, data)


@router.get("/id/{ramos_id}", response_model=RamoOut)
def get_ramo(
    ramos_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(check_auth),
):
    """Busca um ramo de atuação por ID."""
    return crud_ramos.get(db, ramos_id)


@router.put("/id/{ramos_id}", response_model=RamoOut)
def atualizar_ramo(
    ramos_id: str,
    data: RamoUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(check_auth),
):
    """Atualiza um ramo de atuação."""
    return crud_ramos.atualizar(db, ramos_id, data)


@router.delete("/id/{ramos_id}")
def deletar_ramo(
    ramos_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(check_auth),
):
    """Deleta um ramo de atuação."""
    return crud_ramos.deletar(db, ramos_id)
