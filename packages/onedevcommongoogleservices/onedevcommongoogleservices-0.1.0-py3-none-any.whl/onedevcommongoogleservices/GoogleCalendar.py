from __future__ import annotations
from typing import Any, Dict, List, Optional, Iterable
from uuid import uuid4
from datetime import datetime
import pytz

from onedevcommongoogleservices.GoogleServicesAuth import GoogleServicesAuth  # se não quiser, remova e só aceite datetimes já tz-aware


class CalendarService:
    """
    Google Calendar usando a MESMA credencial do GoogleServicesAuth.
    Ex.: cal = CalendarService(auth)  # calendar_id='primary'
    """

    def __init__(self, auth: "GoogleServicesAuth", calendar_id: str = "primary"):
        self._svc = auth.calendar()
        self._calendar_id = calendar_id

    @staticmethod
    def _to_rfc3339(dt: datetime | str, default_tz: str = "America/Sao_Paulo") -> Dict[str, str]:
        """
        Converte datetime (aware/naive) ou string RFC3339 em dict aceito pela API:
        { "dateTime": "...", "timeZone": "..." }
        - Se string, assume já no formato RFC3339.
        - Se naive, aplica default_tz.
        """
        if isinstance(dt, str):
            # string RFC3339 (ex.: "2025-08-29T14:00:00-03:00")
            return {"dateTime": dt}

        if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
            tz = pytz.timezone(default_tz)
            dt = tz.localize(dt)

        return {"dateTime": dt.isoformat(), "timeZone": str(dt.tzinfo)}

    def list_events(
        self,
        *,
        time_min: datetime | str,
        time_max: datetime | str,
        q: Optional[str] = None,
        max_results: int = 2500,
        single_events: bool = True,
        order_by: str = "startTime",
        page_size: int = 250,
    ) -> List[Dict[str, Any]]:
        """
        Lista eventos em um intervalo de tempo.
        """
        events: List[Dict[str, Any]] = []
        page_token: Optional[str] = None

        # API espera strings RFC3339
        tmin = time_min if isinstance(time_min, str) else self._to_rfc3339(time_min)["dateTime"]
        tmax = time_max if isinstance(time_max, str) else self._to_rfc3339(time_max)["dateTime"]

        while True:
            resp = self._svc.events().list(
                calendarId=self._calendar_id,
                timeMin=tmin,
                timeMax=tmax,
                q=q,
                maxResults=min(page_size, max_results - len(events)) if max_results else page_size,
                singleEvents=single_events,
                orderBy=order_by,
                pageToken=page_token,
            ).execute()

            items = resp.get("items", [])
            events.extend(items)

            if max_results and len(events) >= max_results:
                return events[:max_results]

            page_token = resp.get("nextPageToken")
            if not page_token:
                break

        return events

    def get_event(self, event_id: str) -> Dict[str, Any]:
        return self._svc.events().get(calendarId=self._calendar_id, eventId=event_id).execute()

    def create_event(
        self,
        *,
        summary: str,
        start: datetime | str,
        end: datetime | str,
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[Iterable[str]] = None,
        reminders_override: Optional[List[Dict[str, Any]]] = None,
        color_id: Optional[str] = None,
        recurrence: Optional[Iterable[str]] = None,  # ex.: ["RRULE:FREQ=WEEKLY;COUNT=10"]
        conference_meet: bool = False,              # cria link do Google Meet
        send_updates: str = "all",                  # "all" | "externalOnly" | "none"
        default_tz: str = "America/Sao_Paulo",
    ) -> Dict[str, Any]:
        body: Dict[str, Any] = {
            "summary": summary,
            "start": self._to_rfc3339(start, default_tz),
            "end": self._to_rfc3339(end, default_tz),
        }
        if description:
            body["description"] = description
        if location:
            body["location"] = location
        if attendees:
            body["attendees"] = [{"email": a} for a in attendees]
        if color_id:
            body["colorId"] = color_id
        if recurrence:
            body["recurrence"] = list(recurrence)
        if reminders_override is not None:
            body["reminders"] = {"useDefault": False, "overrides": reminders_override}

        kwargs: Dict[str, Any] = {}
        if conference_meet:
            # precisa conferenceDataVersion=1 + createRequest
            body["conferenceData"] = {
                "createRequest": {"requestId": f"meet-{uuid4()}"}
            }
            kwargs["conferenceDataVersion"] = 1

        return self._svc.events().insert(
            calendarId=self._calendar_id,
            body=body,
            sendUpdates=send_updates,
            **kwargs,
        ).execute()

    def update_event(
        self,
        event_id: str,
        *,
        body_updates: Dict[str, Any],
        send_updates: str = "all",
        conference_meet: bool = False,
    ) -> Dict[str, Any]:
        """
        Update completo (substitui campos). Se quer alterar poucos campos, use patch_event().
        """
        kwargs: Dict[str, Any] = {}
        if conference_meet and "conferenceData" not in body_updates:
            body_updates["conferenceData"] = {"createRequest": {"requestId": f"meet-{uuid4()}"}}
            kwargs["conferenceDataVersion"] = 1

        # Pega o evento atual pra evitar apagar campos essenciais sem querer
        current = self.get_event(event_id)
        current.update(body_updates)

        return self._svc.events().update(
            calendarId=self._calendar_id,
            eventId=event_id,
            body=current,
            sendUpdates=send_updates,
            **kwargs,
        ).execute()

    def patch_event(
        self,
        event_id: str,
        *,
        body_patch: Dict[str, Any],
        send_updates: str = "all",
        conference_meet: bool = False,
    ) -> Dict[str, Any]:
        """
        Patch (parcial) — só os campos do dict.
        """
        kwargs: Dict[str, Any] = {}
        if conference_meet and "conferenceData" not in body_patch:
            body_patch["conferenceData"] = {"createRequest": {"requestId": f"meet-{uuid4()}"}}
            kwargs["conferenceDataVersion"] = 1

        return self._svc.events().patch(
            calendarId=self._calendar_id,
            eventId=event_id,
            body=body_patch,
            sendUpdates=send_updates,
            **kwargs,
        ).execute()

    def delete_event(self, event_id: str, send_updates: str = "all") -> None:
        self._svc.events().delete(
            calendarId=self._calendar_id,
            eventId=event_id,
            sendUpdates=send_updates
        ).execute()

    def quick_add(self, text: str, send_updates: str = "all") -> Dict[str, Any]:
        """
        Interpreta texto natural (ex.: "Reunião amanhã 10h com João").
        """
        return self._svc.events().quickAdd(
            calendarId=self._calendar_id,
            text=text,
            sendUpdates=send_updates
        ).execute()

    def add_attendees(self, event_id: str, emails: Iterable[str], send_updates: str = "all") -> Dict[str, Any]:
        ev = self.get_event(event_id)
        current = [a.get("email") for a in ev.get("attendees", []) or []]
        merged = list({*current, *emails})
        return self.patch_event(event_id, body_patch={"attendees": [{"email": e} for e in merged]}, send_updates=send_updates)

    def set_reminders_default(self, event_id: str, use_default: bool = True, overrides: Optional[List[Dict[str, Any]]] = None, send_updates: str = "all") -> Dict[str, Any]:
        body = {"reminders": {"useDefault": use_default}}
        if overrides is not None:
            body["reminders"] = {"useDefault": False, "overrides": overrides}
        return self.patch_event(event_id, body_patch=body, send_updates=send_updates)

    def list_calendars(self, max_results: int = 250) -> List[Dict[str, Any]]:
        """
        Lista calendários da conta (CalendarList).
        """
        out: List[Dict[str, Any]] = []
        page_token = None
        while True:
            resp = self._svc.calendarList().list(maxResults=max_results, pageToken=page_token).execute()
            out.extend(resp.get("items", []))
            page_token = resp.get("nextPageToken")
            if not page_token:
                break
        return out

    def find_calendar_by_summary(self, summary: str) -> Optional[Dict[str, Any]]:
        for c in self.list_calendars():
            if c.get("summary") == summary:
                return c
        return None

    def ensure_calendar(self, summary: str, time_zone: str = "America/Sao_Paulo") -> Dict[str, Any]:
        found = self.find_calendar_by_summary(summary)
        if found:
            return found
        return self._svc.calendars().insert(body={"summary": summary, "timeZone": time_zone}).execute()


