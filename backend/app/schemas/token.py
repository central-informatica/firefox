from dataclasses import dataclass
from typing import Optional

@dataclass
class TokenContext:
    """
    Authentication context returned by token validation dependencies.
    """

    token_id: int
    usuario_id: int
    permissions: dict
    tipo_cliente: str

    @property
    def id_usuario(self) -> int:
        
        return self.usuario_id

    def get_usuario_nivel(self) -> str:
        return self.permissions.get("usuario_nivel", "COMUM")

    def is_admin(self) -> bool:
        return self.get_usuario_nivel() == "ADMINISTRADOR"

    def get_empresas(self) -> list:
        return self.permissions.get("empresas", [])

    def has_empresa_access(self, empresa_id: int) -> bool:
        """
        Check if user has access to a specific empresa.
        """
        return any(e["empresa_id"] == empresa_id for e in self.get_empresas())

    def get_empresa_papel(self, empresa_id: int) -> Optional[str]:
        """
        Get user's role within a specific empresa.
        """
        for emp in self.get_empresas():
            if emp["empresa_id"] == empresa_id:
                return emp["papel"]
        return None

    def is_admin_in_empresa(self, empresa_id: int) -> bool:
        """
        Check if user is an administrator in a specific empresa.

        """
        return self.get_empresa_papel(empresa_id) == "ADMINISTRADOR"

    def get_empresa_ids(self) -> list[int]:
        """
        Useful for filtering queries by multiple empresas.

        """
        return [e["empresa_id"] for e in self.get_empresas()]

    def has_any_empresa_access(self) -> bool:
        """
        Check if user has access to at least one empresa.
        """
        return len(self.get_empresas()) > 0

    def is_web_client(self) -> bool:
        """
        Check if the token belongs to a web browser client.

        """
        return self.tipo_cliente == "WEB"

    def is_desktop_client(self) -> bool:
        """
        Check if the token belongs to a desktop application client.

        """
        return self.tipo_cliente == "DESKTOP"
