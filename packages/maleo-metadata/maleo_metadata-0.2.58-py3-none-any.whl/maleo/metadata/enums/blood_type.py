from enum import StrEnum


class DetailLevel(StrEnum):
    BASIC = "basic"
    STANDARD = "standard"
    FULL = "full"


class IdentifierType(StrEnum):
    ID = "id"
    UUID = "uuid"
    KEY = "key"
    NAME = "name"


class BloodType(StrEnum):
    A = "a"
    B = "b"
    AB = "ab"
    O = "o"  # noqa: E741
