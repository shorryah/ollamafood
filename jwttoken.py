from datetime import datetime, timedelta, timezone
from typing import Optional  #for token expiry timestamps
from fastapi import Depends, HTTPException, Request, status #Depends helps inject dependencies like token verification
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordBearer
import jwt #library to create and verify tokens
from jwt.exceptions import InvalidTokenError #handles errors if token is fake or expires
from pydantic import BaseModel

SECRET_KEY = "68f54473649a060b772a700a8a4520f7ce737ae6b1edeac40f1f933ebce34d74" #secret to sign and verify tokens
ALGORITHM = "HS256" #using HS256 (HMAC with SHA-256)
ACCESS_TOKEN_EXPIRE_MINUTES = 30 #Token expires after 30 minutes

class Token(BaseModel):
    access_token: str
    token_type: str

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")  #FastAPI uses this to look for the JWT token in the Authorization: Bearer <token> header

# creates a new token when a user logs in
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

#reads token, validates it and extract info from it
def verify_token(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")  # extract subject (username or user id)
        if user_id is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    return user_id  # return the user identifier if you want to use it later


def decodeJWT(jwtoken: str):
    try:
        payload = jwt.decode(jwtoken,SECRET_KEY,ALGORITHM)
        return payload
    except InvalidTokenError:
        return None
    
class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            token = credentials.credentials
            if not self.verify_jwt(token):
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")
            return token
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, jwtoken: str) -> bool:
        try:
            payload = decodeJWT(jwtoken)
            return True
        except jwt.ExpiredSignatureError:
            return False
        except jwt.JWTError:
            return False