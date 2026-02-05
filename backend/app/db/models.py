"""
Database models for XSecurity-Vault.

Note: The following entities are now managed by the Auth microservice:
- Usuarios (users)
- Empresas (organizations)
- EmpresaMembros (organization memberships)
- EmpresaConvites (organization invitations)
- AccessTokens (authentication tokens)

The empresa_id and usuario_id columns are kept for multi-tenant data isolation,
but without foreign key constraints since Auth service validates these IDs.
"""

from typing import Optional
import datetime
import uuid

from sqlalchemy import ARRAY, Boolean, Date, DateTime, ForeignKeyConstraint, Index, Integer, PrimaryKeyConstraint, String, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB, UUID as Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Certificados(Base):
    """Certificados digitais criptografados das empresas."""
    __tablename__ = 'certificados'
    __table_args__ = (
        PrimaryKeyConstraint('certificado_id', name='certificados_pkey'),
        Index('idx_cert_criado_por', 'criado_por'),
        Index('idx_cert_emp', 'empresa_id'),
        {'comment': 'Certificados digitais criptografados das empresas.'}
    )

    certificado_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    empresa_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, comment='ID da empresa (validado pelo Auth service)')
    criado_por: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, comment='ID do usuario que criou (validado pelo Auth service)')
    nome_arquivo: Mapped[str] = mapped_column(Text, nullable=False, comment='Nome original do arquivo de certificado.')
    encrypted: Mapped[str] = mapped_column(Text, nullable=False, comment='Dados do certificado em formato criptografado.')
    secret: Mapped[str] = mapped_column(Text, nullable=False, comment='Frase secreta ou chave auxiliar usada na criptografia.')
    criado_em: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    proprietario: Mapped[Optional[str]] = mapped_column(String, comment='Proprietario do certificado')
    emitido_por: Mapped[Optional[str]] = mapped_column(String, comment='Nome da entidade emissora do certificado')
    validade_inicio: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), comment='Data de inicio da validade')
    valido_ate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), comment='Data do fim da validade')
    cofre_cert_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, nullable=True, comment='ID do certificado no servico Cofre')
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'), comment='Indica se o certificado esta ativo para uso')
    deleted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, nullable=True, comment='Data/hora da exclusao (soft delete)')
    deleted_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, nullable=True, comment='ID do usuario que excluiu o certificado')

    grupos_certificados: Mapped[list['GruposCertificados']] = relationship('GruposCertificados', back_populates='certificado')


class Feriados(Base):
    """Feriados cadastrados por empresa, usados para bloquear acessos."""
    __tablename__ = 'feriados'
    __table_args__ = (
        PrimaryKeyConstraint('feriado_id', name='feriados_pkey'),
        Index('idx_feriados_emp', 'empresa_id'),
        {'comment': 'Feriados cadastrados por empresa, usados para bloquear acessos.'}
    )

    feriado_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    empresa_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, comment='ID da empresa (validado pelo Auth service)')
    data: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    recorrente: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'), comment='Indica se o feriado se repete todos os anos na mesma data.')
    criado_em: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))


class PlanosTrabalho(Base):
    """Planos de trabalho de uma empresa (modelos de regras e grupos)."""
    __tablename__ = 'planos_trabalho'
    __table_args__ = (
        PrimaryKeyConstraint('plano_id', name='planos_trabalho_pkey'),
        UniqueConstraint('empresa_id', 'nome', name='planos_trabalho_empresa_nome_unq'),
        Index('idx_planos_trabalho_emp', 'empresa_id'),
        {'comment': 'Planos de trabalho de uma empresa (modelos de regras e grupos).'}
    )

    plano_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    empresa_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, comment='ID da empresa (validado pelo Auth service)')
    nome: Mapped[str] = mapped_column(String(100), nullable=False, comment='Nome do plano de trabalho (deve ser unico dentro da empresa).')
    criado_em: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    descricao: Mapped[Optional[str]] = mapped_column(Text)

    grupos: Mapped[list['Grupos']] = relationship('Grupos', back_populates='plano')


