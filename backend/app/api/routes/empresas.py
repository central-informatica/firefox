from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user

from backend.app.db.session import get_db
from backend.app.schemas.empresas import (
    EmpresaCreate, EmpresaUpdate, EmpresaOut
)
from backend.app.schemas.common import Page
from backend.app.crud.empresas import crud_empresas

router = APIRouter(prefix="/empresas", tags=["Empresas"])


@router.get("/", response_model=Page[EmpresaOut])
def listar_empresas(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: str = "",
    sort: str = "",
):
    items, total = crud_empresas.listar_paginado_do_usuario(
        db=db,
        usuario_id=current_user.usuarios.usuario_id,
        page=page,
        limit=limit,
        search=search,
        sort=sort,
    )
    print(items)
    return {
        "data": items,
        "total": total,
    }

@router.get("/{empresa_id}", response_model=EmpresaOut)
def get_empresa(empresa_id: int, db: Session = Depends(get_db)):
    return crud_empresas.get(db, empresa_id)


@router.post("/", response_model=EmpresaOut)
def criar_empresa(data: EmpresaCreate, db: Session = Depends(get_db)):
    return crud_empresas.criar(db, data)


@router.put("/{empresa_id}", response_model=EmpresaOut)
def atualizar_empresa(empresa_id: int, data: EmpresaUpdate, db: Session = Depends(get_db)):
    return crud_empresas.atualizar(db, empresa_id, data)


@router.delete("/{empresa_id}")
def deletar_empresa(empresa_id: int, db: Session = Depends(get_db)):
    return crud_empresas.deletar(db, empresa_id)
