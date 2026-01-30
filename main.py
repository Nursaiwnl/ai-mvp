from fastapi import FastAPI
from pydantic import BaseModel
import os

from openai import OpenAI

app = FastAPI()

class Payload(BaseModel):
    data: str

@app.get("/health")
def health():
    return {"ok": True}

# --- LLM client ---
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

@app.post("/api/process")
def process(payload: Payload):
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Ты бухгалтер для малого бизнеса. Делай краткий и понятный отчёт."
            },
            {
                "role": "user",
                "content": payload.data
            }
        ]
    )

    return {
        "result": resp.choices[0].message.content
    }
