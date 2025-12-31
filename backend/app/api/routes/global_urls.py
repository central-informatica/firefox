from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user
from backend.app.db.session import get_db
from backend.app.schemas.global_urls import (
    GlobalUrlCreate, GlobalUrlUpdate, GlobalUrlOut
)
from backend.app.schemas.common import Page
from backend.app.crud.global_urls import crud_global_urls

router = APIRouter(prefix="/global-urls", tags=["Global URLs"])


@router.get("/empresa/{empresa_id}", response_model=Page[GlobalUrlOut])
def listar_global_urls(
    empresa_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: str = "",
    sort: str = "",
):
    items, total = crud_global_urls.listar_paginado(
        db=db,
        empresa_id=empresa_id,
        page=page,
        limit=limit,
        search=search,
        sort=sort,
    )
    return {
        "data": items,
        "total": total,
    }


@router.post("/", response_model=GlobalUrlOut)
def criar_global_url(
    data: GlobalUrlCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return crud_global_urls.criar(db, data)


@router.get("/id/{global_urls_id}", response_model=GlobalUrlOut)
def get_global_url(
    global_urls_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return crud_global_urls.get(db, global_urls_id)


@router.put("/id/{global_urls_id}", response_model=GlobalUrlOut)
def atualizar_global_url(
    global_urls_id: int,
    data: GlobalUrlUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return crud_global_urls.atualizar(db, global_urls_id, data)


@router.delete("/id/{global_urls_id}")
def deletar_global_url(
    global_urls_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return crud_global_urls.deletar(db, global_urls_id)
