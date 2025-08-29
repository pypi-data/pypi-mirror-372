from enum import Enum

class RoleType(str, Enum):
    READ_ONLY = "READ_ONLY",
    DEVELOPER = "DEVELOPER",
    ADMIN = "ADMIN",

