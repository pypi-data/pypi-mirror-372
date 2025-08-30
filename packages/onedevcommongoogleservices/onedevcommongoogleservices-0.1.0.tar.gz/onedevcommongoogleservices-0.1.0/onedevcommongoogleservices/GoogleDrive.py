from __future__ import annotations
from typing import Any, Dict, List, Optional
import os
from googleapiclient.discovery import Resource
from googleapiclient.http import MediaIoBaseUpload, MediaFileUpload

from onedevcommongoogleservices.GoogleServicesAuth import GoogleServicesAuth


class GoogleDriveService:
    """
    Google Drive usando a MESMA credencial do GoogleServicesAuth.
    """
    def __init__(self, auth: "GoogleServicesAuth"):
        self._svc: Resource = auth.drive()

    def upload_or_replace_file(
        self,
        file_name: str,
        mime_type: str,
        *,
        file_stream=None,
        file_path: Optional[str] = None,
        folder_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Se existir arquivo com mesmo nome (e mesmo parent, se informado), atualiza; senão cria.
        Retorna {id: "..."} do arquivo final.
        """
        query = f"name='{file_name}' and trashed=false"
        if folder_id:
            query += f" and '{folder_id}' in parents"

        results = self._svc.files().list(
            q=query,
            fields="files(id)",
            includeItemsFromAllDrives=True,
            supportsAllDrives=True,
        ).execute()
        files = results.get("files", [])

        file_id = files[-1]["id"] if files else None
        metadata = {"name": file_name}

        media = MediaIoBaseUpload(file_stream, mimetype=mime_type, resumable=True) if file_stream \
            else MediaFileUpload(file_path, mimetype=mime_type, resumable=True)

        if file_id:
            return self._svc.files().update(
                fileId=file_id,
                body=metadata,
                media_body=media,
                fields="id",
                supportsAllDrives=True,
            ).execute()
        else:
            if folder_id:
                metadata["parents"] = [folder_id]
            return self._svc.files().create(
                body=metadata,
                media_body=media,
                fields="id",
                supportsAllDrives=True,
            ).execute()

    def upload_file_to_folder(self, file_path: str, file_name: str, folder_id: str) -> str:
        media = MediaFileUpload(file_path, resumable=True)
        file_metadata = {"name": file_name, "parents": [folder_id]}
        res = self._svc.files().create(
            body=file_metadata,
            media_body=media,
            fields="id",
            supportsAllDrives=True
        ).execute()
        return res["id"]

    def find_folder_id_by_name(self, folder_name: str, parent_folder_id: str) -> Optional[str]:
        query = f"'{parent_folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
        result = self._svc.files().list(
            q=query,
            includeItemsFromAllDrives=True,
            supportsAllDrives=True,
            pageSize=100,
            fields="files(id, name)"
        ).execute()
        for item in result.get("files", []):
            if item["name"] == folder_name:
                return item["id"]
        return None

    def find_file_id_by_name(self, file_name: str, parent_folder_id: str) -> Optional[str]:
        query = f"'{parent_folder_id}' in parents and name='{file_name}' and trashed=false"
        result = self._svc.files().list(
            q=query,
            includeItemsFromAllDrives=True,
            supportsAllDrives=True,
            pageSize=100,
            fields="files(id, name, mimeType)"
        ).execute()
        for item in result.get("files", []):
            if item["name"] == file_name and item.get("mimeType") != "application/vnd.google-apps.folder":
                return item["id"]
        return None

    def find_or_create_folder(self, folder_name: str, parent_id: str) -> str:
        q = (
            "mimeType='application/vnd.google-apps.folder' "
            f"and name='{folder_name}' and '{parent_id}' in parents and trashed=false"
        )
        result = self._svc.files().list(
            q=q, fields="files(id, name)", supportsAllDrives=True, includeItemsFromAllDrives=True
        ).execute()
        folders = result.get("files", [])
        if folders:
            return folders[0]["id"]

        body = {"name": folder_name, "mimeType": "application/vnd.google-apps.folder", "parents": [parent_id]}
        res = self._svc.files().create(body=body, fields="id", supportsAllDrives=True).execute()
        return res["id"]

    def get_files_by_folder(self, folder_id: str) -> List[Dict[str, Any]]:
        query = f"'{folder_id}' in parents and trashed=false"
        res = self._svc.files().list(
            q=query,
            includeItemsFromAllDrives=True,
            supportsAllDrives=True,
            pageSize=100,
            fields="nextPageToken, files(id, name, trashed, createdTime, modifiedTime)"
        ).execute()
        return res.get("files", [])

    def get_folder_details(self, folder_id: str) -> Dict[str, Any]:
        meta = self._svc.files().get(
            fileId=folder_id, fields="id, name, parents", supportsAllDrives=True
        ).execute()

        folder_name = meta.get("name")
        folder_path = folder_name
        parents = meta.get("parents", [])

        while parents:
            pid = parents[0]
            pmeta = self._svc.files().get(
                fileId=pid, fields="id, name, parents", supportsAllDrives=True
            ).execute()
            folder_path = f"{pmeta.get('name')} / {folder_path}"
            parents = pmeta.get("parents", [])

        files_q = f"'{folder_id}' in parents and mimeType!='application/vnd.google-apps.folder' and trashed=false"
        files_res = self._svc.files().list(
            q=files_q, supportsAllDrives=True, includeItemsFromAllDrives=True,
            fields="files(id, name, mimeType)", pageSize=1000
        ).execute()

        folders_q = f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
        folders_res = self._svc.files().list(
            q=folders_q, supportsAllDrives=True, includeItemsFromAllDrives=True,
            fields="files(id, name)", pageSize=1000
        ).execute()

        return {
            "folder_name": folder_name,
            "folder_path": folder_path,
            "files": files_res.get("files", []),
            "folders": folders_res.get("files", []),
        }

    def get_root_drives(self) -> List[Dict[str, Any]]:
        return self._svc.drives().list().execute().get("drives", [])

    def get_parent_folder_id(self, folder_id: str) -> Optional[str]:
        res = self._svc.files().get(
            fileId=folder_id, fields="parents", supportsAllDrives=True
        ).execute()
        parents = res.get("parents")
        return parents[0] if parents else None

    def file_exists(self, file_id: str) -> bool:
        try:
            self._svc.files().get(
                fileId=file_id, fields="id", supportsAllDrives=True
            ).execute()
            return True
        except Exception:
            return False

    def delete_file_by_id(self, file_id: str) -> bool:
        try:
            self._svc.files().delete(
                fileId=file_id, fields="id", supportsAllDrives=True
            ).execute()
            return True
        except Exception:
            return False

    def move_to_trash(self, file_id: str) -> bool:
        try:
            self._svc.files().update(
                fileId=file_id, body={"trashed": True}, supportsAllDrives=True
            ).execute()
            return True
        except Exception:
            return False


if __name__ == "__main__":
    None
    # auth = GoogleServicesAuth(
    #     credentials_json=credentials_json_installed,
    #     token_json=token_json,
    # )
    # drive = GoogleDriveService(auth)

    # folder_id = drive.find_or_create_folder("Relatorios", parent_id="root_folder_id")
    # up = drive.upload_or_replace_file(
    #     file_name="relatorio.pdf",
    #     mime_type="application/pdf",
    #     file_path="/tmp/relatorio.pdf",
    #     folder_id=folder_id,
    # )
    # print("File ID:", up["id"])
