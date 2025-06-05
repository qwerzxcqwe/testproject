import threading
from typing import List
from fastapi import HTTPException
from models.migration import MigrationTarget, Migration, MigrationState
from models.workload import Workload, Credentials, MountPoint
from persistence import storage
from ..models import MigrationStatusSchema, MigrationSchema
from .route import route
import logging

logger = logging.getLogger(__name__)

@route.get("/", response_model=List[MigrationStatusSchema])
def get_migrations():
    migrations = storage.load_all_migrations()
    return [{"source_ip": m.source.ip, "state": m.state} for m in migrations]

@route.post("/")
def create_migration(mig: MigrationSchema):
    all_workloads = storage.load_all_workloads()
    wl_dict = {w.ip: w for w in all_workloads}
    source = wl_dict.get(mig.source_ip)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    target_vm = Workload(
        ip=mig.target.target_vm.ip,
        credentials=Credentials(**mig.target.target_vm.credentials.dict()),
        storage=[]
    )

    target = MigrationTarget(
        cloud_type=mig.target.cloud_type,
        cloud_credentials=Credentials(**mig.target.cloud_credentials.dict()),
        target_vm=target_vm
    )

    migration = Migration(
        selected_mount_points=mig.selected_mount_points,
        source=source,
        target=target
    )

    storage.save_migration(migration)
    return {"status": "migration created"}


@route.post("/{source_ip}/run")
def run_migration(source_ip: str):
    migrations = storage.load_all_migrations()
    mig = next((m for m in migrations if m.source.ip == source_ip), None)
    if not mig:
        raise HTTPException(status_code=404, detail="Migration not found")

    if mig.state != MigrationState.not_started:
        raise HTTPException(status_code=400, detail="Migration already started or finished")

    def background_run():
        try:
            mig.run()
            storage.save_migration(mig)
        except Exception as e:
            logger.error(f"Migration failed: {e}")

    threading.Thread(target=background_run).start()
    return {"status": "migration started"}

@route.put("/{source_ip}")
def update_migration(source_ip: str, mig: MigrationSchema):
    all_workloads = storage.load_all_workloads()
    wl_dict = {w.ip: w for w in all_workloads}
    source = wl_dict.get(source_ip)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    target_vm = Workload(
        ip=mig.target.target_vm.ip,
        credentials=Credentials(**mig.target.target_vm.credentials.dict()),
        storage=[MountPoint(**mp.dict()) for mp in mig.target.target_vm.storage]
    )

    target = MigrationTarget(
        cloud_type=mig.target.cloud_type,
        cloud_credentials=Credentials(**mig.target.cloud_credentials.dict()),
        target_vm=target_vm
    )

    migration = Migration(
        selected_mount_points=mig.selected_mount_points,
        source=source,
        target=target
    )

    try:
        storage.update_migration(source_ip, migration)
    except ValueError:
        raise HTTPException(status_code=404, detail="Migration not found for update")

    return {"status": "migration updated"}


@route.delete("/{source_ip}")
def delete_migration(source_ip: str):
    migrations = storage.load_all_migrations()
    index = next((i for i, m in enumerate(migrations) if m.source.ip == source_ip), None)
    if index is None:
        raise HTTPException(status_code=404, detail="Migration not found")

    storage.delete_migration(index)
    return {"status": "migration deleted"}