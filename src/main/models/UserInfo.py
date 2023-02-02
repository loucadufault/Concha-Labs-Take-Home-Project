from dataclasses import dataclass
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class UserInfo:
    """Model representing all input basic information of a user account."""
    name: str
    email: str
    address: str
