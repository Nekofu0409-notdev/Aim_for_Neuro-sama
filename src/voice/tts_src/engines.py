import httpx

#自作関数
from src.config import (
    TTS_PORT,
    TTS_SPEAKER,
    TTS_SPEED,
)


class AivisSpeech:
    def __init__(self):
        self.aivis_port = f"http://localhost:{TTS_PORT}"
        self.aivis_query_port = f"{self.aivis_port}/audio_query"
        self.aivis_wav_port = f"{self.aivis_port}/synthesis"
        self.client = httpx.AsyncClient()


    async def r_wav(self, text: str) -> bytes:   # wav

        params = {
            "speaker": TTS_SPEAKER,
            "text": text,
        }

        response = await self.client.post(
            self.aivis_query_port,
            params = params,
            timeout = 20,
        )

        query_json = response.json()
        query_json["speedScale"] = TTS_SPEED
        params = {"speaker": TTS_SPEAKER}

        response = await self.client.post(
            url = self.aivis_wav_port,
            params = params,
            json = query_json,
            timeout = 60,
        )

        return response.content
