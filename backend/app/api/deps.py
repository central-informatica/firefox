"""
Dependências da API (FastAPI Depends).

Funções definidas aqui são injetadas automaticamente nos endpoints
via `Depends()`, como autenticação do usuário, verificação de sessão,
controle de acesso e outras validações compartilhadas.
"""

# backend/app/api/deps.py

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.security import validar_token
from backend.app.db.models import Usuarios


def get_current_user(
    usuario: Usuarios = Depends(validar_token),
) -> Usuarios:
    """
    Retorna o usuário autenticado a partir do token/sessão.
    Centraliza a lógica de autenticação para os endpoints.
    """
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não autenticado",
        )

    return usuario