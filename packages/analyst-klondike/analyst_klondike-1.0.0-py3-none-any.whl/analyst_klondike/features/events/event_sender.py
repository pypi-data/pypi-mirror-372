from abc import ABCMeta, abstractmethod
import httpx


class BaseEventSender(metaclass=ABCMeta):

    @abstractmethod
    async def send_event(self,
                         event_name: str,
                         event_location: str = "/",
                         *,
                         event_json: dict[str, str | int | bool] | None = None) -> None:
        pass

    async def get_user_ip(self) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                'https://checkip.amazonaws.com/', timeout=5000)
            response.raise_for_status()
            ip_address = response.text.strip()
            return ip_address
