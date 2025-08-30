# Google Services

Biblioteca Python para integração **genérica** com os principais serviços do Google:
📧 **Gmail**, 📂 **Google Drive**, 📅 **Google Calendar** e 🔔 **Google Pub/Sub**.

O diferencial é a autenticação unificada: você instancia **uma vez** a classe `GoogleServicesAuth` (suportando OAuth ou Service Account), e então acessa os serviços sem precisar reautenticar.

---

## 🚀 Pré-requisitos

* Python **3.9+** (testado até 3.13)
* Conta Google com APIs habilitadas no [Google Cloud Console](https://console.cloud.google.com/)
* Credenciais no formato **OAuth Installed** ou **Service Account**
* (Opcional) [Poetry](https://python-poetry.org/) para gerenciamento de dependências

---

## 📦 Instalação

Via **pip**:

```bash
pip install onedevcommongoogleservices
```

Via **Poetry**:

```bash
poetry add onedevcommongoogleservices
```

---

## 🔑 Autenticação

A classe `GoogleServicesAuth` aceita dois modos:

### 1. OAuth (Installed App)

```python
from onedevcommongoogleservices import GoogleServicesAuth

credentials_json = {
    "installed": {
        "client_id": "seu_client_id",
        "project_id": "projeto_id",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_secret": "seu_client_secret",
        "redirect_uris": ["http://localhost"]
    }
}

auth = GoogleServicesAuth(
    credentials_json=credentials_json,
    allow_interactive=True  # abre o navegador na primeira vez
)
```

Depois da primeira autenticação, você pode salvar o `token_json`:

```python
token_json = auth.creds.to_json()
```

E nas próximas vezes:

```python
auth = GoogleServicesAuth(credentials_json, token_json=json.loads(token_json))
```

---

### 2. Service Account (com delegação opcional)

```python
from onedevcommongoogleservices import GoogleServicesAuth

auth = GoogleServicesAuth(
    credentials_json=service_account_json,
    delegated_user="usuario@empresa.com"  # se usar Domain-Wide Delegation
)
```

---

## 📚 Exemplos de Uso

### 📧 Gmail

```python
from onedevcommongoogleservices.gmail_service import GmailService

gmail = GmailService(auth)

# Listar últimos 10 e-mails
msgs = gmail.list_messages(limit=10)
print([m["id"] for m in msgs])

# Enviar e-mail
gmail.send_email(
    from_addr="meuemail@gmail.com",
    to="destinatario@empresa.com",
    subject="Teste",
    html_body="<h1>Olá</h1>",
    attachments=["/tmp/relatorio.pdf"]
)
```

---

### 📂 Google Drive

```python
from onedevcommongoogleservices.drive_service import DriveService

drive = DriveService(auth)

# Criar ou substituir arquivo
drive.upload_or_replace_file(
    file_name="relatorio.pdf",
    mime_type="application/pdf",
    file_path="/tmp/relatorio.pdf",
    folder_id="id_da_pasta"
)

# Listar arquivos de uma pasta
files = drive.get_files_by_folder("id_da_pasta")
print(files)
```

---

### 📅 Google Calendar

```python
from datetime import datetime, timedelta
from onedevcommongoogleservices.calendar_service import CalendarService

calendar = CalendarService(auth)

start = datetime.now() + timedelta(hours=1)
end = start + timedelta(hours=2)

event = calendar.create_event(
    summary="Reunião de Alinhamento",
    start=start,
    end=end,
    attendees=["joao@empresa.com"],
    conference_meet=True
)

print("Evento criado:", event["id"], event.get("hangoutLink"))
```

---

### 🔔 Pub/Sub

```python
from onedevcommongoogleservices.pubsub_service import PubSubService

pubsub = PubSubService(auth)

# Criar tópico e subscription
topic_path = pubsub.ensure_topic("meu-projeto", "topico-teste")
sub_path = pubsub.ensure_subscription("meu-projeto", "sub-teste", topic_path)

# Publicar
pubsub.publish_json(topic_path, project_id=None, payload={"msg": "olá"})

# Consumir
msgs = pubsub.pull(sub_path, project_id=None, max_messages=5)
for ack_id, data, attrs in msgs:
    print("Mensagem:", data.decode())
    pubsub.ack(sub_path, [ack_id])
```

---

## ⚡ Funcionalidades

* ✅ **Autenticação unificada** (OAuth Installed ou Service Account)
* ✅ **Token reutilizável** (`token_json`)
* ✅ Serviços prontos:

  * **Gmail** → listar, enviar e-mails, anexos
  * **Drive** → upload, busca, exclusão
  * **Calendar** → criar/listar eventos (com Google Meet)
  * **Pub/Sub** → tópicos, subscriptions, publish/pull
* ✅ Suporte a **Domain-Wide Delegation** para Service Accounts
* ✅ Compatível com **Poetry** e **pip**

---

## 📝 Licença

Este projeto está sob a licença [MIT](LICENSE).
