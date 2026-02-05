from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.api.deps import check_auth_with_ip
from backend.app.db.session import get_db
from backend.app.db.models import Feriados
from backend.app.schemas.feriados import (
    FeriadoCreate,
    FeriadoUpdate,
    FeriadoOut,
    FeriadosReplicar,
    FeriadosImportarPadroes,
)
from backend.app.crud.feriados import crud_feriados


router = APIRouter(prefix="/feriados", tags=["Feriados"])


@router.get("/", response_model=list[FeriadoOut])
def listar_feriados(db: Session = Depends(get_db), current_user=Depends(check_auth_with_ip)):
    # Usuários comuns podem listar feriados
    return crud_feriados.listar(db)


@router.get("/empresa/{empresa_id}")
def listar_feriados_por_empresa(
    empresa_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(check_auth_with_ip),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: str = "",
):
    """Lista feriados de uma empresa com paginação."""
    # Usuários comuns podem listar feriados
    query = db.query(Feriados).filter(Feriados.empresa_id == empresa_id)

    # Aplicar filtro de busca
    if search:
        search_term = f"%{search}%"
        query = query.filter(Feriados.nome.ilike(search_term))

    # Ordenar por data
    query = query.order_by(Feriados.data.desc())

    # Total antes da paginação
    total = query.count()

    # Aplicar paginação
    offset = (page - 1) * limit
    items = query.offset(offset).limit(limit).all()

    return {
        "data": [
            {
                "feriado_id": str(f.feriado_id),
                "empresa_id": str(f.empresa_id),
                "data": str(f.data),
                "nome": f.nome,
                "recorrente": f.recorrente,
                "criado_em": str(f.criado_em) if f.criado_em else None,
            }
            for f in items
        ],
        "total": total,
        "page": page,
        "limit": limit,
    }


@router.get("/{feriado_id}", response_model=FeriadoOut)
def obter_feriado(feriado_id: str, db: Session = Depends(get_db), current_user=Depends(check_auth_with_ip)):
    # Usuários comuns podem visualizar feriados
    return crud_feriados.get(db, feriado_id)


@router.post("/", response_model=FeriadoOut, status_code=201)
def criar_feriado(data: FeriadoCreate, db: Session = Depends(get_db), current_user=Depends(check_auth_with_ip)):
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Apenas administradores podem criar feriados")
    return crud_feriados.criar(db, data)


@router.put("/{feriado_id}", response_model=FeriadoOut)
def atualizar_feriado(feriado_id: str, data: FeriadoUpdate, db: Session = Depends(get_db), current_user=Depends(check_auth_with_ip)):
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Apenas administradores podem atualizar feriados")
    return crud_feriados.atualizar(db, feriado_id, data)


@router.delete("/{feriado_id}")
def deletar_feriado(feriado_id: str, db: Session = Depends(get_db), current_user=Depends(check_auth_with_ip)):
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Apenas administradores podem deletar feriados")
    return crud_feriados.deletar(db, feriado_id)


@router.get("/padroes/lista")
def listar_feriados_padroes(current_user=Depends(check_auth_with_ip)):
    """Lista os feriados nacionais padrões disponíveis para importação."""
    return crud_feriados.listar_padroes()


@router.post("/replicar", status_code=201)
def replicar_feriados(
    data: FeriadosReplicar,
    db: Session = Depends(get_db),
    current_user=Depends(check_auth_with_ip)
):
    """Replica feriados selecionados para outras empresas."""
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Apenas administradores podem replicar feriados")

    result = crud_feriados.replicar(db, data)

    # Formatar resposta
    criados_formatados = [
        {
            "feriado_id": str(f.feriado_id),
            "empresa_id": str(f.empresa_id),
            "data": str(f.data),
            "nome": f.nome,
            "recorrente": f.recorrente,
            "criado_em": str(f.criado_em) if f.criado_em else None,
        }
        for f in result["criados"]
    ]

    return {
        "criados": criados_formatados,
        "total_criados": result["total_criados"],
        "erros": result["erros"]
    }


@router.post("/importar-padroes", status_code=201)
def importar_feriados_padroes(
    data: FeriadosImportarPadroes,
    db: Session = Depends(get_db),
    current_user=Depends(check_auth_with_ip)
):
    """Importa feriados nacionais padrões para uma empresa."""
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Apenas administradores podem importar feriados")

    result = crud_feriados.importar_padroes(db, data)

    # Formatar resposta
    criados_formatados = [
        {
            "feriado_id": str(f.feriado_id),
            "empresa_id": str(f.empresa_id),
            "data": str(f.data),
            "nome": f.nome,
            "recorrente": f.recorrente,
            "criado_em": str(f.criado_em) if f.criado_em else None,
        }
        for f in result["criados"]
    ]

    return {
        "criados": criados_formatados,
        "total_criados": result["total_criados"],
        "erros": result["erros"]
    }
