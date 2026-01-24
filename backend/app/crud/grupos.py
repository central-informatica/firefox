"""
CRUD operations for Grupos.

Note: User/empresa membership validation is now handled by the Auth microservice.
The empresa_id filtering is used for multi-tenant data isolation, but the
actual user authorization is done by the Auth service.
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException
from backend.app.db.models import Grupos, Certificados, GruposCertificados


def get_grupo(db: Session, grupo_id: str):
    return db.query(Grupos).filter(Grupos.grupo_id == grupo_id).first()


def listar_grupos(db: Session):
    return db.query(Grupos).all()


def listar_certificados_do_grupo(db: Session, grupo_id: str):
    return (
        db.query(Certificados)
        .join(GruposCertificados, GruposCertificados.certificado_id == Certificados.certificado_id)
        .filter(
            GruposCertificados.grupo_id == grupo_id,
            Certificados.deleted_at.is_(None),
        )
        .all()
    )


def get_grupo_por_empresa(
    db: Session,
    grupo_id: str,
    empresa_id: str,
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
    empresa_id: str,
    usuario_id: str,
    plano_id: str | None = None,
):
    # Note: User membership validation is now handled by Auth service
    # The usuario_id is kept as parameter for backward compatibility
    # but the actual authorization is done before reaching this function

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
    grupo_id: str,
    certificado_id: str,
    empresa_id: str,
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


def atualizar_grupo(
    db: Session,
    *,
    grupo_id: str,
    empresa_id: str,
    usuario_id: str,
    dados: dict,
):
    # Note: User membership validation is now handled by Auth service
    # The usuario_id is kept as parameter for backward compatibility

    # Busca o grupo garantindo que ele pertence à empresa
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

    # Atualiza campos permitidos
    for campo, valor in dados.items():
        if hasattr(grupo, campo) and valor is not None:
            setattr(grupo, campo, valor)

    db.commit()
    db.refresh(grupo)

    return grupo


def deletar_grupo(db: Session, grupo_id: str):
    grupo = get_grupo(db, grupo_id)
    if not grupo:
        return False

    db.delete(grupo)
    db.commit()
    return True


def remover_certificado_do_grupo(
    db: Session,
    grupo_id: str,
    certificado_id: str,
    empresa_id: str,
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
    grupo_id: str,
    certificado_id: str | None,
    empresa_id: str,
):
    grupo = get_grupo_por_empresa(db, grupo_id, empresa_id)
    if not grupo:
        raise HTTPException(status_code=403, detail="Grupo não pertence à empresa")

    if certificado_id:
        certificado = db.query(Certificados).filter(
            Certificados.certificado_id == certificado_id,
            Certificados.empresa_id == empresa_id,
            Certificados.deleted_at.is_(None),
        ).first()
        if not certificado:
            raise HTTPException(
                status_code=403,
                detail="Certificado não pertence à empresa",
            )

    return grupo
