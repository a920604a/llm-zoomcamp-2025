from fastapi import FastAPI, HTTPException
from typing import List
import httpx
import logging
import datetime

from schema import Message, ChatCompletionRequest

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ollama_api")

OLLAMA_API_URL = "http://ollama:11434/api/generate"


@app.post("/v1/chat/completions")
async def chat_completion(req: ChatCompletionRequest):
    try:
        prompt = build_prompt(req.messages)

        # 第一次呼叫 LLM
        response_text = await call_ollama(req.model, prompt)

        # 模擬 function trigger
        if "現在幾點" in response_text:
            function_result = await get_current_time()

            # append function call + function response
            new_messages = req.messages + [
                Message(role="assistant", content=None, tool_call_id="tool-1", name="get_current_time"),
                Message(role="function", name="get_current_time", content=function_result)
            ]

            new_prompt = build_prompt(new_messages)
            final_response = await call_ollama(req.model, new_prompt)

            return {
                "id": "chatcmpl-001",
                "object": "chat.completion",
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": final_response
                    },
                    "finish_reason": "stop"
                }]
            }

        return {
            "id": "chatcmpl-001",
            "object": "chat.completion",
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response_text
                },
                "finish_reason": "stop"
            }]
        }

    except Exception as e:
        logger.error(f"錯誤: {e}")
        raise HTTPException(status_code=500, detail="處理失敗")


# 🧠 Prompt 組裝器
def build_prompt(messages: List[Message]) -> str:
    result = ""
    for msg in messages:
        if msg.role == "user":
            result += f"User: {msg.content}\n"
        elif msg.role == "assistant":
            result += f"Assistant: {msg.content or ''}\n"
        elif msg.role == "function":
            result += f"(Function {msg.name} 回傳): {msg.content}\n"
    return result + "Assistant:"


# 🧠 呼叫 Ollama 產生回應
async def call_ollama(model: str, prompt: str) -> str:
    async with httpx.AsyncClient(timeout=60) as client:
        res = await client.post(OLLAMA_API_URL, json={
            "model": model,
            "prompt": prompt,
            "stream": False  # ✅ 確保非 streaming 模式，回傳為單筆 JSON
        })
        res.raise_for_status()

        # 如果仍然回傳多筆 JSON（stream false 無效），手動處理
        try:
            return res.json().get("response", "")
        except Exception:
            # 多筆 JSON，用 splitlines + 取最後一筆
            lines = res.text.strip().splitlines()
            for line in reversed(lines):
                if line.strip().startswith("{"):
                    try:
                        import json
                        obj = json.loads(line)
                        return obj.get("response", "")
                    except Exception:
                        continue
            raise ValueError("無法解析 Ollama 回應")


# 🛠 Function call 模擬函式
async def get_current_time() -> str:
    now = datetime.datetime.now().isoformat()
    return f"現在時間是 {now}"
