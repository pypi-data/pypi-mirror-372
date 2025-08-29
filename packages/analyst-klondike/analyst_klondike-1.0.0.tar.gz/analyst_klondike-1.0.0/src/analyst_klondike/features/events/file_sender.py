from datetime import datetime
import csv
import json
import os
from analyst_klondike.features.events.event_sender import BaseEventSender


class FileEventSender(BaseEventSender):

    FieldNames = ['event_name',
                  'event_location',
                  'event_datetime',
                  'event_json',
                  'event_location_id',
                  'user_ip']

    def _create_empty_file(self, file_path: str):
        with open(file_path, mode='w', encoding='UTF-8') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(FileEventSender.FieldNames)

    async def send_event(self,
                         event_name: str,
                         event_location: str = "/",
                         *,
                         event_json: dict[str, str | int | bool] | str | None = None):
        try:
            await self._try_send_event(event_name,
                                       event_location,
                                       event_json=event_json)
        except Exception:  # pylint: disable=W0718
            print(f"Fail to send event {event_name}")

    async def _try_send_event(self,
                              event_name: str,
                              event_location: str = "/",
                              *,
                              event_json: dict[str, str | int | bool] | str | None = None):
        # await asyncio.sleep(4)

        user_ip = await self.get_user_ip()
        event_datetime = datetime.now()
        event_location_id = ''

        events_file_path = self._get_events_file_path()
        if not os.path.exists(events_file_path):
            self._create_empty_events_file(events_file_path)
        # add event info
        stringified_event_json = json.dumps(event_json)
        self._append_line(events_file_path, [
            event_name,
            event_location,
            str(event_datetime),
            stringified_event_json,
            event_location_id,
            user_ip
        ])

    def _create_empty_events_file(self, file_path: str):
        self._create_empty_file(file_path)

    def _append_line(self, file_path: str, line: list[str]) -> None:
        with open(file_path, mode='a', encoding='UTF-8') as f:
            writer = csv.writer(f)
            writer.writerow(line)

    def _get_events_file_path(self) -> str:
        this_file_dir = os.path.dirname(os.path.realpath(__file__))
        return os.path.join(this_file_dir, "events.csv")
