import json
from typing import Any
import httpx
from analyst_klondike.features.events.event_sender import BaseEventSender


class ApiEventSender(BaseEventSender):

    def __init__(self, api_url: str) -> None:
        super().__init__()
        self.api_url = api_url

    async def send_event(self,
                         event_name: str,
                         event_location: str = "/",
                         *,
                         event_json: dict[str, str | int | bool] | None = None) -> None:
        user_ip = await self.get_user_ip()
        data_dict: dict[str, str | Any] = {
            "userId": user_ip,
            "eventJson": {} if event_json is None else {
                'addData': self._dict_to_kvps(event_json)
            },
            "eventName": event_name,
            "eventLocation": event_location,
            "eventLocationId": "",
            "userIp": user_ip
        }

        stringified_data = json.dumps(data_dict, ensure_ascii=False)

        async with httpx.AsyncClient(verify=False) as client:
            response = await client.post(
                url=self.api_url,
                content=stringified_data,
                timeout=5000,
                headers={
                    'accept': 'application/json',
                    'content-type': 'application/json'
                }
            )
            response.raise_for_status()

    def _dict_to_kvps(self, d: dict[str, str | int | bool] | str | None) -> str:
        if d is None:
            return ""
        if isinstance(d, str):
            return d
        return ", ".join(f"{k}={v}" for k, v in d.items())
