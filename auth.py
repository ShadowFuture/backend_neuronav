from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.db import User, SessionLocal
import hashlib
import os

router = APIRouter()

def hash_password(password: str) -> str:
    salt = os.urandom(16).hex()
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}${hashed}"

def verify_password(password: str, stored: str) -> bool:
    salt, hashed = stored.split("$")
    check = hashlib.sha256((salt + password).encode()).hexdigest()
    return check == hashed

class SignupRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/signup")
def signup(data: SignupRequest):
    db = SessionLocal()

    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=data.email,
        password=hash_password(data.password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "Signup successful", "user_id": user.id}

@router.post("/login")
def login(data: LoginRequest):
    db = SessionLocal()

    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    if not verify_password(data.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    return {"message": "Login successful", "user_id": user.id}
