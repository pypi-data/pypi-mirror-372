import json
from typing import Any, Dict, Optional, Protocol, runtime_checkable

@runtime_checkable
class TokenStore(Protocol):
    """Interface p/ persistir token OAuth (opcional)."""
    def load(self) -> Optional[Dict[str, Any]]: ...
    def save(self, authorized_user_info: Dict[str, Any]) -> None: ...
    
class NullTokenStore:
    """Sem persistência (default)."""
    def load(self) -> Optional[Dict[str, Any]]:
        return None
    def save(self, authorized_user_info: Dict[str, Any]) -> None:
        pass
    
class FileTokenStore:
    """Exemplo simples de persistência em arquivo (se quiser usar)."""
    def __init__(self, path: str):
        self.path = path
    def load(self) -> Optional[Dict[str, Any]]:
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return None
    def save(self, authorized_user_info: Dict[str, Any]) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(authorized_user_info, f)