from enum import Enum

class UserInterfaceConfigAuth_type(str, Enum):
    None_ = "none",
    Basic = "basic",
    Oidc = "oidc",

