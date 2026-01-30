from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class Payload(BaseModel):
    data: str

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/", response_class=HTMLResponse)
def home():
    return """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>AI Accountant</title>
</head>
<body style="font-family: sans-serif; max-width: 600px; margin: 40px auto;">
  <h2>AI бухгалтер</h2>
  <textarea id="input" rows="6" style="width:100%;" placeholder="Введите данные"></textarea>
  <br><br>
  <button onclick="send()">Отправить</button>
  <pre id="out" style="margin-top:20px; white-space:pre-wrap;"></pre>

  <script>
    async function send() {
      const out = document.getElementById("out");
      out.textContent = "Думаю...";
      const res = await fetch("/api/process", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ data: document.getElementById("input").value })
      });
      const json = await res.json();
      out.textContent = json.result;
    }
  </script>
</body>
</html>
"""

@app.post("/api/process")
def process(payload: Payload):
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Ты бухгалтер для малого бизнеса. Кратко и по делу."},
            {"role": "user", "content": payload.data}
        ]
    )
    return {"result": resp.choices[0].message.content}
