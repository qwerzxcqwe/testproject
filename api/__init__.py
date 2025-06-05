import fastapi
from .workloads.route import route as route_workloads
from .migrations.route import route as route_migration
main_router = fastapi.APIRouter()

main_router.include_router(route_workloads)
main_router.include_router(route_migration)

