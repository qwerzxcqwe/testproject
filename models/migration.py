from dataclasses import dataclass
from typing import List
import time
from enum import Enum
from models.workload import Workload, Credentials


class CloudType(str, Enum):
    aws = "aws"
    azure = "azure"
    vsphere = "vsphere"
    vcloud = "vcloud"


class MigrationState(str, Enum):
    not_started = "not_started"
    running = "running"
    error = "error"
    success = "success"


@dataclass
class MigrationTarget:
    cloud_type: CloudType
    cloud_credentials: Credentials
    target_vm: Workload


@dataclass
class Migration:
    selected_mount_points: List[str]
    source: Workload
    target: MigrationTarget
    state: MigrationState = MigrationState.not_started

    def run(self):
        if "C:\\" not in self.selected_mount_points:
            raise PermissionError("Migration must include volume C:\\")

        self.state = MigrationState.running
        try:
            time.sleep(7.77) # fake delay
            self.target.target_vm.storage = self.source.clone_selected_mountpoints(self.selected_mount_points)
            self.state = MigrationState.success
        except Exception:
            self.state = MigrationState.error
            raise
