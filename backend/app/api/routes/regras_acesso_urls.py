from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.api.deps import check_auth_with_ip
from backend.app.db.session import get_db
from backend.app.db.models import RegrasAcessoUrls, Grupos, GlobalUrls
from backend.app.schemas.regras_acesso_urls import (
    RegraAcessoUrlsCreate,
    RegraAcessoUrlsCreateBulk,
    RegraAcessoUrlsUpdate,
    RegraAcessoUrlsOut
)
from backend.app.crud.regras_acesso_urls import crud_regras_acesso_urls


router = APIRouter(prefix="/regras-acesso-urls", tags=["Regras de Acesso URLs"])


@router.get("/")
def listar_regras(db: Session = Depends(get_db), current_user=Depends(check_auth_with_ip)):
    """Lista todas as regras de acesso URLs."""
    return crud_regras_acesso_urls.listar(db)


@router.get("/empresa/{empresa_id}")
def listar_regras_por_empresa(
    empresa_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(check_auth_with_ip),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: str = "",
):
    """Lista regras de acesso URLs de uma empresa com paginação."""
    query = db.query(RegrasAcessoUrls).filter(RegrasAcessoUrls.empresa_id == empresa_id)

    # Aplicar filtro de busca pela URL
    if search:
        search_term = f"%{search}%"
        query = query.join(GlobalUrls).filter(GlobalUrls.url.ilike(search_term))

    # Ordenar por data de criação
    query = query.order_by(RegrasAcessoUrls.criado_em.desc())

    # Total antes da paginação
    total = query.count()

    # Aplicar paginação
    offset = (page - 1) * limit
    items = query.offset(offset).limit(limit).all()

    # Buscar nomes dos grupos e URLs para enriquecer a resposta
    result_data = []
    for r in items:
        grupo = db.query(Grupos).filter(Grupos.grupo_id == r.grupo_id).first()
        url = db.query(GlobalUrls).filter(GlobalUrls.global_urls_id == r.global_urls_id).first()

        result_data.append({
            "regra_id": str(r.regra_id),
            "empresa_id": str(r.empresa_id),
            "grupo_id": str(r.grupo_id),
            "global_urls_id": str(r.global_urls_id),
            "tipo_dia": r.tipo_dia,
            "dias_especificos": r.dias_especificos,
            "horarios": r.horarios,
            "bloquear_em_feriado": r.bloquear_em_feriado,
            "criado_em": str(r.criado_em) if r.criado_em else None,
            "grupo_nome": grupo.nome if grupo else None,
            "url": url.url if url else None,
        })

    return {
        "data": result_data,
        "total": total,
        "page": page,
        "limit": limit,
    }


@router.get("/grupo/{grupo_id}")
def listar_regras_por_grupo(
    grupo_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(check_auth_with_ip)
):
    """Lista regras de acesso URLs de um grupo específico."""
    items = crud_regras_acesso_urls.listar_por_grupo(db, grupo_id)

    result_data = []
    for r in items:
        url = db.query(GlobalUrls).filter(GlobalUrls.global_urls_id == r.global_urls_id).first()

        result_data.append({
            "regra_id": str(r.regra_id),
            "empresa_id": str(r.empresa_id),
            "grupo_id": str(r.grupo_id),
            "global_urls_id": str(r.global_urls_id),
            "tipo_dia": r.tipo_dia,
            "dias_especificos": r.dias_especificos,
            "horarios": r.horarios,
            "bloquear_em_feriado": r.bloquear_em_feriado,
            "criado_em": str(r.criado_em) if r.criado_em else None,
            "url": url.url if url else None,
        })

    return result_data


@router.get("/id/{regra_id}")
def obter_regra(regra_id: str, db: Session = Depends(get_db), current_user=Depends(check_auth_with_ip)):
    """Busca uma regra de acesso URL pelo ID."""
    r = crud_regras_acesso_urls.get(db, regra_id)

    grupo = db.query(Grupos).filter(Grupos.grupo_id == r.grupo_id).first()
    url = db.query(GlobalUrls).filter(GlobalUrls.global_urls_id == r.global_urls_id).first()

    return {
        "regra_id": str(r.regra_id),
        "empresa_id": str(r.empresa_id),
        "grupo_id": str(r.grupo_id),
        "global_urls_id": str(r.global_urls_id),
        "tipo_dia": r.tipo_dia,
        "dias_especificos": r.dias_especificos,
        "horarios": r.horarios,
        "bloquear_em_feriado": r.bloquear_em_feriado,
        "criado_em": str(r.criado_em) if r.criado_em else None,
        "grupo_nome": grupo.nome if grupo else None,
        "url": url.url if url else None,
    }


