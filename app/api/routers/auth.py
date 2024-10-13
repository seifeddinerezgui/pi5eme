from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.user import UserCreate, UserResponse
from app.schemas.token import Token
from app.models.user import User
from app.database import get_db
from app.utils import hash_password, verify_password, create_access_token
from app.config import settings
from datetime import timedelta

from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.schemas.token import TokenData

router = APIRouter()

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

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "message": "Access token will expire in 30 minutes"
    }




oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user