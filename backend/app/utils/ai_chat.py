import os
import re
from llama_cpp import Llama
import asyncio
from pathlib import Path


class AIChatAssistant:
    def __init__(self,
                 model_path="backend/models/nous-hermes-3b/Hermes-3-Llama-3.2-3B.Q8_0.gguf",
                 model_url="https://huggingface.co/username/model/resolve/main/Hermes-3-Llama-3.2-3B.Q8_0.gguf"):
        self.model_path = Path(model_path)
        self.model_url = model_url
        self.model = None
        self.memory = {}
        self.memory_size = 5
        self.spam_keywords = [r"free\s+money", r"viagra", r"http[s]?:\/\/", r"mua\s+like"]

    async def load_model(self):
        if self.model is not None:
            return

        if not os.path.isfile(self.model_path):
            print(f"[AI] Model file không tìm thấy tại {self.model_path}")
            return

        loop = asyncio.get_event_loop()
        self.model = await loop.run_in_executor(None, lambda: Llama(
            model_path=self.model_path,
            n_ctx=2048,
            n_threads=4
        ))
        print(f"[AI] Model loaded from {self.model_path}")

    def is_spam(self, message: str) -> bool:
        text = message.lower()
        for pattern in self.spam_keywords:
            if re.search(pattern, text):
                return True
        if len(set(text)) < 3 and len(text) > 10:
            return True
        return False

    def add_to_memory(self, user_key: str, message: str):
        self.memory.setdefault(user_key, []).append(message)
        if len(self.memory[user_key]) > self.memory_size:
            self.memory[user_key] = self.memory[user_key][-self.memory_size:]

    def generate_reply(self, user_key: str, message: str) -> str:
        if self.model is None:
            return "AI hiện tại chưa sẵn sàng, thử lại sau."

        context = "\n".join(self.memory.get(user_key, []))
        prompt = f"{context}\nNgười dùng hỏi: {message}\nTrả lời ngắn gọn và thân thiện:"

        output = self.model(
            prompt,
            max_tokens=128,
            temperature=0.7,
            top_p=0.9,
            stop=["Người dùng hỏi:"]
        )
        reply = output["choices"][0]["text"].strip()
        self.add_to_memory(user_key, reply)
        return reply


ai_assistant = AIChatAssistant()
