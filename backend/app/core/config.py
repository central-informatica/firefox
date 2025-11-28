import os
from pathlib import Path

from dotenv import load_dotenv
from backend.app.utils.chave_mestra import gerar_chave

load_dotenv()

# Origem do frontend no DEV
FRONTEND_ORIGINS = [
    os.getenv("FRONTEND_ORIGIN", "http://127.0.0.1:5173"),
]

# Chave mestra usada no encrypt_pfx/decrypt_pfx
MASTER_KEY = gerar_chave(password=os.getenv("MASTER_KEY"))

# Pasta onde você guarda os JSON de certificados (se ainda usar filesystem)
STORAGE_DIR = os.getenv("CERT_STORAGE_DIR", "storage/certificados")
Path(STORAGE_DIR).mkdir(parents=True, exist_ok=True)
