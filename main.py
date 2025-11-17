from fastapi import FastAPI
from routes import task_routes

app = FastAPI()

app.include_router(task_routes.router)


@app.get("/health", tags=["health"])
def health_check():
    """
    for now it will check if the critical services are down
    """
    from kafka_publisher import kafka_enabled
    import os
    
    health_status = {
        "status": "healthy",
        "service": "task-manager-api",
        "version": "1.0.0",
        "checks": {
            "api": "ok",
            "kafka": "ok" if kafka_enabled else "disabled",
            "gemini": "ok" if os.getenv("GEMINI_API_KEY") else "not_configured"
        }
    }
    if not kafka_enabled:
        health_status["status"] = "degraded"
    
    return health_status

