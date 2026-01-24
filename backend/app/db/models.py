from typing import Optional
import datetime

from sqlalchemy import ARRAY, BigInteger, Boolean, Date, DateTime, Enum, ForeignKeyConstraint, Index, Integer, PrimaryKeyConstraint, String, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass


class Ramos(Base):
    __tablename__ = 'ramos'
    __table_args__ = (
        PrimaryKeyConstraint('ramos_id', name='ramos_pkey'),
        {'comment': 'Ramos de atuação das empresas.'}
    )

    ramos_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    ramo: Mapped[str] = mapped_column(String(80), nullable=False, comment='Nome do ramo de atuação.')

    empresas: Mapped[list['Empresas']] = relationship('Empresas', back_populates='ramo_rel')


class Usuarios(Base):
    __tablename__ = 'usuarios'
    __table_args__ = (
        PrimaryKeyConstraint('usuario_id', name='usuarios_pkey'),
        UniqueConstraint('email', name='usuarios_email_key'),
        Index('idx_usuarios_email', 'email'),
        {'comment': 'Cadastro geral de usuarios da plataforma.'}
    )

    usuario_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    nome: Mapped[str] = mapped_column(String(80), nullable=False, comment='Nome completo do usuario.')
    email: Mapped[str] = mapped_column(String(150), nullable=False, comment='E-mail utilizado para login na plataforma.')
    senha_hash: Mapped[str] = mapped_column(Text, nullable=False)
    email_verificado: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    criado_em: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    atualizado_em: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    nivel: Mapped[str] = mapped_column(Enum('ADMINISTRADOR', 'COMUM', name='usuario_nivel'), nullable=False, server_default=text("'COMUM'::usuario_nivel"), comment='Nivel global do usuario na plataforma SaaS. ADMINISTRADOR = acesso total ao sistema. COMUM = usuario padrao.')
    telefone: Mapped[Optional[str]] = mapped_column(String(40))

    access_tokens: Mapped[list['AccessTokens']] = relationship('AccessTokens', back_populates='usuarios')
    empresas: Mapped[list['Empresas']] = relationship('Empresas', back_populates='anfitria_usuario')
    certificados: Mapped[list['Certificados']] = relationship('Certificados', back_populates='usuarios')
    empresa_convites: Mapped[list['EmpresaConvites']] = relationship('EmpresaConvites', back_populates='convidado_usuario')
    empresa_membros: Mapped[list['EmpresaMembros']] = relationship('EmpresaMembros', back_populates='usuario')
    grupos_usuarios: Mapped[list['GruposUsuarios']] = relationship('GruposUsuarios', back_populates='usuario')


class AccessTokens(Base):
    __tablename__ = 'access_tokens'
    __table_args__ = (
        ForeignKeyConstraint(['usuario_id'], ['usuarios.usuario_id'], ondelete='CASCADE', name='access_tokens_usuario_fk'),
        PrimaryKeyConstraint('token_id', name='access_tokens_pkey'),
        UniqueConstraint('selector', name='access_tokens_selector_key'),
        Index('idx_access_tokens_usuario', 'usuario_id'),
        Index('idx_access_tokens_selector', 'selector', unique=True),
        Index('idx_access_tokens_expires_at', 'expires_at'),
        {'comment': 'Opaque access tokens with Argon2 hashing for secure authentication'}
    )

    token_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    usuario_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='User owning this token')
    selector: Mapped[str] = mapped_column(String(64), nullable=False, comment='First 32 bytes (base64url) for fast indexed lookup')
    validator_hash: Mapped[str] = mapped_column(String(128), nullable=False, comment='Argon2 hash of validator (last 32 bytes)')
    tipo_cliente: Mapped[str] = mapped_column(Enum('WEB', 'DESKTOP', name='client_type'), nullable=False, comment='Client type: WEB (cookies+CSRF) or DESKTOP (Bearer token)')
    criado_em: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'), comment='Token creation timestamp')
    expires_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, comment='Token expiration timestamp (typically 15 minutes)')
    ultimo_uso: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Last time this token was used for authentication')
    revogado: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'), comment='Token revocation flag')
    revogado_em: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='Timestamp when token was revoked')
    revogado_motivo: Mapped[Optional[str]] = mapped_column(String(255), comment='Reason for revocation (logout, security, expired, etc)')
    permissions: Mapped[dict] = mapped_column(JSONB, nullable=False, comment='Embedded permissions: user role + empresa memberships')
    user_agent: Mapped[Optional[str]] = mapped_column(Text, comment='Client user agent string')
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), comment='Client IP address (IPv4 or IPv6)')

    usuarios: Mapped['Usuarios'] = relationship('Usuarios', back_populates='access_tokens')


