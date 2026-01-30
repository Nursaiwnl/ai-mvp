from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Payload(BaseModel):
    data: str

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/api/process")
def process(payload: Payload):
    return {"result": f"received: {payload.data}"}
