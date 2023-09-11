from datetime import datetime
import importlib
from typing import List, Optional, Type
from uuid import UUID, uuid4
from yaerp.model.domain_event import DomainEvent


class Aggregate:

    class Event(DomainEvent):

        def mutate(self, aggregate: Optional['Aggregate']) -> Optional['Aggregate']:
            next_originator_version = self.version + 1
            if self.originator_version != next_originator_version:
                raise aggregate.VersionError(self.originator_version, next_originator_version)
            aggregate.version = next_originator_version
            aggregate.modified_on = self.timestamp
            self.apply(aggregate)
            return aggregate
        
        def apply(self, aggregate: 'Aggregate'):
            pass

    class VersionError(Exception):
        pass

    def __init__(self, id: UUID, version: int, timestamp:  int):
        self.id = id
        self.version = version
        self.created_on = timestamp
        self.modified_on = timestamp
        self.pending_events: List[Aggregate.Event] = []

    def _create_(cls, event_class: Type['Aggregate.Created'], **kwargs,):
        event = event_class(
            originator_id = uuid4(),
            originator_version = 1,
            originator_topic = get_topic(cls),
            timestamp = datetime.now(),
            **kwargs,
            )
        aggregate = event.mutate(None)
        aggregate.pending_events.append(event)
        return aggregate
    
    class Created(Event):
        originator_topic: str

        def mutate(self, aggregate: Optional['Aggregate']) -> Optional['Aggregate']:
            kwargs = self.__dict__.copy()
            id = kwargs.pop('originator_id')
            version = kwargs.pop('originator_version')
            aggregate_class = resolve_topic(
                kwargs.pop('originator_topic')
            )
            return aggregate_class(id=id, version=version, **kwargs)

        def _trigger_(self, event_class: Type['Aggregate.Event'], **kwargs,) -> None:
            next_version = self.version + 1
            try:
                event = event_class(
                    originator_id = self.id,
                    originator_version = next_version,
                    timestamp = datetime.now(),
                    **kwargs,
                )
            except AttributeError:
                raise
            event.mutate(self)
            self.pending_events.append(event)

        def _collect_(self) -> List['Aggregate.Event']:
            collected = []
            while self.pending_events:
                collected.append(self.pending_events.pop(0))
            return collected

def get_topic(cls: type) -> str:
    return f"{cls.__module__}#{cls.__qualname__}"

def resolve_attr(obj, path: str) -> type:
    if not path:
        return obj
    else:
        head, _, tail = path.partition(".")
        obj = getattr(obj, head)
        return resolve_attr(obj, tail)

def resolve_topic(topic: str) -> type:
    module_name, _, class_name = topic.partition("#")
    module = importlib.import_module(module_name)
    return resolve_attr(module, class_name)
        
