from dataclasses import dataclass, asdict
from  typing import Optional

@dataclass
class User():
   username: str
   email: Optional[str]
   state: Optional[str]
   using_license_seat: Optional[bool]
   is_admin: bool = False

   def to_dict(self):
        return asdict(self)
