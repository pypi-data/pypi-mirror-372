from __future__ import annotations

from datetime import datetime
from typing import TypeVar, Type, Generic

import orjson
from dacite import from_dict

from buz.event import Event
from buz.kafka.infrastructure.cdc.cdc_message import CDCPayload
from buz.kafka.infrastructure.deserializers.bytes_to_message_deserializer import BytesToMessageDeserializer
from buz.kafka.infrastructure.deserializers.implementations.cdc.not_valid_cdc_message_exception import (
    NotValidCDCMessageException,
)

T = TypeVar("T", bound=Event)


class CDCRecordBytesToEventDeserializer(BytesToMessageDeserializer[Event], Generic[T]):
    __STRING_ENCODING = "utf-8"

    def __init__(self, event_class: Type[T]) -> None:
        self.__event_class = event_class

    def deserialize(self, data: bytes) -> T:
        decoded_string = data.decode(self.__STRING_ENCODING)
        try:
            cdc_payload = self.__get_outbox_record_as_dict(decoded_string)
            return self.__event_class.restore(
                id=cdc_payload.event_id,
                created_at=self.__get_created_at_in_event_format(cdc_payload.created_at),
                **orjson.loads(cdc_payload.payload),
            )
        except Exception as exception:
            raise NotValidCDCMessageException(decoded_string, exception) from exception

    def __get_created_at_in_event_format(self, cdc_payload_created_at: str) -> str:
        created_at_datetime = datetime.strptime(cdc_payload_created_at, CDCPayload.DATE_TIME_FORMAT)
        return created_at_datetime.strftime(Event.DATE_TIME_FORMAT)

    def __get_outbox_record_as_dict(self, decoded_string: str) -> CDCPayload:
        decoded_record: dict = orjson.loads(decoded_string)

        payload = decoded_record.get("payload")

        if not isinstance(payload, dict):
            raise ValueError("The provided payload value is not valid")

        return from_dict(CDCPayload, payload)
