from fastapi import APIRouter, HTTPException
from models import User
from schemas import LoginRequest
from services import register_user, login_user
from jwttoken import create_access_token 
from datetime import timedelta

router = APIRouter(prefix="/auth")

# Post endpoint for user to register
@router.post("/register")
def register(user: User):
    success, msg = register_user(user)  # success: True or False followed by message; register_user is called to register the user
    if not success:
        raise HTTPException(status_code=400, detail=msg) #print error message if something(s) fails
    return {"message": "User registered successfully"}  # message when registered successfully

 # Post endpoint for user to login using email and password
@router.post("/login") 
def login(login_req: LoginRequest):
    success, data = login_user(login_req.email, login_req.password)  #similar to the one above, this time calling login_req to check if requirements are met
    if not success:
        raise HTTPException(status_code=401, detail=data) #error message
    
    access_token_expires = timedelta(minutes=30) #token has a lifespan of 30 mins
    access_token = create_access_token(data={"sub": login_req.email}, expires_delta=access_token_expires) #stores email under sub and expiry info
    return {"access_token": access_token,"token_type": "bearer"} #returns the JWT token
