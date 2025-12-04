from typing import Optional
import datetime
import uuid

from sqlalchemy import ARRAY, BigInteger, Boolean, Date, DateTime, Enum, ForeignKeyConstraint, Index, Integer, PrimaryKeyConstraint, String, Text, UniqueConstraint, Uuid, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass


class Usuarios(Base):
    __tablename__ = 'usuarios'
    __table_args__ = (
        PrimaryKeyConstraint('usuario_id', name='usuarios_pkey'),
        UniqueConstraint('email', name='usuarios_email_key'),
        Index('idx_usuarios_email', 'email'),
        {'comment': 'Cadastro geral de usu▀rios da plataforma.'}
    )

    usuario_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    nome: Mapped[str] = mapped_column(String(80), nullable=False, comment='Nome completo do usu▀rio.')
    email: Mapped[str] = mapped_column(String(150), nullable=False, comment='E-mail utilizado para login na plataforma.')
    senha_hash: Mapped[str] = mapped_column(Text, nullable=False)
    email_verificado: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    criado_em: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    atualizado_em: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    nivel: Mapped[str] = mapped_column(Enum('ADMINISTRADOR', 'COMUM', name='usuario_nivel'), nullable=False, server_default=text("'COMUM'::usuario_nivel"), comment='NÝvel global do usußrio na plataforma SaaS. ADMINISTRADOR = acesso total ao sistema. COMUM = usußrio padrÒo.')
    telefone: Mapped[Optional[str]] = mapped_column(String(40))

    acesso: Mapped[list['Acesso']] = relationship('Acesso', back_populates='usuarios')
    empresas: Mapped[list['Empresas']] = relationship('Empresas', back_populates='anfitria_usuario')
    certificados: Mapped[list['Certificados']] = relationship('Certificados', back_populates='usuarios')
    empresa_convites: Mapped[list['EmpresaConvites']] = relationship('EmpresaConvites', back_populates='convidado_usuario')
    empresa_membros: Mapped[list['EmpresaMembros']] = relationship('EmpresaMembros', back_populates='usuario')
    grupos_usuarios: Mapped[list['GruposUsuarios']] = relationship('GruposUsuarios', back_populates='usuario')


class Acesso(Base):
    __tablename__ = 'acesso'
    __table_args__ = (
        ForeignKeyConstraint(['id_usuario'], ['usuarios.usuario_id'], name='acesso_id_usuario_fkey'),
        PrimaryKeyConstraint('acesso_id', name='acesso_pkey'),
        UniqueConstraint('token', name='acesso_token_key')
    )

    acesso_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    id_usuario: Mapped[int] = mapped_column(BigInteger, nullable=False)
    token: Mapped[str] = mapped_column(String(255), nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    criado_em: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))

    usuarios: Mapped['Usuarios'] = relationship('Usuarios', back_populates='acesso')


class Empresas(Base):
    __tablename__ = 'empresas'
    __table_args__ = (
        ForeignKeyConstraint(['anfitria_usuario_id'], ['usuarios.usuario_id'], ondelete='RESTRICT', onupdate='CASCADE', name='empresas_anfitria_fk'),
        PrimaryKeyConstraint('empresa_id', name='empresas_pkey'),
        UniqueConstraint('cnpj', name='empresas_cnpj_key'),
        Index('idx_empresas_cnpj', 'cnpj'),
        Index('idx_empresas_timezone', 'timezone'),
        {'comment': 'Empresas cadastradas na plataforma (multi-tenant).'}
    )

    empresa_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    razao_social: Mapped[str] = mapped_column(String(120), nullable=False, comment='RazÊo social da empresa.')
    cnpj: Mapped[str] = mapped_column(String(14), nullable=False, comment='CNPJ da empresa, sem formata■Êo.')
    anfitria_usuario_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment='Usu▀rio que criou a empresa (anfitriÊo/superadmin).')
    timezone: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("'America/Sao_Paulo'::character varying"), comment='Fuso hor▀rio da empresa no padrÊo IANA (ex: America/Sao_Paulo).')
    criado_em: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    fantasia: Mapped[Optional[str]] = mapped_column(String(120), comment='Nome fantasia da empresa.')

    anfitria_usuario: Mapped['Usuarios'] = relationship('Usuarios', back_populates='empresas')
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
    proprietario: Mapped[Optional[str]] = mapped_column(String, comment='Proprietßrio do certificado')
    emitido_por: Mapped[Optional[str]] = mapped_column(String, comment='Nome da entidade emissora do certificado')
    validade_inicio: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), comment='Data de inÝcio da validade')
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
        {'comment': 'Relaciona usu▀rios Ës empresas, com o papel de cada um.'}
    )

    membro_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    empresa_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    usuario_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    papel: Mapped[str] = mapped_column(Enum('ADMINISTRADOR', 'COMUM', name='usuario_nivel'), nullable=False, server_default=text("'COMUM'::usuario_nivel"), comment='Papel do usu▀rio na empresa (superadmin, admin, user, etc.).')
    criado_em: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))

    empresa: Mapped['Empresas'] = relationship('Empresas', back_populates='empresa_membros')
    usuario: Mapped['Usuarios'] = relationship('Usuarios', back_populates='empresa_membros')


