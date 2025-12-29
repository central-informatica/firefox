from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.app.db.models import Usuarios
from backend.app.api.deps import get_current_user
from backend.app.db.session import get_db

from backend.app.crud.grupos import (
    listar_grupos_por_empresa,
    listar_certificados_do_grupo,
    get_grupo,
    criar_grupo,
    atualizar_grupo,
    deletar_grupo,
    adicionar_certificado_ao_grupo,
    remover_certificado_do_grupo,
)

router = APIRouter(prefix="/grupos", tags=["Grupos"])


@router.get("/empresa/{empresa_id}")
def listar_grupos_empresa(
    empresa_id: int,
    plano_id: int | None = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    print("listar_grupos_empresa:: empresa_id recebido:", plano_id)
    grupos = listar_grupos_por_empresa(
        db=db,
        empresa_id=empresa_id,
        usuario_id=current_user.usuario_id, 
        plano_id=plano_id,
    )

    return grupos

@router.get("/{grupo_id}")
def obter(grupo_id: int, db: Session = Depends(get_db)):
    grupo = get_grupo(db, grupo_id)
    if not grupo:
        raise HTTPException(status_code=404, detail="Grupo não encontrado")
    return grupo


@router.get("/{grupo_id}/certificados")
def listar_certificados_grupo(
    grupo_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    certificados = listar_certificados_do_grupo(
        db=db,
        grupo_id=grupo_id,
    )

    return certificados


@router.post("/")
def criar(payload: dict, db: Session = Depends(get_db)):
    print("Payload recebido no criar grupo:", payload)
    return criar_grupo(db, payload)


@router.put("/{grupo_id}")
def atualizar(grupo_id: int, payload: dict, db: Session = Depends(get_db)):
    grupo = atualizar_grupo(
        db=db, 
        grupo_id=grupo_id, 
        empresa_id=payload.get("empresa_id"),
        payload=payload
    )
    if not grupo:
        raise HTTPException(status_code=404, detail="Grupo não encontrado")
    return grupo


@router.delete("/{grupo_id}")
def remover(grupo_id: int, db: Session = Depends(get_db)):
    sucesso = deletar_grupo(db, grupo_id)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Grupo não encontrado")
    return {"detail": "Grupo removido com sucesso"}

@router.post("/{grupo_id}/certificados")
def adicionar_certificado(
    grupo_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    empresa_id = payload.get("empresa_id")   ##current_user.empresas[0].empresa_id
    print("empresa_id no adicionar_certificado:", empresa_id)
    certificado_id = payload.get("certificado_id")

    if not certificado_id:
        raise HTTPException(status_code=400, detail="certificado_id é obrigatório")

    return adicionar_certificado_ao_grupo(
        db=db,
        grupo_id=grupo_id,
        certificado_id=certificado_id,
        empresa_id=empresa_id,
    )


@router.delete("/{grupo_id}/remover/certificado")
def remover_certificado(
    grupo_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    # Obter empresa_id e certificado_id do payload
    empresa_id = payload.get("empresa_id")
    certificado_id = payload.get("certificado_id")

    ok = remover_certificado_do_grupo(
        db=db,
        grupo_id=grupo_id,
        certificado_id=certificado_id,
        empresa_id=empresa_id
    )

    if not ok:
        raise HTTPException(status_code=404, detail="Vínculo não encontrado")

    return {"success": True}

"""
@router.delete("/{grupo_id}/certificados/{certificado_id}")
def remover_certificado(
    grupo_id: int,
    certificado_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    ok = remover_certificado_do_grupo(
        db=db,
        grupo_id=grupo_id,
        certificado_id=certificado_id,
        empresa_id=empresa_id
    )

    if not ok:
        raise HTTPException(status_code=404, detail="Vínculo não encontrado")

    return {"success": True}
"""
