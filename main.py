from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
import os
import requests

app = FastAPI()

HF_API_KEY = os.getenv("HF_API_KEY")
HF_MODEL = "google/flan-t5-large"
HF_URL = f"https://router.huggingface.co/models/{HF_MODEL}"

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
<title>AI Бухгалтер (free)</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{font-family:system-ui;background:#0b0b0f;color:#eaeaf0;margin:0}
.wrap{max-width:820px;margin:40px auto;padding:0 16px}
.card{background:#151522;border:1px solid #2a2a3d;border-radius:16px;padding:18px}
textarea{width:100%;min-height:140px;border-radius:12px;border:1px solid #2a2a3d;background:#0f0f18;color:#eaeaf0;padding:12px}
button{margin-top:12px;padding:10px 14px;border-radius:12px;border:0;background:#4c6fff;color:white;font-weight:600}
pre{white-space:pre-wrap;background:#0f0f18;border:1px solid #2a2a3d;border-radius:12px;padding:12px;margin-top:12px}
</style>
</head>
<body>
<div class="wrap">
<div class="card">
<h2>AI бухгалтер (бесплатно)</h2>
<textarea id="input" placeholder="Бюджет 1000 тг. Хлеб 150. Дорога 500. Что по итогу?"></textarea>
<button onclick="send()">Сделать отчёт</button>
<pre id="out">Ответ появится здесь.</pre>
</div>
</div>
<script>
async function send(){
  const out=document.getElementById("out");
  out.textContent="Думаю...";
  const res=await fetch("/api/process",{
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({data:document.getElementById("input").value})
  });
  const json=await res.json();
  out.textContent=json.result || JSON.stringify(json);
}
</script>
</body>
</html>
"""

@app.post("/api/process")
def process(payload: Payload):
    if not HF_API_KEY:
        return {"result": "HF_API_KEY не задан в Railway"}

    prompt = f"""
Ты бухгалтер для малого бизнеса.
Ответь кратко и структурно:

1) Итог и остаток
2) Риски
3) 2-3 совета

Данные:
{payload.data}
"""

    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "application/json"
    }

    res = requests.post(
        HF_URL,
        headers=headers,
        json={
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 256,
                "temperature": 0.3
            }
        },
        timeout=45
    )

    if res.status_code != 200:
        return {"result": f"HF error {res.status_code}: {res.text[:300]}"}

    data = res.json()

    if isinstance(data, list) and "generated_text" in data[0]:
        return {"result": data[0]["generated_text"].strip()}

    return {"result": str(data)[:1000]}