class Feriados(Base):
    __tablename__ = 'feriados'
    __table_args__ = (
        ForeignKeyConstraint(['empresa_id'], ['empresas.empresa_id'], ondelete='CASCADE', name='feriados_empresa_fk'),
        PrimaryKeyConstraint('feriado_id', name='feriados_pkey'),
        Index('idx_feriados_emp_data', 'empresa_id', 'data'),
        {'comment': 'Feriados cadastrados por empresa, usados para bloquear acessos.'}
    )

    feriado_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    empresa_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    data: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    recorrente: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'), comment='Indica se o feriado se repete todos os anos na mesma data.')
    criado_em: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))

    empresa: Mapped['Empresas'] = relationship('Empresas', back_populates='feriados')


class PlanosTrabalho(Base):
    __tablename__ = 'planos_trabalho'
    __table_args__ = (
        ForeignKeyConstraint(['empresa_id'], ['empresas.empresa_id'], ondelete='CASCADE', name='planos_empresa_fk'),
        PrimaryKeyConstraint('plano_id', name='planos_trabalho_pkey'),
        UniqueConstraint('empresa_id', 'nome', name='planos_trabalho_unq'),
        Index('idx_planos_emp', 'empresa_id'),
        {'comment': 'Planos de trabalho de uma empresa (modelos de regras e grupos).'}
    )

    plano_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    empresa_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    nome: Mapped[str] = mapped_column(String(100), nullable=False, comment='Nome do plano de trabalho (deve ser Ànico dentro da empresa).')
    criado_em: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    descricao: Mapped[Optional[str]] = mapped_column(Text)

    empresa: Mapped['Empresas'] = relationship('Empresas', back_populates='planos_trabalho')
    grupos: Mapped[list['Grupos']] = relationship('Grupos', back_populates='plano')


class Grupos(Base):
    __tablename__ = 'grupos'
    __table_args__ = (
        ForeignKeyConstraint(['empresa_id'], ['empresas.empresa_id'], ondelete='CASCADE', name='grupos_empresa_fk'),
        ForeignKeyConstraint(['plano_id'], ['planos_trabalho.plano_id'], ondelete='CASCADE', name='grupos_plano_fk'),
        PrimaryKeyConstraint('grupo_id', name='grupos_pkey'),
        UniqueConstraint('empresa_id', 'nome', name='grupos_unq'),
        Index('idx_grupos_emp', 'empresa_id'),
        Index('idx_grupos_plano', 'plano_id'),
        {'comment': 'Grupos de usu▀rios pertencentes a planos de trabalho de uma '
                'empresa.'}
    )

    grupo_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    empresa_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    plano_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    nome: Mapped[str] = mapped_column(String(100), nullable=False, comment='Nome do grupo (Ànico dentro da empresa).')
    criado_em: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))

    empresa: Mapped['Empresas'] = relationship('Empresas', back_populates='grupos')
    plano: Mapped['PlanosTrabalho'] = relationship('PlanosTrabalho', back_populates='grupos')
    grupos_certificados: Mapped[list['GruposCertificados']] = relationship('GruposCertificados', back_populates='grupo')
    grupos_usuarios: Mapped[list['GruposUsuarios']] = relationship('GruposUsuarios', back_populates='grupo')
    regras_acesso: Mapped[list['RegrasAcesso']] = relationship('RegrasAcesso', back_populates='grupo')
    regras_acesso_hosts: Mapped[list['RegrasAcessoHosts']] = relationship('RegrasAcessoHosts', back_populates='grupo')


class GruposCertificados(Base):
    __tablename__ = 'grupos_certificados'
    __table_args__ = (
        ForeignKeyConstraint(['certificado_id'], ['certificados.certificado_id'], ondelete='CASCADE', name='grupos_certificados_cert_fk'),
        ForeignKeyConstraint(['empresa_id'], ['empresas.empresa_id'], ondelete='CASCADE', name='grupos_certificados_empresa_fk'),
        ForeignKeyConstraint(['grupo_id'], ['grupos.grupo_id'], ondelete='CASCADE', name='grupos_certificados_grupo_fk'),
        PrimaryKeyConstraint('grupo_cert_id', name='grupos_certificados_pkey'),
        UniqueConstraint('grupo_id', 'certificado_id', name='grupos_certificados_unq'),
        Index('idx_g_cert_cert', 'certificado_id'),
        Index('idx_g_cert_emp', 'empresa_id'),
        Index('idx_g_cert_grupo', 'grupo_id'),
        {'comment': 'Rela■Êo de quais certificados cada grupo pode acessar.'}
    )

    grupo_cert_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    empresa_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    grupo_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    certificado_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

    certificado: Mapped['Certificados'] = relationship('Certificados', back_populates='grupos_certificados')
    empresa: Mapped['Empresas'] = relationship('Empresas', back_populates='grupos_certificados')
    grupo: Mapped['Grupos'] = relationship('Grupos', back_populates='grupos_certificados')


