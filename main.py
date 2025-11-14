from fastapi import FastAPI
from routes import task_routes

app = FastAPI()

app.include_router(task_routes.router)

