from enum import Enum

class HandleReferencesType(str, Enum):
    PRESERVE = "PRESERVE",
    DEREFERENCE = "DEREFERENCE",
    REWRITE = "REWRITE",

