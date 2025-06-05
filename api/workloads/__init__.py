from typing import List
from fastapi import HTTPException
from models.workload import Workload, Credentials, MountPoint
from persistence import storage
from ..models import WorkloadSchema, WorkloadUpdateSchema
from .route import route

@route.get("/", response_model=List[WorkloadSchema])
def list_workloads():
    return storage.load_all_workloads()

@route.post("/")
def create_workload(wl: WorkloadSchema):
    try:
        workload = Workload(
            ip=wl.ip,
            credentials=Credentials(**wl.credentials.dict()),
            storage=[MountPoint(**mp.dict()) for mp in wl.storage]
        )
        storage.save_workload(workload)
        return {"status": "ok"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@route.put("/{ip}")
def modify_workload(ip: str, updated_data: WorkloadUpdateSchema):
    all_workloads = storage.load_all_workloads()
    index = next((i for i, w in enumerate(all_workloads) if w.ip == ip), None)

    if index is None:
        raise HTTPException(status_code=404, detail="Workload not found")

    updated_workload = Workload(
        ip=ip,
        credentials=Credentials(**updated_data.credentials.dict()),
        storage=[MountPoint(**m.dict()) for m in updated_data.storage]
    )

    storage.update_workload(index, updated_workload)
    return {"status": "workload updated"}

@route.delete("/{ip}")
def delete_workload(ip: str):
    storage.delete_workload(ip)
    return {"status": "deleted"}