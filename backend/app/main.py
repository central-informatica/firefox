from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import FRONTEND_ORIGINS
from backend.app.api.routes.grupos import router as grupos_router
from backend.app.api.routes.planos_trabalho import router as planos_trabalho_router
from backend.app.api.routes.feriados import router as feriados_router
from backend.app.api.routes.grupos_certificados import router as grupos_certificados_router
from backend.app.api.routes.grupos_usuarios import router as grupos_usuarios_router
from backend.app.api.routes.regras_acesso import router as regras_acesso
from backend.app.api.routes.regras_acesso_hosts import router as regras_acesso_hosts


app = FastAPI(title="Certificado Protegido")

app.add_middleware(
    CORSMiddleware,
    # allow_origins=FRONTEND_ORIGINS,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(grupos_router)
app.include_router(grupos_certificados_router)
app.include_router(grupos_usuarios_router)
app.include_router(planos_trabalho_router)
app.include_router(feriados_router)
app.include_router(regras_acesso)
app.include_router(regras_acesso_hosts)

@app.get("/")
def healthcheck():
    return {"status": "ok", "message": "API funcionando"}
