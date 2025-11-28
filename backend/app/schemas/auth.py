from pydantic import BaseModel

class LoginJSON(BaseModel):
    email: str
    senha: str


class UserOut(BaseModel):
    id: int
    nome: str
    email: str
    empresa_id: int | None = None
