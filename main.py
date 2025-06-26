from fastapi import FastAPI
from routes import authentication, food

app = FastAPI()

app.include_router(authentication.router)
app.include_router(food.router, prefix="/chat")