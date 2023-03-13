from dataclasses import dataclass


class FrozenDataClass(type):
    def __new__(cls, *args):
        new_cls = super().__new__(cls, *args)
        return dataclass(frozen=True)(new_cls)

class ImmutableObject(metaclass=FrozenDataClass):
    pass

class DomainEvent(ImmutableObject):
    originator_id: int
    originator_version: int
    timestamp: int