if __name__ == "__main__":
    None
    # auth = GoogleServicesAuth(
    #     credentials_json=credentials_json_installed,
    #     token_json=token_json,
    # )

    # cal = CalendarService(auth)  # usa "primary"

    # # 1) Criar evento com Meet e 2 convidados
    # start = datetime(2025, 9, 1, 10, 0)   # tz será aplicado (America/Sao_Paulo) se naive
    # end   = datetime(2025, 9, 1, 11, 0)

    # ev = cal.create_event(
    #     summary="Kickoff Projeto X",
    #     start=start,
    #     end=end,
    #     description="Alinhamentos iniciais",
    #     attendees=["joao@empresa.com", "maria@empresa.com"],
    #     reminders_override=[{"method": "email", "minutes": 30}, {"method": "popup", "minutes": 10}],
    #     conference_meet=True,   # cria link do Meet
    # )
    # print("Event id:", ev["id"])
    # print("Meet link:", ev.get("hangoutLink"))

    # # 2) Listar eventos da semana
    # from datetime import timedelta
    # now = datetime.now()
    # events = cal.list_events(time_min=now, time_max=now + timedelta(days=7))
    # print(len(events), "eventos encontrados")

    # # 3) Adicionar convidados depois (patch)
    # cal.add_attendees(ev["id"], ["renan@empresa.com"])

    # 4) Deletar
    # cal.delete_event(ev["id"])
