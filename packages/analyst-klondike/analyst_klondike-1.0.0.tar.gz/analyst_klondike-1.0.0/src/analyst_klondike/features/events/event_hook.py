import asyncio
from typing import Any, Literal
from analyst_klondike.features.events.api_sender import ApiEventSender
from analyst_klondike.features.events.event_sender import BaseEventSender
from analyst_klondike.features.events.file_sender import FileEventSender
from analyst_klondike.features.events.no_sender import NoEventSender
from analyst_klondike.state.app_state import select

from analyst_klondike.state.app_state import AppState


EventSenderType = Literal["local_file", "local_db", "remote_db", "no_events"]


def create_event_sender(sender_type: EventSenderType) -> BaseEventSender:
    if sender_type == "local_file":
        return FileEventSender()
    if sender_type == "local_db":
        return ApiEventSender(
            api_url="https://localhost:7150/api/NeonApi/PostEvent")
    if sender_type == "remote_db":
        return ApiEventSender(
            api_url="https://www.xn----7sbbaat6aaehdfdhwgj7f.xn--p1ai/api/NeonApi/PostEvent")
    if sender_type == "no_events":
        return NoEventSender()
    raise ValueError(f"Event sender <{sender_type}> supported")


def send_event(event_name: str,
               event_location: str,
               event_json: dict[str, str | int | bool] | None = None,
               async_run: bool = True) -> None:
    # pylint: disable=import-outside-toplevel
    from analyst_klondike.ui.runner_app import get_app

    async def _send_async(event_name: str,
                          event_location: str) -> None:
        # await asyncio.sleep(10)
        event_sender = _use_event_sender()
        await event_sender.send_event(event_name=event_name,
                                      event_location=event_location,
                                      event_json=event_json)

    app = get_app()
    if async_run:
        app.run_worker(_send_async(event_name, event_location), thread=True)
    else:
        asyncio.create_task(_send_async(event_name, event_location))


def event(event_name: str,
          event_location: str,
          event_start_prefix: str | None = None,
          event_end_prefix: str | None = None) -> Any:

    def actual_decorator(func: Any):

        def wrapper(*args: Any, **kwargs: Any):
            if event_start_prefix is not None and event_end_prefix is not None:
                send_event(event_name + "_start", event_location)
                func(*args, **kwargs)
                send_event(event_name + "_end", event_location)

            if event_end_prefix is None and event_start_prefix is None:
                func(*args, **kwargs)
                send_event(event_name, event_location)
        return wrapper

    return actual_decorator


def _use_event_sender() -> BaseEventSender:
    sender_type = select(_select_senver)
    return create_event_sender(sender_type)


def _select_senver(state: AppState) -> str:
    return state.event_sender