class Grupos(Base):
    """Grupos de usuarios pertencentes a planos de trabalho de uma empresa."""
    __tablename__ = 'grupos'
    __table_args__ = (
        ForeignKeyConstraint(['plano_id'], ['planos_trabalho.plano_id'], ondelete='CASCADE', name='grupos_plano_fk'),
        PrimaryKeyConstraint('grupo_id', name='grupos_pkey'),
        UniqueConstraint('empresa_id', 'nome', name='grupos_empresa_nome_unq'),
        Index('idx_grupos_plano', 'plano_id'),
        Index('idx_grupos_emp', 'empresa_id'),
        {'comment': 'Grupos de usuarios pertencentes a planos de trabalho de uma empresa.'}
    )

    grupo_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    empresa_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, comment='ID da empresa (validado pelo Auth service)')
    plano_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    nome: Mapped[str] = mapped_column(String(100), nullable=False, comment='Nome do grupo (unico dentro da empresa).')
    criado_em: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))

    plano: Mapped['PlanosTrabalho'] = relationship('PlanosTrabalho', back_populates='grupos')
    grupos_certificados: Mapped[list['GruposCertificados']] = relationship('GruposCertificados', back_populates='grupo')
    grupos_usuarios: Mapped[list['GruposUsuarios']] = relationship('GruposUsuarios', back_populates='grupo')
    regras_acesso: Mapped[list['RegrasAcesso']] = relationship('RegrasAcesso', back_populates='grupo')
    regras_acesso_urls: Mapped[list['RegrasAcessoUrls']] = relationship('RegrasAcessoUrls', back_populates='grupo')
    regras_acesso_ips: Mapped[list['RegrasAcessoIps']] = relationship('RegrasAcessoIps', back_populates='grupo')


class GruposCertificados(Base):
    """Relacao de quais certificados cada grupo pode acessar."""
    __tablename__ = 'grupos_certificados'
    __table_args__ = (
        ForeignKeyConstraint(['grupo_id'], ['grupos.grupo_id'], ondelete='CASCADE', name='grupos_certificados_grupo_fk'),
        ForeignKeyConstraint(['certificado_id'], ['certificados.certificado_id'], ondelete='CASCADE', name='grupos_certificados_cert_fk'),
        PrimaryKeyConstraint('grupo_cert_id', name='grupos_certificados_pkey'),
        UniqueConstraint('grupo_id', 'certificado_id', name='grupos_certificados_unq'),
        Index('idx_g_cert_grupo', 'grupo_id'),
        Index('idx_g_cert_cert', 'certificado_id'),
        Index('idx_g_cert_emp', 'empresa_id'),
        {'comment': 'Relacao de quais certificados cada grupo pode acessar.'}
    )

    grupo_cert_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    empresa_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, comment='ID da empresa (validado pelo Auth service)')
    grupo_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    certificado_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)

    grupo: Mapped['Grupos'] = relationship('Grupos', back_populates='grupos_certificados')
    certificado: Mapped['Certificados'] = relationship('Certificados', back_populates='grupos_certificados')
    grupos_certificados_urls: Mapped[list['GruposCertificadosUrls']] = relationship('GruposCertificadosUrls', back_populates='grupo_certificado')


class GruposUsuarios(Base):
    """Relacao entre usuarios e grupos, dentro de uma empresa."""
    __tablename__ = 'grupos_usuarios'
    __table_args__ = (
        ForeignKeyConstraint(['grupo_id'], ['grupos.grupo_id'], ondelete='CASCADE', name='grupos_usuarios_grupo_fk'),
        PrimaryKeyConstraint('grupo_usuario_id', name='grupos_usuarios_pkey'),
        UniqueConstraint('grupo_id', 'usuario_id', name='grupos_usuarios_unq'),
        Index('idx_g_usuarios_grupo', 'grupo_id'),
        Index('idx_g_usuarios_user', 'usuario_id'),
        Index('idx_g_usuarios_emp', 'empresa_id'),
        {'comment': 'Relacao entre usuarios e grupos, dentro de uma empresa.'}
    )

    grupo_usuario_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    empresa_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, comment='ID da empresa (validado pelo Auth service)')
    grupo_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    usuario_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, comment='ID do usuario (validado pelo Auth service)')

    grupo: Mapped['Grupos'] = relationship('Grupos', back_populates='grupos_usuarios')