class Empresas(Base):
    __tablename__ = 'empresas'
    __table_args__ = (
        ForeignKeyConstraint(['anfitria_usuario_id'], ['usuarios.usuario_id'], ondelete='RESTRICT', onupdate='CASCADE', name='empresas_anfitria_fk'),
        ForeignKeyConstraint(['ramos_id'], ['ramos.ramos_id'], ondelete='RESTRICT', onupdate='CASCADE', name='empresas_ramos_fk'),
        PrimaryKeyConstraint('empresa_id', name='empresas_pkey'),
        UniqueConstraint('cnpj', name='empresas_cnpj_key'),
        Index('idx_empresas_cnpj', 'cnpj'),
        Index('idx_empresas_timezone', 'timezone'),
        Index('idx_empresas_ramos', 'ramos_id'),
        {'comment': 'Empresas cadastradas na plataforma (multi-tenant).'}
    )

    empresa_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    razao_social: Mapped[str] = mapped_column(String(120), nullable=False, comment='Razao social da empresa.')
    cnpj: Mapped[str] = mapped_column(String(14), nullable=False, comment='CNPJ da empresa, sem formatacao.')
    anfitria_usuario_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='Usuario que criou a empresa (anfitriao/superadmin).')
    ramos_id: Mapped[int] = mapped_column(BigInteger, nullable=False, server_default=text('1'), comment='Ramo de atuação da empresa.')
    timezone: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("'America/Sao_Paulo'::character varying"), comment='Fuso horario da empresa no padrao IANA (ex: America/Sao_Paulo).')
    criado_em: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    fantasia: Mapped[Optional[str]] = mapped_column(String(120), comment='Nome fantasia da empresa.')

    anfitria_usuario: Mapped['Usuarios'] = relationship('Usuarios', back_populates='empresas')
    ramo_rel: Mapped['Ramos'] = relationship('Ramos', back_populates='empresas')
    certificados: Mapped[list['Certificados']] = relationship('Certificados', back_populates='empresa')
    empresa_convites: Mapped[list['EmpresaConvites']] = relationship('EmpresaConvites', back_populates='empresa')
    empresa_membros: Mapped[list['EmpresaMembros']] = relationship('EmpresaMembros', back_populates='empresa')
    feriados: Mapped[list['Feriados']] = relationship('Feriados', back_populates='empresa')
    planos_trabalho: Mapped[list['PlanosTrabalho']] = relationship('PlanosTrabalho', back_populates='empresa')
    grupos: Mapped[list['Grupos']] = relationship('Grupos', back_populates='empresa')
    grupos_certificados: Mapped[list['GruposCertificados']] = relationship('GruposCertificados', back_populates='empresa')
    grupos_usuarios: Mapped[list['GruposUsuarios']] = relationship('GruposUsuarios', back_populates='empresa')
    regras_acesso: Mapped[list['RegrasAcesso']] = relationship('RegrasAcesso', back_populates='empresa')
    regras_acesso_hosts: Mapped[list['RegrasAcessoHosts']] = relationship('RegrasAcessoHosts', back_populates='empresa')
    global_urls: Mapped[list['GlobalUrls']] = relationship('GlobalUrls', back_populates='empresa')


class Certificados(Base):
    __tablename__ = 'certificados'
    __table_args__ = (
        ForeignKeyConstraint(['criado_por'], ['usuarios.usuario_id'], ondelete='RESTRICT', name='certificados_usuario_fk'),
        ForeignKeyConstraint(['empresa_id'], ['empresas.empresa_id'], ondelete='CASCADE', name='certificados_empresa_fk'),
        PrimaryKeyConstraint('certificado_id', name='certificados_pkey'),
        Index('idx_cert_criado_por', 'criado_por'),
        Index('idx_cert_emp', 'empresa_id'),
        {'comment': 'Certificados digitais criptografados das empresas.'}
    )

    certificado_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    empresa_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    criado_por: Mapped[int] = mapped_column(BigInteger, nullable=False)
    nome_arquivo: Mapped[str] = mapped_column(Text, nullable=False, comment='Nome original do arquivo de certificado.')
    encrypted: Mapped[str] = mapped_column(Text, nullable=False, comment='Dados do certificado em formato criptografado.')
    secret: Mapped[str] = mapped_column(Text, nullable=False, comment='Frase secreta ou chave auxiliar usada na criptografia.')
    criado_em: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    proprietario: Mapped[Optional[str]] = mapped_column(String, comment='Proprietario do certificado')
    emitido_por: Mapped[Optional[str]] = mapped_column(String, comment='Nome da entidade emissora do certificado')
    validade_inicio: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), comment='Data de inicio da validade')
    valido_ate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), comment='Data do fim da validade')

    usuarios: Mapped['Usuarios'] = relationship('Usuarios', back_populates='certificados')
    empresa: Mapped['Empresas'] = relationship('Empresas', back_populates='certificados')
    grupos_certificados: Mapped[list['GruposCertificados']] = relationship('GruposCertificados', back_populates='certificado')


