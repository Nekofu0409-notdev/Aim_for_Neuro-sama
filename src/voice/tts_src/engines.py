import httpx
from typing import Text, Any

#自作関数
from src.config import (
    AIVIS_PORT,
    AIVIS_SPEAKER,
    AIVIS_SPEED,
)



class AivisSpeech:
    def __init__(self):
        self.aivis_port = f"http://localhost:{AIVIS_PORT}"
        self.aivis_query_port = f"{self.aivis_port}/audio_query"
        self.aivis_wav_port = f"{self.aivis_port}/synthesis"
        self.client = httpx.AsyncClient()


    async def r_json(self, text: Text) -> dict[str, Any]:   # json
        params = {
            "speaker": AIVIS_SPEAKER,
            "text": text,
        }

        response = await self.client.post(
            self.aivis_query_port, 
            params = params,
            timeout = 20,
        )

        query_data = response.json()
        return query_data


    async def r_wav(self, query_json: dict[str, Any]) -> bytes:   # wav
        query_json["speedScale"] = AIVIS_SPEED
        params = {"speaker": AIVIS_SPEAKER}

        response = await self.client.post(
            url = self.aivis_wav_port,
            params = params,
            json = query_json,
            timeout = 60,
        )

        return response.content