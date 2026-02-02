import os
from pathlib import Path
from dotenv import load_dotenv
from backend.app.utils.chave_mestra import gerar_chave

load_dotenv()

DEBUG = os.getenv("DEBUG", "false").lower() == "true"

FRONTEND_ORIGINS = [
    os.getenv("FRONTEND_ORIGIN", "http://127.0.0.1:5173"),
]

MASTER_KEY = gerar_chave(password=os.getenv("MASTER_KEY"))

STORAGE_DIR = os.getenv("CERT_STORAGE_DIR", "storage/certificados")
Path(STORAGE_DIR).mkdir(parents=True, exist_ok=True)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@127.0.0.1:5432/certprot"
)
