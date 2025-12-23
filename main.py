from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import users

# Create tables on startup (for dev only; use Alembic in production)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="My Project API")

# Allow frontend (React) to access API
origins = [
    "http://localhost:3000",  # React dev server
    # Add your deployed frontend URL here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router)

# Health check route
@app.get("/")
def health_check():
    return {"status": "API is running"}