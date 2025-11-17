from fastapi import FastAPI
from routes import task_routes

app = FastAPI()

app.include_router(task_routes.router)


@app.get("/health", tags=["health"])
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

