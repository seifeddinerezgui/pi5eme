# Authentication middleware
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt
from app.config import settings


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        token = request.headers.get('Authorization')
        if token is None:
            raise HTTPException(status_code=403, detail="Not authorized")

        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            request.state.user = payload.get('sub')
        except jwt.JWTError:
            raise HTTPException(status_code=403, detail="Invalid token")

        response = await call_next(request)
        return response
