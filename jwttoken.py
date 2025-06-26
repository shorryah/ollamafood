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
        payload = jwt.decode(jwtoken,SECRET_KEY,ALGORITHM) #decodes the JWT token using the secret key and algorithm
        return payload #returns the decoded data if info is correct
    except InvalidTokenError:
        return None #returns none if code is expired or fake
    
# this class lets FastAPI check for valid tokens when someone calls a protected API route
class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error) #calls parent class (JWTBearer) and error is raised if there is a problem with the token

    async def __call__(self, request: Request)-> Optional[str]: #runs every time a user tries to access a protected route
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request) #checks the Authorization header to get the token
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.") #If there's no Bearer token, raise a 403 error
            token = credentials.credentials #pulls out the actual token string and passes it to verify_jwt
            if not self.verify_jwt(token): 
                raise HTTPException(status_code=403, detail="Invalid token or expired token.") #if it fails verification, it raises another 403
            return token #if everything is fine, it returns the token to identify the user in the route later
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

#tries to decode the JWT
    def verify_jwt(self, jwtoken: str) -> bool:
        try:
            payload = decodeJWT(jwtoken)
            return True #if it succeeds, token is valid → returns True
        except jwt.ExpiredSignatureError:
            return False
        except jwt.JWTError:
            return False #if token is expired or broken, returns False