from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
import json
import base64
from google.iam.v1 import policy_pb2
from onedevcommongoogleservices.GoogleServicesAuth import GoogleServicesAuth

GMAIL_PUSH_PUBLISHER = "serviceAccount:gmail-api-push@system.gserviceaccount.com"


class PubSubService:
    """
    Pub/Sub usando a MESMA credencial do GoogleServicesAuth.
    Nada de re-autenticar aqui.
    """
    def __init__(self, auth: "GoogleServicesAuth"):
        self._publisher = auth.pubsub_publisher()
        self._subscriber = auth.pubsub_subscriber()

    def ensure_topic(self, project_id: str, topic_name: str) -> str:
        """
        Garante que o tópico exista. Aceita nome simples ou full path.
        Retorna 'projects/{project}/topics/{name}'.
        """
        if topic_name.startswith("projects/"):
            topic_path = topic_name
        else:
            topic_path = self._publisher.topic_path(project_id, topic_name)

        try:
            self._publisher.get_topic(request={"topic": topic_path})
        except Exception:
            self._publisher.create_topic(request={"name": topic_path})
        return topic_path

    def ensure_subscription(
        self,
        project_id: str,
        subscription_name: str,
        topic_path_or_name: str,
        push_endpoint: Optional[str] = None,
        ack_deadline_seconds: int = 10,
    ) -> str:
        """
        Garante que a subscription exista (pull padrão ou push se push_endpoint).
        Retorna 'projects/{project}/subscriptions/{name}'.
        """
        if subscription_name.startswith("projects/"):
            sub_path = subscription_name
        else:
            sub_path = self._subscriber.subscription_path(project_id, subscription_name)

        topic_path = topic_path_or_name
        if not topic_path.startswith("projects/"):
            topic_path = self._publisher.topic_path(project_id, topic_path_or_name)

        try:
            self._subscriber.get_subscription(request={"subscription": sub_path})
        except Exception:
            if push_endpoint:
                self._subscriber.create_subscription(
                    request={
                        "name": sub_path,
                        "topic": topic_path,
                        "push_config": {"push_endpoint": push_endpoint},
                        "ack_deadline_seconds": ack_deadline_seconds,
                    }
                )
            else:
                self._subscriber.create_subscription(
                    request={
                        "name": sub_path,
                        "topic": topic_path,
                        "ack_deadline_seconds": ack_deadline_seconds,
                    }
                )
        return sub_path

    def ensure_gmail_push_binding(self, topic_path: str) -> None:
        """
        Adiciona o publisher do Gmail Watch no tópico (roles/pubsub.publisher).
        Necessário p/ `users.watch` do Gmail.
        """
        policy = self._publisher.get_iam_policy(request={"resource": topic_path})
        has_binding = any(
            b.role == "roles/pubsub.publisher" and GMAIL_PUSH_PUBLISHER in b.members
            for b in policy.bindings
        )
        if not has_binding:
            policy.bindings.append(
                policy_pb2.Binding(
                    role="roles/pubsub.publisher",
                    members=[GMAIL_PUSH_PUBLISHER],
                )
            )
            self._publisher.set_iam_policy(request={"resource": topic_path, "policy": policy})

    def publish_json(self, topic_path_or_name: str, project_id: Optional[str], payload: Dict[str, Any], *, attrs: Optional[Dict[str, str]] = None) -> str:
        """
        Publica JSON (utf-8) no tópico.
        """
        topic_path = topic_path_or_name
        if not topic_path.startswith("projects/"):
            if not project_id:
                raise ValueError("project_id é obrigatório quando topic não é full path.")
            topic_path = self._publisher.topic_path(project_id, topic_path_or_name)

        data = json.dumps(payload).encode("utf-8")
        future = self._publisher.publish(topic_path, data=data, **(attrs or {}))
        return future.result()

    def pull(
        self,
        subscription_path_or_name: str,
        project_id: Optional[str],
        *,
        max_messages: int = 10,
        return_immediately: bool = False,
    ) -> List[Tuple[str, bytes, Dict[str, str]]]:
        """
        Faz pull de mensagens. Retorna lista de tuplas (ack_id, data, attributes).
        """
        sub_path = subscription_path_or_name
        if not sub_path.startswith("projects/"):
            if not project_id:
                raise ValueError("project_id é obrigatório quando subscription não é full path.")
            sub_path = self._subscriber.subscription_path(project_id, subscription_path_or_name)

        resp = self._subscriber.pull(
            request={
                "subscription": sub_path,
                "max_messages": max_messages,
                "return_immediately": return_immediately,
            }
        )
        out: List[Tuple[str, bytes, Dict[str, str]]] = []
        for rm in resp.received_messages or []:
            ack_id = rm.ack_id
            data = rm.message.data or b""
            attrs = dict(rm.message.attributes)
            out.append((ack_id, data, attrs))
        return out

    def ack(self, subscription_path: str, ack_ids: List[str]) -> None:
        if ack_ids:
            self._subscriber.acknowledge(request={"subscription": subscription_path, "ack_ids": ack_ids})

    @staticmethod
    def decode_push_envelope(envelope: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Decodifica o push do Pub/Sub (Gmail Watch manda {"emailAddress","historyId"} em data b64url).
        """
        if not envelope:
            return None
        msg = envelope.get("message") or {}
        data_b64 = msg.get("data")
        if not data_b64:
            return None
        try:
            decoded = base64.urlsafe_b64decode(data_b64.encode("utf-8")).decode("utf-8")
            return json.loads(decoded)
        except Exception:
            return None


if __name__ == "__main__":
    None
    # auth = GoogleServicesAuth(
    #     credentials_json=credentials_json_installed,
    #     token_json=token_json,
    # )
    # pubsub = PubSubService(auth)

    # topic_path = pubsub.ensure_topic("meu-projeto", "gmail-watch")
    # pubsub.ensure_gmail_push_binding(topic_path)
    # sub_path = pubsub.ensure_subscription("meu-projeto", "gmail-watch-sub", topic_path, push_endpoint=None)

    # # publicar algo
    # pubsub.publish_json(topic_path, project_id=None, payload={"hello": "world"})