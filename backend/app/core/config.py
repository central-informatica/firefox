import os
from pathlib import Path
from dotenv import load_dotenv
from backend.app.utils.chave_mestra import gerar_chave

load_dotenv()

DEBUG = os.getenv("DEBUG", "false").lower() == "true"

FRONTEND_ORIGINS = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
]

# Add custom origin from env if specified and different from defaults
_custom_origin = os.getenv("FRONTEND_ORIGIN")
if _custom_origin and _custom_origin not in FRONTEND_ORIGINS:
    FRONTEND_ORIGINS.append(_custom_origin)

MASTER_KEY = gerar_chave(password=os.getenv("MASTER_KEY"))

STORAGE_DIR = os.getenv("CERT_STORAGE_DIR", "storage/certificados")
Path(STORAGE_DIR).mkdir(parents=True, exist_ok=True)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@127.0.0.1:5432/certprot"
)
