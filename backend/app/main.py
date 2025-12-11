from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import FRONTEND_ORIGINS
from backend.app.api.routes.auth import router as auth_router
from backend.app.api.routes.certificados import router as cert_router
from backend.app.api.routes.usuarios import router as user_router
from backend.app.api.routes.empresas import router as empresas_router
from backend.app.api.routes.grupos import router as grupos_router
from backend.app.api.routes.planos_trabalho import router as planos_trabalho_router
from backend.app.api.routes.empresa_convites import router as empresa_convites
#from backend.app.api.routes.empresa_membros import router as empresa_membros


app = FastAPI(title="Certificado Protegido")

app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(cert_router)
app.include_router(user_router)
app.include_router(empresas_router)
app.include_router(grupos_router)
app.include_router(planos_trabalho_router)
app.include_router(empresa_convites)
#app.include_router(empresa_membros)


@app.get("/")
def healthcheck():
    return {"status": "ok", "message": "API funcionando"}
