import os, re
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import openai
from .tools import calculate, get_time, search_web

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PORT = int(os.getenv("PORT", 8000))
openai.api_key = OPENAI_API_KEY

app = FastAPI(title="LLM Agent Chatbot")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

class ChatRequest(BaseModel):
    query: str

@app.get("/", response_class=HTMLResponse)
def root():
    return open("app/static/index.html").read()  # Serve chatbot UI directly

# Detect if query needs a tool
def detect_tool(msg: str):
    t = msg.lower()
    if t.startswith(("calc:", "calculate:")) or re.search(r"[\d\+\-\*/]", t):
        return "calculator", msg.split(":", 1)[-1].strip()
    if t.startswith(("search:", "find:")):
        return "websearch", msg.split(":", 1)[-1].strip()
    m = re.search(r"time in ([a-zA-Z _/]+)", t)
    if m:
        return "timezone", m.group(1).strip()
    return "llm", msg

# Query OpenAI GPT
def query_openai(prompt: str) -> str:
    resp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=512,
        temperature=0.2
    )
    return resp.choices[0].message.content.strip()

@app.post("/chat/", response_class=JSONResponse)
async def chat(req: ChatRequest):
    tool, arg = detect_tool(req.query)
    if tool == "calculator":
        return {"source": "tool", "tool": "calculator", "output": calculate(arg)}
    if tool == "timezone":
        return {"source": "tool", "tool": "timezone", "output": get_time(arg)}
    if tool == "websearch":
        return {"source": "tool", "tool": "websearch", "output": search_web(arg)}
    try:
        return {"source": "llm", "response": query_openai(req.query)}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
