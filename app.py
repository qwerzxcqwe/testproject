import fastapi
import api

app = fastapi.FastAPI()
app.include_router(api.main_router)