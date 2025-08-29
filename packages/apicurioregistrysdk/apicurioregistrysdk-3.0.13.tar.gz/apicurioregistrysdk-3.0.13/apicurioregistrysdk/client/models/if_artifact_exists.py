from enum import Enum

class IfArtifactExists(str, Enum):
    FAIL = "FAIL",
    CREATE_VERSION = "CREATE_VERSION",
    FIND_OR_CREATE_VERSION = "FIND_OR_CREATE_VERSION",

