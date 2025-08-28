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


class Gender(StrEnum):
    UNDISCLOSED = "undisclosed"
    FEMALE = "female"
    MALE = "male"
