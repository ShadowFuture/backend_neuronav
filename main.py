import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.ai import router as ai_router

from backend.auth import router as auth_router
from backend.ai import router as ai_router
from backend.echo import router as echo_router
from backend.db import Base, engine

load_dotenv()

app = FastAPI()

Base.metadata.create_all(bind=engine)


app.include_router(ai_router, prefix="/ai")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth")
app.include_router(ai_router, prefix="/ai")
app.include_router(echo_router, prefix="/utils")

@app.get("/home")
def home():
    return {"message": "Backend is running!"}

