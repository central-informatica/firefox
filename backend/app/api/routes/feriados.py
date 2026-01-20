from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.feriados import (
    FeriadoCreate,
    FeriadoUpdate,
    FeriadoOut
)
from backend.app.crud.feriados import crud_feriados


router = APIRouter(prefix="/feriados", tags=["Feriados"])


@router.get("/", response_model=list[FeriadoOut])
def listar_feriados(db: Session = Depends(get_db)):
    return crud_feriados.listar(db)


@router.get("/{feriado_id}", response_model=FeriadoOut)
def obter_feriado(feriado_id: int, db: Session = Depends(get_db)):
    return crud_feriados.get(db, feriado_id)


@router.post("/", response_model=FeriadoOut, status_code=201)
def criar_feriado(data: FeriadoCreate, db: Session = Depends(get_db)):
    return crud_feriados.criar(db, data)


@router.put("/{feriado_id}", response_model=FeriadoOut)
def atualizar_feriado(feriado_id: int, data: FeriadoUpdate, db: Session = Depends(get_db)):
    return crud_feriados.atualizar(db, feriado_id, data)


@router.delete("/{feriado_id}")
def deletar_feriado(feriado_id: int, db: Session = Depends(get_db)):
    return crud_feriados.deletar(db, feriado_id)
