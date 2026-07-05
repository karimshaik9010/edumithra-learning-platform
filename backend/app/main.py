import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import users, roadmaps, planner, analytics, readiness
from app.config import settings

# Create all database tables on startup
# This guarantees that the SQLite database file and structure are generated instantly
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend services for EDUMITHRA -- AI Learning Copilot",
    version="1.0.0"
)

# Enable CORS for Next.js frontend calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for local hackathon demo convenience
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Router Modules
app.include_router(users.router, prefix="/api")
app.include_router(roadmaps.router, prefix="/api")

app.include_router(planner.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(readiness.router, prefix="/api")


@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "database": "connected",
        "groq_api_status": "active" if settings.GROQ_API_KEY else "simulation_fallback"
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
