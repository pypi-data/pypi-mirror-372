from typing import Optional, Iterable

from buz.event import Event, EventBus
from buz.event.transactional_outbox import OutboxRecord
from buz.event.transactional_outbox.event_to_outbox_record_translator import EventToOutboxRecordTranslator
from buz.event.transactional_outbox.outbox_record_validation.outbox_record_validator import OutboxRecordValidator
from buz.event.transactional_outbox.outbox_repository import OutboxRepository


class TransactionalOutboxEventBus(EventBus):
    def __init__(
        self,
        outbox_repository: OutboxRepository,
        event_to_outbox_record_translator: EventToOutboxRecordTranslator,
        outbox_record_validator: Optional[OutboxRecordValidator] = None,
    ):
        self.__outbox_repository = outbox_repository
        self.__event_to_outbox_record_translator = event_to_outbox_record_translator
        self.__outbox_record_validator = outbox_record_validator

    def publish(self, event: Event) -> None:
        outbox_record = self.__translate_and_validate(event)
        self.__outbox_repository.save(outbox_record)

    def bulk_publish(self, events: Iterable[Event]) -> None:
        outbox_records = map(self.__translate_and_validate, events)
        self.__outbox_repository.bulk_create(outbox_records)

    # Raises OutboxRecordValidationException: If any validation inside outbox_record_validator fails
    def __translate_and_validate(self, event: Event) -> OutboxRecord:
        outbox_record = self.__event_to_outbox_record_translator.translate(event)
        if self.__outbox_record_validator is not None:
            self.__outbox_record_validator.validate(record=outbox_record)
        return outbox_record
