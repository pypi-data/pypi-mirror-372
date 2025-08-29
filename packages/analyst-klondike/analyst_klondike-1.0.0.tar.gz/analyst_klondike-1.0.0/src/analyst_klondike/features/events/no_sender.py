from analyst_klondike.features.events.event_sender import BaseEventSender


class NoEventSender(BaseEventSender):

    async def send_event(self,
                         event_name: str,
                         event_location: str = "/",
                         *,
                         event_json: dict[str, str | int | bool] | str | None = None):
        pass
