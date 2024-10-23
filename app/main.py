# main.py

from fastapi import FastAPI
from app.api.routers import auth, portfolio, user, education, lesson
from app.database import Base, engine
from fastapi.middleware.cors import CORSMiddleware
from app.api.routers import auth, order, portfolio, marketdata,Notification,PriceAlere
from app.database import Base, engine, SessionLocal




from app.middleware.auth_middleware import AuthMiddleware


# Initialize FastAPI app
app = FastAPI()


original_openapi = app.openapi

# Define a custom OpenAPI configuration to include a Bearer token
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema  # Use cached schema if available

    # Call the original OpenAPI method
    openapi_schema = original_openapi()

    # Add a custom security scheme for Bearer token
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",  # Optional: set it to JWT or any other format you want
        }
    }

    # Optionally apply BearerAuth security globally to all routes
    openapi_schema["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema  # Cache the schema to avoid recursion
    return app.openapi_schema

# Assign the custom OpenAPI function to the app
app.openapi = custom_openapi


@app.get("/")
def read_root():
    return {"message": "Welcome to the Trading Simulator API!"}


# CORS configuration
origins = [
    "http://localhost:4200",  # Front-end Angular app URL
    # Add more origins here if needed, or use "*" to allow all origins (not recommended in production)
]

# Create all tables if they don't exist
Base.metadata.create_all(bind=engine)

# Include the routers for the various API endpoints
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])

app.include_router(portfolio.router, prefix="/portfolio", tags=["Portfolio"])
app.include_router(order.router, prefix="/order", tags=["Order"])
app.include_router(marketdata.router, prefix="/market", tags=["MarketData"]) 
app.include_router(Notification.router, prefix="/notifications", tags=["Notifications"])  
app.include_router(PriceAlere.router, prefix="/alerts", tags=["Price Alerts"]) 

@app.get("/")
def read_root():
    return {"message": "Welcome to the Trading Simulator API!"}


app.add_middleware(AuthMiddleware)
app.include_router(portfolio.router, prefix="/portfolio", tags=["Portfolio"])

app.include_router(user.router, prefix="/user", tags=["User"])
app.include_router(lesson.router,prefix="/lesson", tags=['Lesson'])
app.include_router(education.router,prefix="/education",tags=['Education'])

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows requests from Angular app
    allow_credentials=True,  # Allows cookies and credentials
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)