@router.post("/", status_code=201)
def criar_regra(data: RegraAcessoUrlsCreate, db: Session = Depends(get_db), current_user=Depends(check_auth_with_ip)):
    """Cria uma nova regra de acesso URL."""
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Apenas administradores podem criar regras de acesso")

    r = crud_regras_acesso_urls.criar(db, data)

    grupo = db.query(Grupos).filter(Grupos.grupo_id == r.grupo_id).first()
    url = db.query(GlobalUrls).filter(GlobalUrls.global_urls_id == r.global_urls_id).first()

    return {
        "regra_id": str(r.regra_id),
        "empresa_id": str(r.empresa_id),
        "grupo_id": str(r.grupo_id),
        "global_urls_id": str(r.global_urls_id),
        "tipo_dia": r.tipo_dia,
        "dias_especificos": r.dias_especificos,
        "horarios": r.horarios,
        "bloquear_em_feriado": r.bloquear_em_feriado,
        "criado_em": str(r.criado_em) if r.criado_em else None,
        "grupo_nome": grupo.nome if grupo else None,
        "url": url.url if url else None,
    }


@router.post("/bulk", status_code=201)
def criar_regras_bulk(data: RegraAcessoUrlsCreateBulk, db: Session = Depends(get_db), current_user=Depends(check_auth_with_ip)):
    """Cria regras de acesso URL para múltiplos grupos."""
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Apenas administradores podem criar regras de acesso")

    result = crud_regras_acesso_urls.criar_bulk(db, data)

    # Formatar resposta com detalhes
    criadas_formatadas = []
    for r in result["criadas"]:
        grupo = db.query(Grupos).filter(Grupos.grupo_id == r.grupo_id).first()
        url = db.query(GlobalUrls).filter(GlobalUrls.global_urls_id == r.global_urls_id).first()

        criadas_formatadas.append({
            "regra_id": str(r.regra_id),
            "empresa_id": str(r.empresa_id),
            "grupo_id": str(r.grupo_id),
            "global_urls_id": str(r.global_urls_id),
            "tipo_dia": r.tipo_dia,
            "dias_especificos": r.dias_especificos,
            "horarios": r.horarios,
            "bloquear_em_feriado": r.bloquear_em_feriado,
            "criado_em": str(r.criado_em) if r.criado_em else None,
            "grupo_nome": grupo.nome if grupo else None,
            "url": url.url if url else None,
        })

    return {
        "criadas": criadas_formatadas,
        "total_criadas": result["total_criadas"],
        "erros": result["erros"]
    }


@router.put("/{regra_id}")
def atualizar_regra(regra_id: str, data: RegraAcessoUrlsUpdate, db: Session = Depends(get_db), current_user=Depends(check_auth_with_ip)):
    """Atualiza uma regra de acesso URL."""
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Apenas administradores podem atualizar regras de acesso")

    r = crud_regras_acesso_urls.atualizar(db, regra_id, data)

    grupo = db.query(Grupos).filter(Grupos.grupo_id == r.grupo_id).first()
    url = db.query(GlobalUrls).filter(GlobalUrls.global_urls_id == r.global_urls_id).first()

    return {
        "regra_id": str(r.regra_id),
        "empresa_id": str(r.empresa_id),
        "grupo_id": str(r.grupo_id),
        "global_urls_id": str(r.global_urls_id),
        "tipo_dia": r.tipo_dia,
        "dias_especificos": r.dias_especificos,
        "horarios": r.horarios,
        "bloquear_em_feriado": r.bloquear_em_feriado,
        "criado_em": str(r.criado_em) if r.criado_em else None,
        "grupo_nome": grupo.nome if grupo else None,
        "url": url.url if url else None,
    }


@router.delete("/{regra_id}")
def deletar_regra(regra_id: str, db: Session = Depends(get_db), current_user=Depends(check_auth_with_ip)):
    """Remove uma regra de acesso URL."""
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Apenas administradores podem deletar regras de acesso")
    return crud_regras_acesso_urls.deletar(db, regra_id)
