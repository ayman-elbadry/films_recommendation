"""
FastAPI application entry point.
Includes auth and ratings routers, CORS middleware, and a health check.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.auth_router import router as auth_router
from routers.ratings_router import router as ratings_router
from routers.recommendations_router import router as recommendations_router

# ------------------------------------------------------------------
# App
# ------------------------------------------------------------------
app = FastAPI(
    title="Movie Recommendation API",
    description="Hybrid movie recommendation system with JWT auth and JSON storage",
    version="1.0.0",
)

# CORS — allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router)
app.include_router(ratings_router)
app.include_router(recommendations_router)


# ------------------------------------------------------------------
# Health check
# ------------------------------------------------------------------
@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "Movie Recommendation API is running"}