class EmpresaConvites(Base):
    __tablename__ = 'empresa_convites'
    __table_args__ = (
        ForeignKeyConstraint(['convidado_usuario_id'], ['usuarios.usuario_id'], ondelete='SET NULL', name='convites_usuario_fk'),
        ForeignKeyConstraint(['empresa_id'], ['empresas.empresa_id'], ondelete='CASCADE', name='convites_empresa_fk'),
        PrimaryKeyConstraint('convite_id', name='empresa_convites_pkey'),
        UniqueConstraint('convite_uuid', name='empresa_convites_uuid_unq'),
        {'comment': 'Convites enviados por e-mail para adicionar membros Ë empresa.'}
    )

    convite_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    empresa_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    email_convidado: Mapped[str] = mapped_column(String(150), nullable=False, comment='E-mail da pessoa convidada para entrar na empresa.')
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'pendente'::character varying"), comment='Status do convite: pendente, aceito, expirado ou cancelado.')
    criado_em: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    convite_uuid: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, server_default=text('gen_random_uuid()'))
    convidado_usuario_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    expiracao: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text("(now() + '7 days'::interval)"))

    convidado_usuario: Mapped[Optional['Usuarios']] = relationship('Usuarios', back_populates='empresa_convites')
    empresa: Mapped['Empresas'] = relationship('Empresas', back_populates='empresa_convites')


class EmpresaMembros(Base):
    __tablename__ = 'empresa_membros'
    __table_args__ = (
        ForeignKeyConstraint(['empresa_id'], ['empresas.empresa_id'], ondelete='CASCADE', name='membros_empresa_fk'),
        ForeignKeyConstraint(['usuario_id'], ['usuarios.usuario_id'], ondelete='CASCADE', name='membros_usuario_fk'),
        PrimaryKeyConstraint('membro_id', name='empresa_membros_pkey'),
        UniqueConstraint('empresa_id', 'usuario_id', name='empresa_membros_unq'),
        Index('idx_emp_membros_emp', 'empresa_id'),
        Index('idx_emp_membros_user', 'usuario_id'),
        {'comment': 'Relaciona usuarios e empresas, com o papel de cada um.'}
    )

    membro_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    empresa_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    usuario_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    papel: Mapped[str] = mapped_column(Enum('ADMINISTRADOR', 'COMUM', name='usuario_nivel'), nullable=False, server_default=text("'COMUM'::usuario_nivel"), comment='Papel do usuario na empresa (superadmin, admin, user, etc.).')
    criado_em: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))

    empresa: Mapped['Empresas'] = relationship('Empresas', back_populates='empresa_membros')
    usuario: Mapped['Usuarios'] = relationship('Usuarios', back_populates='empresa_membros')


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


class GlobalUrls(Base):
    __tablename__ = 'global_urls'
    __table_args__ = (
        ForeignKeyConstraint(['empresa_id'], ['empresas.empresa_id'], ondelete='CASCADE', name='global_urls_empresa_fk'),
        PrimaryKeyConstraint('global_urls_id', name='global_urls_pkey'),
        Index('idx_global_urls_emp', 'empresa_id'),
        {'comment': 'URLs globais cadastradas por empresa.'}
    )

    global_urls_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, comment='Identificador único')
    url: Mapped[Optional[str]] = mapped_column(Text, comment='URL cadastrada')
    criado_em: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('now()'), comment='Data de criação')
    inativo: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'), comment='Indica se a URL está inativa')
    empresa_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='Chave estrangeira da empresa')

    empresa: Mapped['Empresas'] = relationship('Empresas', back_populates='global_urls')
