"""
Main module that starts the whole app
"""

from fastapi import FastAPI

from app.routers import project, job

# Initialize API
app = FastAPI(
    title="take-over", description="Coverage reports API", version="0.0.1"
)
app.include_router(project.router)
app.include_router(job.router)
