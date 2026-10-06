import httpx

#自作関数
from src.config import (
    LLM_PORT,
    TTS_PORT,
)


class Confirm_Port:
    def __init__(self):
        self.openai_port = f"http://localhost:{LLM_PORT}"
        self.tts_port = f"http://localhost:{TTS_PORT}"


    async def openai_conf(self):
        url = f"{self.openai_port}/v1/models"

        async with httpx.AsyncClient() as client:
            for _ in range(60):
                try:
                    response = await client.get(url, timeout = 1)
                    if response.status_code == 200:
                        return True

                except httpx.RequestError:
                    pass

        return False


    async def tts_conf(self):
        url = f"{self.tts_port}/docs"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, timeout = 1)
                return response.status_code == 200

            except httpx.RequestError:
                return False



if __name__ == "__main__":
    pass
