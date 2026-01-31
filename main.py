from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
import os
import requests

app = FastAPI()

# =========================
# CONFIG
# =========================

HF_API_KEY = os.getenv("HF_API_KEY")
HF_CHAT_URL = "https://router.huggingface.co/v1/chat/completions"
HF_MODEL = "HuggingFaceH4/zephyr-7b-beta"


# =========================
# MODELS
# =========================

class Payload(BaseModel):
    data: str

# =========================
# ROUTES
# =========================

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
  <title>AI Бухгалтер</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    body {
      font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial;
      background: #0b0b0f;
      color: #eaeaf0;
      margin: 0;
    }
    .wrap {
      max-width: 820px;
      margin: 40px auto;
      padding: 0 16px;
    }
    .card {
      background: #151522;
      border: 1px solid #2a2a3d;
      border-radius: 16px;
      padding: 18px;
    }
    h1 {
      font-size: 18px;
      margin: 0 0 10px 0;
    }
    p {
      opacity: .8;
      margin: 0 0 14px 0;
      font-size: 13px;
      line-height: 1.35;
    }
    textarea {
      width: 100%;
      min-height: 140px;
      border-radius: 12px;
      border: 1px solid #2a2a3d;
      background: #0f0f18;
      color: #eaeaf0;
      padding: 12px;
      font-size: 14px;
      outline: none;
    }
    .row {
      display: flex;
      gap: 10px;
      align-items: center;
      margin-top: 12px;
      flex-wrap: wrap;
    }
    button {
      border: 0;
      border-radius: 12px;
      padding: 10px 14px;
      background: #4c6fff;
      color: white;
      font-weight: 600;
      cursor: pointer;
    }
    button:disabled {
      opacity: .5;
      cursor: not-allowed;
    }
    .status {
      font-size: 13px;
      opacity: .75;
    }
    pre {
      white-space: pre-wrap;
      word-wrap: break-word;
      background: #0f0f18;
      border: 1px solid #2a2a3d;
      border-radius: 12px;
      padding: 12px;
      margin-top: 12px;
      min-height: 120px;
    }
    .chips {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin-top: 10px;
    }
    .chip {
      border: 1px solid #2a2a3d;
      background: #10101a;
      color: #eaeaf0;
      border-radius: 999px;
      padding: 6px 10px;
      font-size: 12px;
      cursor: pointer;
      opacity: .9;
    }
    .chip:hover {
      opacity: 1;
    }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <h1>AI бухгалтер (бесплатный режим)</h1>
      <p>Введи расходы/доходы и вопрос. Ответ будет краткий и по делу.</p>

      <textarea id="input" placeholder="Пример: Бюджет 1000 тг. Хлеб 150 тг. Дорога 500 тг. Что по итогу?"></textarea>

      <div class="chips">
        <div class="chip" onclick="fill(1)">Пример 1</div>
        <div class="chip" onclick="fill(2)">Пример 2</div>
        <div class="chip" onclick="clearAll()">Очистить</div>
      </div>

      <div class="row">
        <button id="btn" onclick="send()">Сделать отчёт</button>
        <div class="status" id="status"></div>
      </div>

      <pre id="out">Ответ появится здесь.</pre>
    </div>
  </div>

<script>
  const btn = document.getElementById("btn");
  const statusEl = document.getElementById("status");
  const out = document.getElementById("out");
  const input = document.getElementById("input");

  function fill(n){
    if(n===1) input.value="Бюджет 1000 тг. Хлеб 150 тг. Дорога 500 тг. Что по итогу и остаток?";
    if(n===2) input.value="Доход 250000 тг. Расходы: аренда 90000, еда 70000, транспорт 20000. Где риск?";
  }

  function clearAll(){
    input.value="";
    out.textContent="Ответ появится здесь.";
    statusEl.textContent="";
  }

  async function send(){
    btn.disabled = true;
    statusEl.textContent = "Думаю (на free может быть медленно)...";
    out.textContent = "";

    try{
      const res = await fetch("/api/process", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({data: input.value})
      });

      const json = await res.json();
      out.textContent = json.result || JSON.stringify(json, null, 2);
      statusEl.textContent = "Готово";
    } catch(e){
      out.textContent = "Ошибка запроса. Попробуй ещё раз.";
      statusEl.textContent = "Ошибка";
    } finally{
      btn.disabled = false;
    }
  }
</script>
</body>
</html>
"""


@app.post("/api/process")
def process(payload: Payload):
    if not HF_API_KEY:
        return {"result": "⚠️ HF_API_KEY не задан. Добавь его в Railway → Variables."}

    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": HF_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Ты бухгалтер для малого бизнеса. "
                    "Ответь строго по структуре:\n"
                    "1) Итог и остаток\n"
                    "2) Риски\n"
                    "3) 2-3 конкретных совета"
                )
            },
            {
                "role": "user",
                "content": payload.data
            }
        ],
        "temperature": 0.3,
        "max_tokens": 350
    }

    try:
        res = requests.post(
            HF_CHAT_URL,
            headers=headers,
            json=body,
            timeout=60
        )
    except requests.exceptions.Timeout:
        return {"result": "⏳ Таймаут. На бесплатном HF это нормально. Попробуй ещё раз."}

    if res.status_code != 200:
        return {"result": f"⚠️ HF ошибка {res.status_code}: {res.text[:300]}"}

    data = res.json()

    try:
        return {"result": data["choices"][0]["message"]["content"].strip()}
    except Exception:
        return {"result": f"⚠️ Неожиданный формат ответа: {str(data)[:300]}"}
