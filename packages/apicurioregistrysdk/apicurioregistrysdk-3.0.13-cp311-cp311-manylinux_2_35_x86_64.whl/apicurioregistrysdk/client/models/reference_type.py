from enum import Enum

class ReferenceType(str, Enum):
    OUTBOUND = "OUTBOUND",
    INBOUND = "INBOUND",

