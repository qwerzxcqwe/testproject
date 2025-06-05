from pydantic import BaseModel
from typing import List
from models.migration import CloudType, MigrationState


class CredentialsSchema(BaseModel):
    username: str
    password: str
    domain: str

class MountPointSchema(BaseModel):
    name: str
    total_size: int

class WorkloadSchema(BaseModel):
    ip: str
    credentials: CredentialsSchema
    storage: List[MountPointSchema]

class WorkloadUpdateSchema(BaseModel):
    credentials: CredentialsSchema
    storage: List[MountPointSchema]

class MigrationTargetSchema(BaseModel):
    cloud_type: CloudType
    cloud_credentials: CredentialsSchema
    target_vm: WorkloadSchema

class MigrationSchema(BaseModel):
    selected_mount_points: List[str]
    source_ip: str
    target: MigrationTargetSchema

class MigrationStatusSchema(BaseModel):
    source_ip: str
    state: MigrationState