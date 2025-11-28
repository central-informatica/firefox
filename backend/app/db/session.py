from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

#DATABASE_URL = "postgresql+psycopg2://certpro:seq098@192.168.10.36:5432/cert-prot"
DATABASE_URL = "postgresql+psycopg2://postgres:seq098@192.168.10.36:5432/cert-prot"

engine = create_engine(
    DATABASE_URL,
    echo=False,  # pode ativar para debug
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)