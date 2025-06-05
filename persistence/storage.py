import os
import json
from typing import List
from models.workload import Workload, MountPoint, Credentials
from models.migration import Migration, MigrationTarget, CloudType, MigrationState

DATA_DIR = "data"
WORKLOADS_FILE = os.path.join(DATA_DIR, "workloads.json")
MIGRATIONS_FILE = os.path.join(DATA_DIR, "migrations.json")


def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def _serialize(obj):
    if isinstance(obj, Workload):
        return {
            "ip": obj.ip,
            "credentials": vars(obj.credentials),
            "storage": [vars(m) for m in obj.storage],
        }
    elif isinstance(obj, MigrationTarget):
        return {
            "cloud_type": obj.cloud_type,
            "cloud_credentials": vars(obj.cloud_credentials),
            "target_vm": _serialize(obj.target_vm)
        }
    elif isinstance(obj, Migration):
        return {
            "selected_mount_points": obj.selected_mount_points,
            "source": obj.source.ip,
            "target": _serialize(obj.target),
            "state": obj.state,
        }
    return obj


def _deserialize_workload(data) -> Workload:
    creds = Credentials(**data["credentials"])
    mounts = [MountPoint(**m) for m in data["storage"]]
    return Workload(ip=data["ip"], credentials=creds, storage=mounts)


def save_workload(workload: Workload):
    _ensure_data_dir()
    workloads = load_all_workloads()
    if any(w.ip == workload.ip for w in workloads):
        raise ValueError("Duplicate IP not allowed")

    workloads.append(workload)
    with open(WORKLOADS_FILE, "w") as f:
        json.dump([_serialize(w) for w in workloads], f, indent=2)


def load_all_workloads() -> List[Workload]:
    if not os.path.exists(WORKLOADS_FILE):
        return []
    with open(WORKLOADS_FILE) as f:
        raw = json.load(f)
    return [_deserialize_workload(w) for w in raw]


def save_all_workloads(workloads: List[Workload]):
    _ensure_data_dir()
    with open(WORKLOADS_FILE, "w") as f:
        json.dump([_serialize(w) for w in workloads], f, indent=2)


def update_workload(index: int, new_workload: Workload):
    workloads = load_all_workloads()
    if index < 0 or index >= len(workloads):
        raise ValueError("Workload index out of range")

    workloads[index] = new_workload
    save_all_workloads(workloads)


def delete_workload(ip: str):
    workloads = load_all_workloads()
    workloads = [w for w in workloads if w.ip != ip]
    with open(WORKLOADS_FILE, "w") as f:
        json.dump([_serialize(w) for w in workloads], f, indent=2)


def save_migration(migration: Migration):
    _ensure_data_dir()
    migrations = load_all_migrations()
    migrations.append(migration)
    with open(MIGRATIONS_FILE, "w") as f:
        json.dump([_serialize(m) for m in migrations], f, indent=2)


def load_all_migrations() -> List[Migration]:
    if not os.path.exists(MIGRATIONS_FILE):
        return []

    with open(MIGRATIONS_FILE) as f:
        raw = json.load(f)

    workloads = {w.ip: w for w in load_all_workloads()}
    migrations = []

    for m in raw:
        source_ip = m["source"]
        source = workloads.get(source_ip)
        if not source:
            continue
        target_vm = _deserialize_workload(m["target"]["target_vm"])
        target = MigrationTarget(
            cloud_type=CloudType(m["target"]["cloud_type"]),
            cloud_credentials=Credentials(**m["target"]["cloud_credentials"]),
            target_vm=target_vm
        )
        migrations.append(Migration(
            selected_mount_points=m["selected_mount_points"],
            source=source,
            target=target,
            state=MigrationState(m["state"])
        ))
    return migrations

def update_migration(source_ip: str, migration: Migration):
    _ensure_data_dir()
    migrations = load_all_migrations()
    for i, m in enumerate(migrations):
        if m.source.ip == source_ip:
            migrations[i] = migration
            break
    else:
        raise ValueError("Migration not found for update")

    with open(MIGRATIONS_FILE, "w") as f:
        json.dump([_serialize(m) for m in migrations], f, indent=2)


def delete_migration(index: int):
    _ensure_data_dir()
    migrations = load_all_migrations()
    if index < 0 or index >= len(migrations):
        raise ValueError("Invalid migration index")
    del migrations[index]
    with open(MIGRATIONS_FILE, "w") as f:
        json.dump([_serialize(m) for m in migrations], f, indent=2)


