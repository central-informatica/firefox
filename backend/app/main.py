from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import FRONTEND_ORIGINS
from backend.app.api.routes.auth import router as auth_router
from backend.app.api.routes.certificados import router as cert_router
from backend.app.api.routes.usuarios import router as user_router


app = FastAPI(title="Certificado Protegido")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas
app.include_router(auth_router)
app.include_router(cert_router)
app.include_router(user_router)


@app.get("/")
def healthcheck():
    return {"status": "ok", "message": "API funcionando"}
