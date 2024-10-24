from datetime import time
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from app.api.routers import auth, order, portfolio, marketdata
from app.database import Base, engine, SessionLocal
from app.middleware.auth_middleware import AuthMiddleware
from app.services.OrderService import OrderService
from sqlalchemy.orm import Session
import asyncio  # Use asyncio for background processing

# Initialize FastAPI app
app = FastAPI()

# Store the original OpenAPI function
original_openapi = app.openapi


def custom_openapi():
    """Generate a custom OpenAPI schema with Bearer token security."""
    if app.openapi_schema:
        return app.openapi_schema  # Use cached schema

    # Call the original OpenAPI function only once
    openapi_schema = original_openapi()

    # Add Bearer token security schema
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    # Apply BearerAuth security globally
    openapi_schema["security"] = [{"BearerAuth": []}]

    # Cache the modified schema
    app.openapi_schema = openapi_schema

    return app.openapi_schema

# Assign custom OpenAPI function to the app
app.openapi = custom_openapi

@app.on_event("startup")
async def startup_event():
    """Startup event to initiate background tasks."""
    db = SessionLocal()  # Open a DB session
    asyncio.create_task(background_task_runner(db))  # Schedule background task

async def background_task_runner(db: Session):
    """Background task to check and process limit orders every minute."""
    while True:
        OrderService.process_limit_orders(db)  # Process pending limit orders
        await asyncio.sleep(60)  # Wait for 60 seconds before next check

# CORS configuration
origins = [
    "http://localhost:4200",  # Front-end Angular app
    # Add more origins or "*" for all (not recommended in production)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables if they don't exist
Base.metadata.create_all(bind=engine)

# Include API routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(portfolio.router, prefix="/portfolio", tags=["Portfolio"])
app.include_router(order.router, prefix="/order", tags=["Order"])
app.include_router(marketdata.router, prefix="/market", tags=["MarketData"])

# Add custom middleware
app.add_middleware(AuthMiddleware)
@app.get("/")
def read_root():
    """Root endpoint."""
    return {"message": "Welcome to the Trading Simulator API!"}





