from pydantic import BaseModel

class SignRequest(BaseModel):
    cert_id: str
    data: str  # digest (hash) em base64