class RegrasAcesso(Base):
    """Regras de dias e horarios permitidos para grupos de uma empresa."""
    __tablename__ = 'regras_acesso'
    __table_args__ = (
        ForeignKeyConstraint(['grupo_id'], ['grupos.grupo_id'], ondelete='CASCADE', name='regras_grupo_fk'),
        PrimaryKeyConstraint('regra_id', name='regras_acesso_pkey'),
        Index('idx_regras_grupo', 'grupo_id'),
        Index('idx_regras_emp', 'empresa_id'),
        {'comment': 'Regras de dias e horarios permitidos para grupos de uma empresa.'}
    )

    regra_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    empresa_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, comment='ID da empresa (validado pelo Auth service)')
    grupo_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    tipo_dia: Mapped[str] = mapped_column(String(20), nullable=False, comment='Tipo de regra: corridos, uteis ou especificos.')
    horarios: Mapped[dict] = mapped_column(JSONB, nullable=False, comment='Lista de janelas de horario em JSON (inicio/fim no formato HH:MI).')
    criado_em: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    dias_especificos: Mapped[Optional[list[int]]] = mapped_column(ARRAY(Integer()), comment='Lista de dias (ex: 1=segunda ... 7=domingo) quando tipo_dia = especificos.')
    bloquear_em_feriado: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'), comment='Bloqueia acesso em feriados da empresa.')

    grupo: Mapped['Grupos'] = relationship('Grupos', back_populates='regras_acesso')


class GlobalUrls(Base):
    """URLs globais cadastradas por empresa."""
    __tablename__ = 'global_urls'
    __table_args__ = (
        PrimaryKeyConstraint('global_urls_id', name='global_urls_pkey'),
        Index('idx_global_urls_emp', 'empresa_id'),
        {'comment': 'URLs globais cadastradas por empresa.'}
    )

    global_urls_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'), comment='Identificador unico')
    url: Mapped[Optional[str]] = mapped_column(Text, comment='URL cadastrada')
    criado_em: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('now()'), comment='Data de criacao')
    inativo: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'), comment='Indica se a URL esta inativa')
    empresa_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, comment='ID da empresa (validado pelo Auth service)')

    grupos_certificados_urls: Mapped[list['GruposCertificadosUrls']] = relationship('GruposCertificadosUrls', back_populates='global_url')
    regras_acesso_urls: Mapped[list['RegrasAcessoUrls']] = relationship('RegrasAcessoUrls', back_populates='global_url')


class GruposCertificadosUrls(Base):
    """URLs permitidas para cada relacao grupo-certificado."""
    __tablename__ = 'grupos_certificados_urls'
    __table_args__ = (
        ForeignKeyConstraint(['grupo_cert_id'], ['grupos_certificados.grupo_cert_id'], ondelete='CASCADE', name='grupos_cert_urls_grupo_cert_fk'),
        ForeignKeyConstraint(['global_urls_id'], ['global_urls.global_urls_id'], ondelete='CASCADE', name='grupos_cert_urls_url_fk'),
        PrimaryKeyConstraint('grupo_cert_url_id', name='grupos_certificados_urls_pkey'),
        UniqueConstraint('grupo_cert_id', 'global_urls_id', name='grupos_certificados_urls_unq'),
        Index('idx_g_cert_urls_grupo_cert', 'grupo_cert_id'),
        Index('idx_g_cert_urls_url', 'global_urls_id'),
        Index('idx_g_cert_urls_emp', 'empresa_id'),
        {'comment': 'URLs permitidas para cada relacao grupo-certificado.'}
    )

    grupo_cert_url_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    empresa_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, comment='ID da empresa (validado pelo Auth service)')
    grupo_cert_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    global_urls_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)

    grupo_certificado: Mapped['GruposCertificados'] = relationship('GruposCertificados', back_populates='grupos_certificados_urls')
    global_url: Mapped['GlobalUrls'] = relationship('GlobalUrls', back_populates='grupos_certificados_urls')


class UsuariosIpWhitelist(Base):
    """Lista de IPs permitidos por usuario e empresa."""
    __tablename__ = 'usuarios_ip_whitelist'
    __table_args__ = (
        PrimaryKeyConstraint('whitelist_id', name='usuarios_ip_whitelist_pkey'),
        UniqueConstraint('usuario_id', 'empresa_id', 'ip_address', name='usuarios_ip_whitelist_unq'),
        Index('idx_usuarios_ip_whitelist_usuario', 'usuario_id'),
        Index('idx_usuarios_ip_whitelist_empresa', 'empresa_id'),
        Index('idx_usuarios_ip_whitelist_ip', 'ip_address'),
        {'comment': 'Lista de IPs permitidos por usuario e empresa.'}
    )

    whitelist_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    usuario_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, comment='ID do usuario (validado pelo Auth service)')
    empresa_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, comment='ID da empresa (validado pelo Auth service)')
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False, comment='Endereco IP permitido (IPv4 ou IPv6)')
    descricao: Mapped[Optional[str]] = mapped_column(Text, comment='Descricao opcional para referencia do admin')
    criado_em: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    criado_por: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, comment='ID do admin que criou a entrada')
    deleted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, nullable=True, comment='Data/hora da exclusao (soft delete)')
    deleted_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, nullable=True, comment='ID do usuario que excluiu')


