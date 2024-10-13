# Authentication middleware
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt , JWTError
from app.config import settings


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip authentication for root ("/"), auth routes ("/auth"), and OpenAPI docs
        if request.url.path in ["/", "/docs", "/redoc", "/openapi.json"] or request.url.path.startswith("/auth"):
            return await call_next(request)

        token = request.headers.get('Authorization')
        if token is None or not token.startswith('Bearer '):
            raise HTTPException(status_code=403, detail="Not authorized")

        try:
            token = token.split(" ")[1]
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            request.state.user = payload.get("sub")
        except (JWTError, IndexError):
            print('error log',JWTError)
            raise HTTPException(status_code=403, detail="Invalid token")

        response = await call_next(request)
        return response

