import asyncio
from backend.app.utils.ai_chat import ai_assistant

async def init_ai():
    print("[AI] Đang load model...")
    await ai_assistant.load_model()
    print("[AI] Model đã sẵn sàng")
