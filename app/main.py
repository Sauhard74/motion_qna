from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from pathlib import Path

from app.api.routes import questions_router, direct_router
from app.core.config import settings

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(questions_router, prefix=settings.API_V1_STR)
app.include_router(direct_router, prefix=settings.API_V1_STR)

# Set up static files
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")

# Set up templates
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

@app.get("/")
async def root(request: Request):
    """Root endpoint that serves the main HTML page."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/docs")
async def custom_docs_redirect():
    """Redirect to API docs."""
    return {"message": "API documentation", "docs_url": f"{settings.API_V1_STR}/docs"}