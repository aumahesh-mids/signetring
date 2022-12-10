from enum import auto, Enum


class UserType(str, Enum):
    Creator = "creator"
    Publisher = "publisher"


class SourceAppType(str, Enum):
    WordProcessor = "word-processor"
    Camera = "camera"


class DigitalObjectType(str, Enum):
    Document = "doc"
    Photo = "pic"
    Video = "vid"


class StatsType(str, Enum):
    Creations = "creations"
    Edits = "edits"
    Publications = "publications"
    Verifications = "verifications"
