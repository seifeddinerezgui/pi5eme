from datetime import time
from fastapi import FastAPI, BackgroundTasks
# FastAPI instance and startup
from fastapi import FastAPI

from app.api.routers import auth, portfolio, comparison, prediction, risk, strategy, note
from app.api.routers import auth, portfolio, user, education, lesson

from app.api.routers import auth, portfolio, comparison, prediction, risk, strategy, stock_forcasting
from app.api.routers import auth, portfolio, user, education, lesson, VaR_router

from app.database import Base, engine
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
    "http://127.0.0.1:8000",  # Local backend server
    "http://localhost:8000",  # In case of a different local setup
]




# Create all tables if they don't exist
Base.metadata.create_all(bind=engine)

# Include API routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(portfolio.router, prefix="/portfolio", tags=["Portfolio"])
app.include_router(order.router, prefix="/order", tags=["Order"])
app.include_router(marketdata.router, prefix="/market", tags=["MarketData"])
app.include_router(comparison.router, prefix="/comparison", tags=["Comparison"])
app.include_router(prediction.router, prefix="/predeiction", tags=["Prediction"])
app.include_router(risk.router, prefix="/risk", tags=["Risk"])
app.include_router(strategy.router, prefix="/strategy", tags=["Strategy"])
app.include_router(user.router, prefix="/user", tags=["User"])
app.include_router(lesson.router,prefix="/lesson", tags=['Lesson'])
app.include_router(education.router,prefix="/education",tags=['Education'])

app.include_router(note.router,prefix="/note",tags=['Note'])


app.include_router(stock_forcasting.router, prefix="/forecast", tags=["Forecasting"])
app.include_router(VaR_router.router, prefix="/risk", tags=["Risk Management"])

# Add custom middleware
app.add_middleware(AuthMiddleware)
@app.get("/")
def read_root():
    """Root endpoint."""
    return {"message": "Welcome to the Trading Simulator API!"}


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows requests from Angular app
    allow_credentials=True,  # Allows cookies and credentials
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)
