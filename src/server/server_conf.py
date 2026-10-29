import asyncio

import httpx

#自作関数
from src.config import (
    JUDGE_LLM_HOST,
    JUDGE_LLM_PORT,
    JUDGE_STT_PORT,
    LLM_HOST,
    LLM_PORT,
    STT_PORT,
    TTS_PORT,
)


async def llm_main_conf() -> bool:
    url = f"http://{LLM_HOST}:{LLM_PORT}/v1/models"

    async with httpx.AsyncClient() as client:
        for _ in range(60):
            try:
                response = await client.get(url, timeout = 1)
                if response.status_code == 200:
                    return True

            except httpx.RequestError:
                pass

            await asyncio.sleep(1.0)

    return False


async def llm_judge_conf() -> bool:
    url = f"http://{JUDGE_LLM_HOST}:{JUDGE_LLM_PORT}/v1/models"

    async with httpx.AsyncClient() as client:
        for _ in range(60):
            try:
                response = await client.get(url, timeout = 1)
                if response.status_code == 200:
                    return True

            except httpx.RequestError:
                pass

            await asyncio.sleep(1.0)

    return False


async def stt_main_conf() -> bool:
    url = f"http://localhost:{STT_PORT}/v1/models"

    async with httpx.AsyncClient() as client:
        for _ in range(60):
            try:
                response = await client.get(url, timeout = 1)
                if response.status_code == 200:
                    return True

            except httpx.RequestError:
                pass

            await asyncio.sleep(1.0)

    return False


async def stt_judge_conf() -> bool:
    url = f"http://localhost:{JUDGE_STT_PORT}/v1/models"

    async with httpx.AsyncClient() as client:
        for _ in range(60):
            try:
                response = await client.get(url, timeout = 1)
                if response.status_code == 200:
                    return True

            except httpx.RequestError:
                pass

            await asyncio.sleep(1.0)

    return False


async def tts_conf() -> bool:
    url = f"http://localhost:{TTS_PORT}/docs"

    async with httpx.AsyncClient() as client:
        for _ in range(60):
            try:
                response = await client.get(url, timeout = 1)
                if response.status_code == 200:
                    return True

            except httpx.RequestError:
                pass

            await asyncio.sleep(1.0)

    return False



if __name__ == "__main__":
    pass
