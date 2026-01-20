from typing import Optional
import datetime

from sqlalchemy import ARRAY, BigInteger, Boolean, Date, DateTime, Enum, ForeignKeyConstraint, Index, Integer, PrimaryKeyConstraint, String, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass


class Feriados(Base):
    __tablename__ = 'feriados'
    __table_args__ = (
        PrimaryKeyConstraint('feriado_id', name='feriados_pkey'),
        {'comment': 'Feriados cadastrados por empresa, usados para bloquear acessos.'}
    )

    feriado_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    data: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    recorrente: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'), comment='Indica se o feriado se repete todos os anos na mesma data.')
    criado_em: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))


class PlanosTrabalho(Base):
    __tablename__ = 'planos_trabalho'
    __table_args__ = (
        PrimaryKeyConstraint('plano_id', name='planos_trabalho_pkey'),
        UniqueConstraint('nome', name='planos_trabalho_nome_unq'),
        {'comment': 'Planos de trabalho de uma empresa (modelos de regras e grupos).'}
    )

    plano_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False, comment='Nome do plano de trabalho (deve ser unico dentro da empresa).')
    criado_em: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    descricao: Mapped[Optional[str]] = mapped_column(Text)

    grupos: Mapped[list['Grupos']] = relationship('Grupos', back_populates='plano')


class Grupos(Base):
    __tablename__ = 'grupos'
    __table_args__ = (
        ForeignKeyConstraint(['plano_id'], ['planos_trabalho.plano_id'], ondelete='CASCADE', name='grupos_plano_fk'),
        PrimaryKeyConstraint('grupo_id', name='grupos_pkey'),
        UniqueConstraint('nome', name='grupos_nome_unq'),
        Index('idx_grupos_plano', 'plano_id'),
        {'comment': 'Grupos de usuarios pertencentes a planos de trabalho de uma '
                'empresa.'}
    )

    grupo_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    plano_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    nome: Mapped[str] = mapped_column(String(100), nullable=False, comment='Nome do grupo (unico dentro da empresa).')
    criado_em: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))

    plano: Mapped['PlanosTrabalho'] = relationship('PlanosTrabalho', back_populates='grupos')
    grupos_certificados: Mapped[list['GruposCertificados']] = relationship('GruposCertificados', back_populates='grupo')
    grupos_usuarios: Mapped[list['GruposUsuarios']] = relationship('GruposUsuarios', back_populates='grupo')
    regras_acesso: Mapped[list['RegrasAcesso']] = relationship('RegrasAcesso', back_populates='grupo')
    regras_acesso_hosts: Mapped[list['RegrasAcessoHosts']] = relationship('RegrasAcessoHosts', back_populates='grupo')


class GruposCertificados(Base):
    __tablename__ = 'grupos_certificados'
    __table_args__ = (
        ForeignKeyConstraint(['grupo_id'], ['grupos.grupo_id'], ondelete='CASCADE', name='grupos_certificados_grupo_fk'),
        PrimaryKeyConstraint('grupo_cert_id', name='grupos_certificados_pkey'),
        Index('idx_g_cert_grupo', 'grupo_id'),
        {'comment': 'Relacao de quais certificados cada grupo pode acessar.'}
    )

    grupo_cert_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    grupo_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

    grupo: Mapped['Grupos'] = relationship('Grupos', back_populates='grupos_certificados')


class GruposUsuarios(Base):
    __tablename__ = 'grupos_usuarios'
    __table_args__ = (
        ForeignKeyConstraint(['grupo_id'], ['grupos.grupo_id'], ondelete='CASCADE', name='grupos_usuarios_grupo_fk'),
        PrimaryKeyConstraint('grupo_usuario_id', name='grupos_usuarios_pkey'),
        Index('idx_g_usuarios_grupo', 'grupo_id'),
        {'comment': 'Relacao entre usuarios e grupos, dentro de uma empresa.'}
    )

    grupo_usuario_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    grupo_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

    grupo: Mapped['Grupos'] = relationship('Grupos', back_populates='grupos_usuarios')


class RegrasAcesso(Base):
    __tablename__ = 'regras_acesso'
    __table_args__ = (
        ForeignKeyConstraint(['grupo_id'], ['grupos.grupo_id'], ondelete='CASCADE', name='regras_grupo_fk'),
        PrimaryKeyConstraint('regra_id', name='regras_acesso_pkey'),
        Index('idx_regras_grupo', 'grupo_id'),
        {'comment': 'Regras de dias e horarios permitidos para grupos de uma empresa.'}
    )

    regra_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    grupo_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    tipo_dia: Mapped[str] = mapped_column(String(20), nullable=False, comment='Tipo de regra: corridos, uteis ou especificos.')
    horarios: Mapped[dict] = mapped_column(JSONB, nullable=False, comment='Lista de janelas de horario em JSON (inicio/fim no formato HH:MI).')
    criado_em: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    dias_especificos: Mapped[Optional[list[int]]] = mapped_column(ARRAY(Integer()), comment='Lista de dias (ex: 1=segunda ... 7=domingo) quando tipo_dia = especificos.')

    grupo: Mapped['Grupos'] = relationship('Grupos', back_populates='regras_acesso')


class RegrasAcessoHosts(Base):
    __tablename__ = 'regras_acesso_hosts'
    __table_args__ = (
        ForeignKeyConstraint(['grupo_id'], ['grupos.grupo_id'], ondelete='CASCADE', name='regras_grupo_fk'),
        PrimaryKeyConstraint('regra_id', name='regras_acesso_hosts_pkey'),
        Index('idx_regras_acesso_hosts_grupo', 'grupo_id'),
    )

    regra_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    grupo_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    tipo_dia: Mapped[str] = mapped_column(String(20), nullable=False)
    horarios: Mapped[dict] = mapped_column(JSONB, nullable=False)
    criado_em: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    dias_especificos: Mapped[Optional[list[int]]] = mapped_column(ARRAY(Integer()))
    urls: Mapped[Optional[str]] = mapped_column(Text)

    grupo: Mapped['Grupos'] = relationship('Grupos', back_populates='regras_acesso_hosts')
