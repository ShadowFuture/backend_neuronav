import json
import requests
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import re

router = APIRouter()

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "mistral"


# -----------------------------
# Request / Response Models
# -----------------------------

class SimplifyTaskRequest(BaseModel):
    task: str

class SimplifyTaskResponse(BaseModel):
    steps: list[str]


class BrainDumpRequest(BaseModel):
    text: str

class BrainDumpResponse(BaseModel):
    tasks: list[str]
    reminders: list[str]
    emotional_load: str
    decisions: list[str]
    next_steps: list[str]


# -----------------------------
# JSON BLOCK EXTRACTOR (WORKS 100%)
# -----------------------------

def extract_json_block(text: str):
    """
    Extract the FIRST JSON block from the model output.
    Handles markdown fences, extra text, explanations, etc.
    """

    # Remove markdown fences
    cleaned = re.sub(r"```json", "", text)
    cleaned = re.sub(r"```", "", cleaned)

    # Find the FIRST JSON object
    match = re.search(r"\{(?:[^{}]|(?:\{[^{}]*\}))*\}", cleaned)

    if not match:
        raise ValueError("Model did not return JSON")

    return json.loads(match.group(0))


# -----------------------------
# STREAMING + JSON BLOCK EXTRACTOR
# -----------------------------

def get_json_from_stream(prompt: str):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "stream": True
        },
        stream=True
    )

    buffer = ""

    for chunk in response.iter_lines():
        if not chunk:
            continue

        data = json.loads(chunk.decode("utf-8"))

        if data.get("done"):
            break

        content_piece = data.get("message", {}).get("content", "")
        buffer += content_piece

    print("MODEL OUTPUT:", buffer)

    # Extract ONLY the JSON block
    return extract_json_block(buffer)


# -----------------------------
# Simplify Task Endpoint
# -----------------------------

@router.post("/simplify-task", response_model=SimplifyTaskResponse)
def simplify_task(data: SimplifyTaskRequest):
    prompt = (
        "Break this task into simple steps. "
        "Return ONLY JSON: {\"steps\": [\"step 1\", \"step 2\"]}.\n"
        f"Task: {data.task}"
    )

    try:
        parsed = get_json_from_stream(prompt)
        return SimplifyTaskResponse(**parsed)

    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


# -----------------------------
# Brain Dump Endpoint
# -----------------------------

@router.post("/brain-dump", response_model=BrainDumpResponse)
def brain_dump(data: BrainDumpRequest):
    prompt = (
        "Organize this brain dump into JSON with keys: "
        "tasks, reminders, emotional_load, decisions, next_steps.\n"
        "Return ONLY JSON.\n"
        f"{data.text}"
    )

    try:
        parsed = get_json_from_stream(prompt)
        return BrainDumpResponse(**parsed)

    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))