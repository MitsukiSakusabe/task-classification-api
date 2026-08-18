from typing import Literal

import json
import httpx
from fastapi import FastAPI,HTTPException
from pydantic import BaseModel,Field

app = FastAPI(
    title="Task Classification API",
    version="1.0.0",
)

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2"
REQUEST_TIMEOUT_SECONDS = 30.0

class TaskRequest(BaseModel):
    text:str = Field(
    min_length=1,
    max_length=1000,
    description="分類対象のテキスト",
    )

class TaskResponse(BaseModel):
    category:str
    priority:str
    reason:str

SYSTEM_PROMPT = """
あなたはタスク分類AIです。
以下のカテゴリのいずれか1つに分類してください。

bug
feature
inquiry
documentation
other

必ずJSONのみを返してください。

{
"category":"<category>"
"priority":"<high|medium|low>",
"reason":"<reason>"
}

priorityは次のルールで決めてください。

high: システム停止や重大な不具合
medium: 通常の不具合・機能追加
low: 軽微な改善・ドキュメント修正

説明文やMarkdown（```json）は付けないでください。
"""

@app.get("/health")
async def health_check() -> dict[str, str]:
    return {
  "status": "ok",
  "service": "task-classification-api",
  "version": "1.0",
  "environment": "development"
}

@app.post(
    "/classify",
    response_model=TaskResponse,
)
async def classify_task(
    request:TaskRequest,
) -> TaskResponse:
    prompt = f"""
{SYSTEM_PROMPT}

テキスト:
{request.text}
"""
    payload = {
        "model" : OLLAMA_MODEL,
        "prompt" : prompt,
        "stream" : False,
    }

    try:
        async with httpx.AsyncClient(
            timeout = REQUEST_TIMEOUT_SECONDS
        )as client:
            response =await client.post(
                OLLAMA_URL,
                json=payload,
            )

            response.raise_for_status()

            data = response.json()

            llm_response = data.get("response","").strip()
            ai_data = json.loads(llm_response)

            category = ai_data["category"]
            priority = ai_data["priority"]
            reason = ai_data["reason"]

            return TaskResponse(
                category=category,
                priority=priority,
                reason=reason,
            )
                
    except httpx.ConnectError as exc:
        raise HTTPException(
            status_code=503,
            detail="Ollama server is unavailable",
        )from exc
        
    except httpx.TimeoutException as exc:
        raise HTTPException(
            status_code=504,
            detail="Ollama request timed out.",
        )from exc

    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Ollama returned HTTP {exc.response.status_code}."
        )from exc

    ##except Exception as exc:
        ##print(type(exc))
        ##print(exc)
        #raise

# Git practice