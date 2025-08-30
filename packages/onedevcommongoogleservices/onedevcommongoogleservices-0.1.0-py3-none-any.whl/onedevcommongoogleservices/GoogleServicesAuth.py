import json
from typing import Any, Dict, Optional, List
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials as UserCredentials
from google.oauth2.service_account import Credentials as SACredentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build as gapi_build
from google.cloud import pubsub_v1
from onedevcommongoogleservices.TokenStore import NullTokenStore, TokenStore


DEFAULT_SCOPES: List[str] = [
    # Escolhi o mínimo pra seus 4 serviços. Acrescente se precisar.
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/pubsub",
]

class GoogleServicesAuth:
    """
    Autentica 1x (OAuth Installed ou Service Account) e expõe
    builders p/ Gmail, Drive, Calendar (googleapiclient) e Pub/Sub (google-cloud).

    - Se precisar trocar scopes, crie uma nova instância.
    - Por padrão, não salva token. Pluge um TokenStore se quiser.
    """

    def __init__(
        self,
        credentials_json: Dict[str, Any],
        token_json: Optional[Dict[str, Any]] = None,
        scopes: Optional[List[str]] = None,
        *,
        delegated_user: Optional[str] = None,
        token_store: Optional[TokenStore] = None,
        allow_interactive: bool = True,
        user_agent: str = "GoogleServicesAuth/1.0",
    ):
        self._creds: Optional[Any] = None
        self._scopes = scopes[:] if scopes else DEFAULT_SCOPES[:]
        self._delegated_user = delegated_user
        self._credentials_json = credentials_json or {}
        self._token_json = token_json
        self._token_store = token_store or NullTokenStore()
        self._allow_interactive = allow_interactive
        self._user_agent = user_agent

        self._creds = self._build_credentials()
        self._ensure_valid_and_refresh_if_needed()

    # ---------- Público: acesso aos serviços ----------

    def gmail(self, version: str = "v1"):
        self._require_scopes(["https://www.googleapis.com/auth/gmail.modify"])
        return self._gapi("gmail", version)

    def drive(self, version: str = "v3"):
        self._require_scopes(["https://www.googleapis.com/auth/drive"])
        return self._gapi("drive", version)

    def calendar(self, version: str = "v3"):
        self._require_scopes(["https://www.googleapis.com/auth/calendar"])
        return self._gapi("calendar", version)

    def pubsub_publisher(self) -> pubsub_v1.PublisherClient:
        self._require_scopes(["https://www.googleapis.com/auth/pubsub"])
        return pubsub_v1.PublisherClient(credentials=self._creds, client_info={"user_agent": self._user_agent})

    def pubsub_subscriber(self) -> pubsub_v1.SubscriberClient:
        self._require_scopes(["https://www.googleapis.com/auth/pubsub"])
        return pubsub_v1.SubscriberClient(credentials=self._creds, client_info={"user_agent": self._user_agent})

    # ---------- Internos ----------

    def _gapi(self, api: str, version: str):
        # Usa o mesmo credential pra todos os serviços
        return gapi_build(api, version, credentials=self._creds, cache_discovery=False)

    def _is_service_account_payload(self) -> bool:
        # SA padrão tem chave 'type': 'service_account' ou pelo menos private_key/client_email
        cj = self._credentials_json
        return (
            cj.get("type") == "service_account"
            or ("private_key" in cj and "client_email" in cj)
        )

    def _is_installed_client_payload(self) -> bool:
        cj = self._credentials_json
        return "installed" in cj or "web" in cj

    def _build_credentials(self):
        if self._is_service_account_payload():
            return self._build_sa_credentials()

        if self._is_installed_client_payload():
            return self._build_oauth_credentials()

        raise ValueError(
            "credentials_json inválido: informe Service Account (dict com 'type=service_account' "
            "ou 'private_key'/'client_email'), ou Client Secret ('installed'/'web')."
        )

    def _build_sa_credentials(self):
        # Para SA, *scopes* são aplicados ao JWT quando necessário (APIs HTTP).
        creds = SACredentials.from_service_account_info(self._credentials_json, scopes=self._scopes)
        if self._delegated_user:
            creds = creds.with_subject(self._delegated_user)
        return creds

    def _build_oauth_credentials(self):
        # Ordem de fontes:
        # 1) token_json fornecido (authorized_user style)
        # 2) token_store.load()
        # 3) interactive flow (se allow_interactive=True)
        # 4) erro
        token_info = None

        if self._token_json:
            token_info = self._normalize_authorized_user_info(self._token_json)
        else:
            token_info = self._token_store.load()
            if token_info is not None:
                token_info = self._normalize_authorized_user_info(token_info)

        if token_info:
            creds = UserCredentials.from_authorized_user_info(token_info, scopes=self._scopes)
            # Ajuste de scopes se o token veio com menos escopos (requer refresh/grant)
            # O google-auth ajusta internamente; se não cobrir, vai precisar re-consentir via interactive flow.
            return creds

        if not self._allow_interactive:
            raise ValueError(
                "token_json ausente e allow_interactive=False. "
                "Forneça token_json, pluge um TokenStore com token, ou habilite allow_interactive."
            )

        # Flow interativo: InstalledApp (web tb funciona com run_local_server)
        flow = InstalledAppFlow.from_client_config(self._credentials_json, scopes=self._scopes)
        creds = flow.run_local_server(port=0)
        # Persistir se houver TokenStore
        try:
            self._token_store.save(json.loads(creds.to_json()))
        except Exception:
            pass
        return creds

    def _normalize_authorized_user_info(self, info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aceita tanto payload completo de authorized_user quanto pares token/refresh.
        Normaliza pro formato esperado por `from_authorized_user_info`.
        """
        if "type" in info and info["type"] == "authorized_user":
            return info

        # Monta um "authorized_user" do zero com os campos comuns
        client_id = info.get("client_id") or (self._credentials_json.get("installed") or {}).get("client_id")
        client_secret = info.get("client_secret") or (self._credentials_json.get("installed") or {}).get("client_secret")
        token_uri = info.get("token_uri") or "https://oauth2.googleapis.com/token"
        scopes = info.get("scopes") or self._scopes

        if not client_id or not client_secret:
            raise ValueError("Para token_json sem 'type=authorized_user', é necessário client_id e client_secret.")

        return {
            "type": "authorized_user",
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": info.get("refresh_token"),
            "token": info.get("token"),
            "token_uri": token_uri,
            "scopes": scopes,
        }

    def _ensure_valid_and_refresh_if_needed(self):
        # Tenta refresh silencioso quando possível (OAuth).
        if hasattr(self._creds, "expired") and getattr(self._creds, "expired") and getattr(self._creds, "refresh_token", None):
            self._creds.refresh(Request())
            # Atualiza store se for OAuth
            if isinstance(self._creds, UserCredentials):
                try:
                    self._token_store.save(json.loads(self._creds.to_json()))
                except Exception:
                    pass

    def _require_scopes(self, required: List[str]):
        # Garante que os scopes necessários já estavam presentes na criação.
        # Se não estiver, força recriação da instância (design que você pediu).
        missing = [s for s in required if s not in self._scopes]
        if missing:
            raise RuntimeError(
                f"Scopes ausentes: {missing}. Recrie GoogleServicesAuth com os scopes necessários."
            )

    # ---------- Utilidades ----------

    @property
    def scopes(self) -> List[str]:
        return self._scopes[:]

    @property
    def creds(self):
        """Acesso direto ao Credentials (evite trocar scopes aqui)."""
        return self._creds