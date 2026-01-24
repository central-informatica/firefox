from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.app.api.deps import check_auth
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
    empresa_id: str,
    plano_id: str | None = None,
    db: Session = Depends(get_db),
    # current_user = Depends(check_auth),
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
def obter(grupo_id: str, db: Session = Depends(get_db)):
    grupo = get_grupo(db, grupo_id)
    if not grupo:
        raise HTTPException(status_code=404, detail="Grupo não encontrado")
    return grupo


@router.get("/{grupo_id}/certificados")
def listar_certificados_grupo(
    grupo_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(check_auth),
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
def atualizar(grupo_id: str, payload: dict, db: Session = Depends(get_db)):
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
def remover(grupo_id: str, db: Session = Depends(get_db)):
    sucesso = deletar_grupo(db, grupo_id)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Grupo não encontrado")
    return {"detail": "Grupo removido com sucesso"}

@router.post("/{grupo_id}/certificados")
def adicionar_certificado(
    grupo_id: str,
    payload: dict,
    db: Session = Depends(get_db),
    current_user = Depends(check_auth),
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


# =====================
# Usuários <-> Grupos
# =====================
from backend.app.crud.grupos_usuarios import crud_grupos_usuarios
from backend.app.schemas.grupos_usuarios import GrupoUsuarioCreate, GrupoUsuarioBulkCreate


@router.get("/{grupo_id}/usuarios")
def listar_usuarios_do_grupo(grupo_id: str, db: Session = Depends(get_db)):
    registros = crud_grupos_usuarios.listar_por_grupo(db, grupo_id)
    # Mapear para dados do usuário (se houver relacionamento)
    usuarios = []
    for r in registros:
        try:
            u = r.usuarios
            usuarios.append({
                "usuario_id": u.usuario_id,
                "nome": u.nome,
                "email": u.email,
            })
        except Exception:
            usuarios.append({
                "usuario_id": r.usuario_id,
            })
    return usuarios


@router.post("/{grupo_id}/usuarios", status_code=201)
def adicionar_usuario_ao_grupo(grupo_id: str, payload: dict, db: Session = Depends(get_db)):
    usuario_id = payload.get("usuario_id")
    empresa_id = payload.get("empresa_id")
    if not usuario_id:
        raise HTTPException(status_code=400, detail="usuario_id é obrigatório")

    data = GrupoUsuarioCreate(empresa_id=empresa_id or None, grupo_id=grupo_id, usuario_id=usuario_id)
    return crud_grupos_usuarios.criar(db, data)


@router.delete("/{grupo_id}/usuarios/{usuario_id}")
def remover_usuario_do_grupo(grupo_id: str, usuario_id: str, db: Session = Depends(get_db)):
    # procurar vínculo e deletar
    registros = crud_grupos_usuarios.listar_por_grupo(db, grupo_id)
    target = None
    for r in registros:
        if r.usuario_id == usuario_id:
            target = r
            break
    if not target:
        raise HTTPException(status_code=404, detail="Vínculo não encontrado")
    return crud_grupos_usuarios.deletar(db, target.grupo_usuario_id)


@router.post("/{grupo_id}/usuarios/bulk")
def adicionar_usuarios_em_lote(grupo_id: str, payload: GrupoUsuarioBulkCreate, db: Session = Depends(get_db)):
    # Usa o CRUD criar_bulk
    resumo = crud_grupos_usuarios.criar_bulk(db, grupo_id, payload.usuario_ids, payload.empresa_id)
    return resumo

@router.delete("/{grupo_id}/remover/certificado")
def remover_certificado(
    grupo_id: str,
    payload: dict,
    db: Session = Depends(get_db),
    current_user = Depends(check_auth),
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
    current_user = Depends(check_auth),
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
