from dataclasses import dataclass

from buz.event.infrastructure.models.delivery_context import DeliveryContext


@dataclass(frozen=True)
class ExecutionContext:
    delivery_context: DeliveryContext
