from fastapi import APIRouter

router = APIRouter()

@router.get("/echo")
def echo(message: str = "Hello"):
    return {"echo": message}
