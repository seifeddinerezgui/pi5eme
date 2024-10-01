# FastAPI instance and startup
from fastapi import FastAPI
from app.api.routers import auth, portfolio
from app.database import Base, engine
from fastapi.middleware.cors import CORSMiddleware




# Initialize FastAPI app
app = FastAPI()

# CORS configuration
origins = [
    "http://localhost:4200",  # Front-end Angular app URL
    # Add more origins here if needed, or use "*" to allow all origins (not recommended in production)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows requests from Angular app
    allow_credentials=True,  # Allows cookies and credentials
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

# Create all tables if they don't exist
Base.metadata.create_all(bind=engine)
# Include the routers for the various API endpoints
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(portfolio.router, prefix="/portfolio", tags=["Portfolio"])
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Trading Simulator API!"}