class RegrasAcessoUrls(Base):
    """Regras de dias e horarios permitidos para URLs especificas de um grupo."""
    __tablename__ = 'regras_acesso_urls'
    __table_args__ = (
        ForeignKeyConstraint(['grupo_id'], ['grupos.grupo_id'], ondelete='CASCADE', name='regras_acesso_urls_grupo_fk'),
        ForeignKeyConstraint(['global_urls_id'], ['global_urls.global_urls_id'], ondelete='CASCADE', name='regras_acesso_urls_url_fk'),
        PrimaryKeyConstraint('regra_id', name='regras_acesso_urls_pkey'),
        UniqueConstraint('grupo_id', 'global_urls_id', name='regras_acesso_urls_grupo_url_unq'),
        Index('idx_regras_acesso_urls_grupo', 'grupo_id'),
        Index('idx_regras_acesso_urls_url', 'global_urls_id'),
        Index('idx_regras_acesso_urls_emp', 'empresa_id'),
        {'comment': 'Regras de dias e horarios permitidos para URLs especificas de um grupo.'}
    )

    regra_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    empresa_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, comment='ID da empresa (validado pelo Auth service)')
    grupo_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    global_urls_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    tipo_dia: Mapped[str] = mapped_column(String(20), nullable=False, comment='Tipo de regra: corridos, uteis ou especificos.')
    horarios: Mapped[dict] = mapped_column(JSONB, nullable=False, comment='Lista de janelas de horario em JSON (inicio/fim no formato HH:MI).')
    criado_em: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    dias_especificos: Mapped[Optional[list[int]]] = mapped_column(ARRAY(Integer()), comment='Lista de dias (ex: 1=segunda ... 7=domingo) quando tipo_dia = especificos.')
    bloquear_em_feriado: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'), comment='Bloqueia acesso em feriados da empresa.')
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'), comment='Indica se a regra esta ativa.')

    grupo: Mapped['Grupos'] = relationship('Grupos', back_populates='regras_acesso_urls')
    global_url: Mapped['GlobalUrls'] = relationship('GlobalUrls', back_populates='regras_acesso_urls')


class RegrasAcessoIps(Base):
    """Regras de dias e horarios permitidos para enderecos IP especificos de um grupo."""
    __tablename__ = 'regras_acesso_ips'
    __table_args__ = (
        ForeignKeyConstraint(['grupo_id'], ['grupos.grupo_id'], ondelete='CASCADE', name='regras_acesso_ips_grupo_fk'),
        PrimaryKeyConstraint('regra_id', name='regras_acesso_ips_pkey'),
        UniqueConstraint('grupo_id', 'ip_address', name='regras_acesso_ips_grupo_ip_unq'),
        Index('idx_regras_acesso_ips_grupo', 'grupo_id'),
        Index('idx_regras_acesso_ips_ip', 'ip_address'),
        Index('idx_regras_acesso_ips_emp', 'empresa_id'),
        {'comment': 'Regras de dias e horarios permitidos para enderecos IP especificos de um grupo.'}
    )

    regra_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    empresa_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, comment='ID da empresa (validado pelo Auth service)')
    grupo_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False, comment='Endereco IP (IPv4 ou IPv6)')
    tipo_dia: Mapped[str] = mapped_column(String(20), nullable=False, comment='Tipo de regra: corridos, uteis ou especificos.')
    horarios: Mapped[dict] = mapped_column(JSONB, nullable=False, comment='Lista de janelas de horario em JSON (inicio/fim no formato HH:MI).')
    criado_em: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    dias_especificos: Mapped[Optional[list[int]]] = mapped_column(ARRAY(Integer()), comment='Lista de dias (ex: 1=segunda ... 7=domingo) quando tipo_dia = especificos.')
    bloquear_em_feriado: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'), comment='Bloqueia acesso em feriados da empresa.')
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'), comment='Indica se a regra esta ativa.')

    grupo: Mapped['Grupos'] = relationship('Grupos', back_populates='regras_acesso_ips')


