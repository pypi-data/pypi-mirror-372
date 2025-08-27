from dataclasses import dataclass, asdict

@dataclass
class Job():
    _class: str
    name: str
    url: str
    color: str
    fullName: str

    def to_dict(self):
        return asdict(self)
