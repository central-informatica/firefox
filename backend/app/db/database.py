from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
import os

# ---------------------------------------------------------------------
# 1) BUSCAR URL DO BANCO
# (pode vir do .env ou ser hardcode para teste)
# ---------------------------------------------------------------------
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/backend_certificado"
)

# ---------------------------------------------------------------------
# 2) CRIA ENGINE DO POSTGRES
# ---------------------------------------------------------------------
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    poolclass=NullPool   # garante reinicialização limpa no reload
)

# ---------------------------------------------------------------------
# 3) SESSION FACTORY
# ---------------------------------------------------------------------
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ---------------------------------------------------------------------
# 4) BASE PARA OS MODELOS
# ---------------------------------------------------------------------
Base = declarative_base()

# ---------------------------------------------------------------------
# 5) FUNÇÃO PADRÃO DO FASTAPI PARA OBTER A SESSÃO DO BANCO
# ---------------------------------------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
