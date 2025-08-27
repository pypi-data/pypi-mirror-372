from dataclasses import dataclass
from typing import Optional

@dataclass
class JenkinsPlugin:
    shortName: str
    longName: str
    hasUpdate: Optional[bool] = None
    enabled: Optional[bool] = None
    detached: Optional[bool] = None
    downgradable: Optional[bool] = None
    url: Optional[str] = ""
    version: Optional[str] = ""
    
    
    def __post_init__(self):
        self.version = str(self.version)
