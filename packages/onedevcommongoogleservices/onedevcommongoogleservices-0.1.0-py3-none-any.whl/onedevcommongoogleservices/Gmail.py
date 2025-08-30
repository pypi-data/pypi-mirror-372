from __future__ import annotations

import os
import io
import zipfile
import base64
from typing import Any, Dict, Iterable, List, Optional, Tuple, Callable

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from onedevcommongoogleservices.GoogleServicesAuth import GoogleServicesAuth


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _b64url_decode(data: str) -> bytes:
    # Gmail pode mandar sem padding; ajusta
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


class GmailService:
    """
    Service para Gmail que reutiliza credenciais do GoogleServicesAuth.
    Nada de re-autenticar aqui — só consome o client já autenticado.
    """

    def __init__(self, auth: "GoogleServicesAuth", user_id: str = "me"):
        """
        :param auth: instância já criada do GoogleServicesAuth (com scopes de gmail)
        :param user_id: "me" (default) ou e-mail alvo (em DWD / delegated)
        """
        self._svc = auth.gmail()  # googleapiclient.discovery.Resource
        self._user = user_id

    def list_messages(
        self,
        q: Optional[str] = None,
        label_ids: Optional[List[str]] = None,
        include_spam_trash: bool = False,
        limit: Optional[int] = None,
        page_size: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Lista mensagens por query/labels, com paginação opcional.

        :return: lista de {id, threadId}
        """
        msgs: List[Dict[str, Any]] = []
        page_token: Optional[str] = None

        while True:
            req = self._svc.users().messages().list(
                userId=self._user,
                q=q,
                labelIds=label_ids or [],
                includeSpamTrash=include_spam_trash,
                maxResults=min(page_size, (limit - len(msgs)) if limit else page_size),
                pageToken=page_token,
            )
            resp = req.execute()
            chunk = resp.get("messages", [])
            msgs.extend(chunk)

            if limit and len(msgs) >= limit:
                return msgs[:limit]

            page_token = resp.get("nextPageToken")
            if not page_token:
                break

        return msgs

    def list_messages_from(self, sender_email: str, **kwargs) -> List[Dict[str, Any]]:
        q = f'from:{sender_email}'
        return self.list_messages(q=q, **kwargs)

    def get_message(
        self,
        message_id: str,
        fmt: str = "full",  # "minimal" | "metadata" | "full" | "raw"
        metadata_headers: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        req = self._svc.users().messages().get(
            userId=self._user,
            id=message_id,
            format=fmt,
            metadataHeaders=metadata_headers or [],
        )
        return req.execute()

    def _walk_parts(self, payload: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
        """
        Itera recursivamente por todas as 'parts' de um payload 'full'.
        """
        if not payload:
            return
        stack = [payload]
        while stack:
            p = stack.pop()
            yield p
            for child in p.get("parts", []) or []:
                stack.append(child)

    def download_attachments_to(
        self,
        message_id: str,
        dest_dir: str,
        filename_filter: Optional[Callable[[str], bool]] = None,
        unzip: bool = True,
    ) -> List[str]:
        """
        Baixa anexos da mensagem para `dest_dir`. Se `unzip=True`, extrai ZIPs.
        :return: lista de caminhos salvos (e, se unzip=True, dos arquivos extraídos).
        """
        os.makedirs(dest_dir, exist_ok=True)
        saved_paths: List[str] = []

        msg = self.get_message(message_id, fmt="full")
        payload = msg.get("payload", {}) or {}

        for part in self._walk_parts(payload):
            filename = part.get("filename") or ""
            body = part.get("body") or {}
            attach_id = body.get("attachmentId")

            if not filename or not attach_id:
                continue
            if filename_filter and not filename_filter(filename):
                continue

            attachment = self._svc.users().messages().attachments().get(
                userId=self._user, messageId=message_id, id=attach_id
            ).execute()
            data_b64 = attachment.get("data")
            if not data_b64:
                continue

            content = _b64url_decode(data_b64)
            out_path = os.path.join(dest_dir, filename)
            with open(out_path, "wb") as f:
                f.write(content)
            saved_paths.append(out_path)

            if unzip and filename.lower().endswith(".zip"):
                with zipfile.ZipFile(io.BytesIO(content)) as zf:
                    zf.extractall(dest_dir)
                    for n in zf.namelist():
                        saved_paths.append(os.path.join(dest_dir, n))

        return saved_paths

    def send_email(
        self,
        from_addr: str,
        to: str | List[str],
        subject: str,
        html_body: str,
        *,
        cc: Optional[str | List[str]] = None,
        bcc: Optional[str | List[str]] = None,
        attachments: Optional[List[str]] = None,
        headers: Optional[List[Tuple[str, str]]] = None,
    ) -> Dict[str, Any]:
        """
        Envia um e-mail com HTML e anexos.

        :param from_addr: remetente (precisa estar autorizado pela conta)
        :param to: string ou lista
        :param cc/bcc: string ou lista
        :param attachments: caminhos de arquivos
        :param headers: headers extras [(k,v)]
        :return: resposta do Gmail API (message resource)
        """
        def _as_list(x: Optional[str | List[str]]) -> List[str]:
            if not x:
                return []
            return [x] if isinstance(x, str) else list(x)

        msg = MIMEMultipart()
        msg["From"] = from_addr
        to_list = _as_list(to)
        cc_list = _as_list(cc)
        bcc_list = _as_list(bcc)
        all_rcpts = to_list + cc_list + bcc_list

        if to_list:
            msg["To"] = ", ".join(to_list)
        if cc_list:
            msg["Cc"] = ", ".join(cc_list)
        msg["Subject"] = subject

        if headers:
            for k, v in headers:
                msg[k] = v

        msg.attach(MIMEText(html_body, "html", "utf-8"))

        for path in (attachments or []):
            with open(path, "rb") as fp:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(fp.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f'attachment; filename="{os.path.basename(path)}"')
            msg.attach(part)

        raw = _b64url_encode(msg.as_string().encode("utf-8"))
        # Dica: para "send-as", pode precisar setar 'From' compatível com alias autorizado
        return self._svc.users().messages().send(
            userId=self._user,
            body={"raw": raw},
        ).execute()



if __name__ == "__main__":
    None
    # auth = GoogleServicesAuth(
    #     credentials_json=credentials_json_installed,
    #     token_json=token_json,
    # )

    # gmail = GmailService(auth)
    # msgs = gmail.list_messages(q=None, limit=20)
    # print(msgs)