from enum import Enum

class VersionState(str, Enum):
    ENABLED = "ENABLED",
    DISABLED = "DISABLED",
    DEPRECATED = "DEPRECATED",
    DRAFT = "DRAFT",