class GruposUsuarios(Base):
    __tablename__ = 'grupos_usuarios'
    __table_args__ = (
        ForeignKeyConstraint(['empresa_id'], ['empresas.empresa_id'], ondelete='CASCADE', name='grupos_usuarios_empresa_fk'),
        ForeignKeyConstraint(['grupo_id'], ['grupos.grupo_id'], ondelete='CASCADE', name='grupos_usuarios_grupo_fk'),
        ForeignKeyConstraint(['usuario_id'], ['usuarios.usuario_id'], ondelete='CASCADE', name='grupos_usuarios_usuario_fk'),
        PrimaryKeyConstraint('grupo_usuario_id', name='grupos_usuarios_pkey'),
        UniqueConstraint('grupo_id', 'usuario_id', name='grupos_usuarios_unq'),
        Index('idx_g_usuarios_emp', 'empresa_id'),
        Index('idx_g_usuarios_grupo', 'grupo_id'),
        Index('idx_g_usuarios_user', 'usuario_id'),
        {'comment': 'Rela■Êo entre usu▀rios e grupos, dentro de uma empresa.'}
    )

    grupo_usuario_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    empresa_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    grupo_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    usuario_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

    empresa: Mapped['Empresas'] = relationship('Empresas', back_populates='grupos_usuarios')
    grupo: Mapped['Grupos'] = relationship('Grupos', back_populates='grupos_usuarios')
    usuario: Mapped['Usuarios'] = relationship('Usuarios', back_populates='grupos_usuarios')


class RegrasAcesso(Base):
    __tablename__ = 'regras_acesso'
    __table_args__ = (
        ForeignKeyConstraint(['empresa_id'], ['empresas.empresa_id'], ondelete='CASCADE', name='regras_empresa_fk'),
        ForeignKeyConstraint(['grupo_id'], ['grupos.grupo_id'], ondelete='CASCADE', name='regras_grupo_fk'),
        PrimaryKeyConstraint('regra_id', name='regras_acesso_pkey'),
        Index('idx_regras_acesso_hosts_emp', 'empresa_id'),
        Index('idx_regras_acesso_hosts_grupo', 'grupo_id'),
        Index('idx_regras_emp', 'empresa_id'),
        Index('idx_regras_grupo', 'grupo_id'),
        {'comment': 'Regras de dias e hor▀rios permitidos para grupos de uma empresa.'}
    )

    regra_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    empresa_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    grupo_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    tipo_dia: Mapped[str] = mapped_column(String(20), nullable=False, comment='Tipo de regra: corridos, uteis ou especificos.')
    horarios: Mapped[dict] = mapped_column(JSONB, nullable=False, comment='Lista de janelas de hor▀rio em JSON (inicio/fim no formato HH:MI).')
    criado_em: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    dias_especificos: Mapped[Optional[list[int]]] = mapped_column(ARRAY(Integer()), comment='Lista de dias (ex: 1=segunda ... 7=domingo) quando tipo_dia = especificos.')

    empresa: Mapped['Empresas'] = relationship('Empresas', back_populates='regras_acesso')
    grupo: Mapped['Grupos'] = relationship('Grupos', back_populates='regras_acesso')


class RegrasAcessoHosts(Base):
    __tablename__ = 'regras_acesso_hosts'
    __table_args__ = (
        ForeignKeyConstraint(['empresa_id'], ['empresas.empresa_id'], ondelete='CASCADE', name='regras_empresa_fk'),
        ForeignKeyConstraint(['grupo_id'], ['grupos.grupo_id'], ondelete='CASCADE', name='regras_grupo_fk'),
        PrimaryKeyConstraint('regra_id', name='regras_acesso_hosts_pkey')
    )

    regra_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    empresa_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    grupo_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    tipo_dia: Mapped[str] = mapped_column(String(20), nullable=False)
    horarios: Mapped[dict] = mapped_column(JSONB, nullable=False)
    criado_em: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    dias_especificos: Mapped[Optional[list[int]]] = mapped_column(ARRAY(Integer()))
    urls: Mapped[Optional[str]] = mapped_column(Text)

    empresa: Mapped['Empresas'] = relationship('Empresas', back_populates='regras_acesso_hosts')
    grupo: Mapped['Grupos'] = relationship('Grupos', back_populates='regras_acesso_hosts')
