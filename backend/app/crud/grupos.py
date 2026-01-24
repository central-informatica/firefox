from sqlalchemy.orm import Session
from fastapi import HTTPException
from backend.app.db.models import Grupos, EmpresaMembros, Certificados, GruposCertificados
from backend.app.crud.certificado import get_certificado_por_empresa

def get_grupo(db: Session, grupo_id: int):
    return db.query(Grupos).filter(Grupos.grupo_id == grupo_id).first()

def listar_grupos(db: Session):
    return db.query(Grupos).all()

def listar_certificados_do_grupo(db: Session, grupo_id: int):
    return (
        db.query(Certificados)
        .join(GruposCertificados, GruposCertificados.certificado_id == Certificados.certificado_id)
        .filter(GruposCertificados.grupo_id == grupo_id)
        .all()
    )

def get_grupo_por_empresa(
    db: Session,
    grupo_id: int,
    empresa_id: int,
):
    return (
        db.query(Grupos)
        .filter(
            Grupos.grupo_id == grupo_id,
            Grupos.empresa_id == empresa_id,
        )
        .first()
    )

def listar_grupos_por_empresa(
    db: Session,
    *,
    empresa_id: int,
    usuario_id: int,
    plano_id: int | None = None,
):
    if not _usuario_pertence_empresa(db, usuario_id, empresa_id):
        raise HTTPException(
            status_code=403,
            detail="Usuário não pertence à empresa",
        )

    query = db.query(Grupos).filter(
        Grupos.empresa_id == empresa_id
    )

    if plano_id:
        query = query.filter(
            Grupos.plano_id == plano_id
        )

    return query.order_by(Grupos.nome).all()


def criar_grupo(db: Session, payload: dict):
    novo = Grupos(**payload)
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo

def adicionar_certificado_ao_grupo(
    db: Session,
    grupo_id: int,
    certificado_id: int,
    empresa_id: int,
):
    validar_grupo_e_certificado_do_tenant(
        db=db,
        grupo_id=grupo_id,
        certificado_id=certificado_id,
        empresa_id=empresa_id,
    )

    relacao = (
        db.query(GruposCertificados)
        .filter(
            GruposCertificados.grupo_id == grupo_id,
            GruposCertificados.certificado_id == certificado_id,
        )
        .first()
    )

    if relacao:
        return relacao

    relacao = GruposCertificados(
        grupo_id=grupo_id,
        certificado_id=certificado_id,
        empresa_id=empresa_id,
    )

    db.add(relacao)
    db.commit()
    db.refresh(relacao)

    return relacao

#def atualizar_grupo(db: Session, grupo_id: int, dados: dict):
#    grupo = get_grupo(db, grupo_id)
#    if not grupo:
#        return None
#
#    for key, value in dados.items():
#        setattr(grupo, key, value)
#
#    db.commit()
#    db.refresh(grupo)
#    return grupo

def atualizar_grupo(
    db: Session,
    *,
    grupo_id: int,
    empresa_id: int,
    usuario_id: int,
    dados: dict,
):
    # 1. Verifica se o usuário pertence à empresa
    if not _usuario_pertence_empresa(db, usuario_id, empresa_id):
        raise HTTPException(
            status_code=403,
            detail="Usuário não pertence à empresa",
        )

    # 2. Busca o grupo garantindo que ele pertence à empresa
    grupo = (
        db.query(Grupos)
        .filter(
            Grupos.grupo_id == grupo_id,
            Grupos.empresa_id == empresa_id,
        )
        .first()
    )

    if not grupo:
        return None

    # 3. Atualiza campos permitidos
    for campo, valor in dados.items():
        if hasattr(grupo, campo) and valor is not None:
            setattr(grupo, campo, valor)

    db.commit()
    db.refresh(grupo)

    return grupo


def deletar_grupo(db: Session, grupo_id: int):
    grupo = get_grupo(db, grupo_id)
    if not grupo:
        return False

    db.delete(grupo)
    db.commit()
    return True

def remover_certificado_do_grupo(
    db: Session,
    grupo_id: int,
    certificado_id: int,
    empresa_id: int,
):
    validar_grupo_e_certificado_do_tenant(
        db=db,
        grupo_id=grupo_id,
        certificado_id=certificado_id,
        empresa_id=empresa_id,
    )

    relacao = (
        db.query(GruposCertificados)
        .filter(
            GruposCertificados.grupo_id == grupo_id,
            GruposCertificados.certificado_id == certificado_id,
        )
        .first()
    )

    if not relacao:
        return False

    db.delete(relacao)
    db.commit()

    return True


def validar_grupo_e_certificado_do_tenant(
    db: Session,
    grupo_id: int,
    certificado_id: int | None,
    empresa_id: int,
):
    grupo = get_grupo_por_empresa(db, grupo_id, empresa_id)
    if not grupo:
        raise HTTPException(status_code=403, detail="Grupo não pertence à empresa")

    if certificado_id:
        certificado = get_certificado_por_empresa(db, certificado_id, empresa_id)
        if not certificado:
            raise HTTPException(
                status_code=403,
                detail="Certificado não pertence à empresa",
            )

    return grupo

def _usuario_pertence_empresa(db: Session, usuario_id: int, empresa_id: int) -> bool:
    return (
        db.query(EmpresaMembros)
        .filter(
            EmpresaMembros.usuario_id == usuario_id,
            EmpresaMembros.empresa_id == empresa_id,
        )
        .first()
        is not None
    )