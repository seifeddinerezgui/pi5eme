from fastapi import APIRouter, Depends, HTTPException, Cookie
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette.responses import Response

from app.schemas.user import UserCreate, UserResponse
from app.schemas.token import Token
from app.models.user import User
from app.models.portfolio import Portfolio
from app.database import get_db
from app.utils import *
from app.config import settings
from datetime import timedelta

from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.schemas.token import TokenData

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if the user already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email is already registered")

    # Hash the password
    hashed_password = hash_password(user.password)

    # Create a new user object with the additional fields
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        age=user.age,
        experience=user.experience,
        education_level=user.education_level,
        proficiency=user.proficiency
    )

    # Save the user to the database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create a new portfolio with an initial balance for the new user
    initial_balance = 100000.0
    new_portfolio = Portfolio(
        user_id=new_user.id,
        balance=initial_balance
    )
    db.add(new_portfolio)
    db.commit()

    # Return the user response without exposing the password
    return UserResponse(
        id=new_user.id, 
        username=new_user.username, 
        email=new_user.email,
        age=new_user.age,
        experience=new_user.experience,
        education_level=new_user.education_level,
        proficiency=new_user.proficiency
    )



# @router.post("/register", response_model=UserResponse)
# def register(user: UserCreate, db: Session = Depends(get_db)):
#     hashed_pwd = hash_password(user.password)
#     new_user = User(username=user.username, email=user.email, hashed_password=hashed_pwd)
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)
#     return new_user

@router.post("/login")
def login(requestBody : LoginRequest, response : Response,  db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == requestBody.username).first()
    if not user or not verify_password(requestBody.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    refresh_token_expires = timedelta(minutes=settings.refresh_token_expire_minutes)
    access_token = create_access_token(username=user.username, expires_delta=access_token_expires)
    refresh_token = create_refresh_token(username=user.username, expires_delta=refresh_token_expires)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,  # Prevent JavaScript access to the cookie
        samesite="strict",  # Adjust as necessary
    )

    return {
                "access_token": access_token,
                "token_type": "bearer",
                "message": "Access token will expire in 30 minutes"
            }

@router.post("/refresh_token", response_model=Token)
def refresh_access_token(response: Response, refresh_token: str = Cookie(None)):
    if refresh_token is None:
        raise HTTPException(status_code=403, detail="Refresh token is missing")

    try:
        payload = jwt.decode(refresh_token, settings.secret_key, algorithms=[settings.algorithm])
        username = payload.get("sub")

        # You might want to check if the refresh token is valid and belongs to the user
        # This could involve checking it against a database of valid refresh tokens
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid refresh token")

    # Create a new access token
    access_token = create_access_token(username=username, expires_delta=timedelta(minutes=settings.access_token_expire_minutes))
    refresh_token = create_refresh_token(username=username, expires_delta=timedelta(minutes=settings.refresh_token_expire_minutes))
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,  # Prevent JavaScript access to the cookie
        samesite="strict",  # Adjust as necessary
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "message": "New access token generated"
    }



