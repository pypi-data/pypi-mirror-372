from enum import Enum

class RuleType(str, Enum):
    VALIDITY = "VALIDITY",
    COMPATIBILITY = "COMPATIBILITY",
    INTEGRITY = "INTEGRITY",

