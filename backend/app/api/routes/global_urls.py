from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.api.deps import check_auth_with_ip
from backend.app.db.session import get_db
from backend.app.schemas.global_urls import (
    GlobalUrlCreate, GlobalUrlUpdate, GlobalUrlOut
)
from backend.app.schemas.common import Page
from backend.app.crud.global_urls import crud_global_urls

router = APIRouter(prefix="/global-urls", tags=["Global URLs"])


@router.get("/empresa/{empresa_id}", response_model=Page[GlobalUrlOut])
def listar_global_urls(
    empresa_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(check_auth_with_ip),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: str = "",
    sort: str = "",
):
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Apenas administradores podem listar URLs globais")
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
    current_user=Depends(check_auth_with_ip),
):
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Apenas administradores podem criar URLs globais")
    return crud_global_urls.criar(db, data)


@router.get("/id/{global_urls_id}", response_model=GlobalUrlOut)
def get_global_url(
    global_urls_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(check_auth_with_ip),
):
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Apenas administradores podem visualizar URLs globais")
    return crud_global_urls.get(db, global_urls_id)


@router.put("/id/{global_urls_id}", response_model=GlobalUrlOut)
def atualizar_global_url(
    global_urls_id: str,
    data: GlobalUrlUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(check_auth_with_ip),
):
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Apenas administradores podem atualizar URLs globais")
    return crud_global_urls.atualizar(db, global_urls_id, data)


@router.delete("/id/{global_urls_id}")
def deletar_global_url(
    global_urls_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(check_auth_with_ip),
):
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Apenas administradores podem deletar URLs globais")
    return crud_global_urls.deletar(db, global_urls_id)
