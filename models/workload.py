from dataclasses import dataclass, field
from typing import List

@dataclass
class Credentials:
    username: str
    password: str
    domain: str


@dataclass
class MountPoint:
    name: str  # e.g. C:\\
    total_size: int


@dataclass
class Workload:
    credentials: Credentials
    ip: str
    storage: List[MountPoint] = field(default_factory=list)

    def __post_init__(self):
        if not self.ip or not self.credentials.username or not self.credentials.password:
            raise ValueError("IP, username and password cannot be None")
        self._ip_locked = self.ip

    @property
    def ip(self):
        return self._ip_locked

    @ip.setter
    def ip(self, value):
        if hasattr(self, '_ip_locked') and self._ip_locked != value:
            raise ValueError("IP cannot be changed once set")
        self._ip_locked = value

    def clone_selected_mountpoints(self, selected: List[str]) -> List[MountPoint]:
        return [mp for mp in self.storage if mp.name in selected]
