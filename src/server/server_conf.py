import httpx
import asyncio
import time

#自作関数
from src.config import (
    LLM_PORT,

    AIVISSPEECH,
    AIVISSPEECH_PORT,

    TTS,
)



class Confirm_Port():
    def __init__(self):
        self.openai_port = f"http://localhost:{LLM_PORT}"
        self.aivis_port = f"http://localhost:{AIVISSPEECH_PORT}"


    async def openai_conf(self):
        url = f"{self.openai_port}/v1/models"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, timeout = 1)
                return response.status_code == 200

            except:
                return False


    async def aivis_conf(self):
        url = f"{self.aivis_port}/docs"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, timeout = 1)
                return response.status_code == 200

            except:
                return False



class Loop_Conf():
    def __init__(self):
        self.cp = Confirm_Port()


    async def loop_openai(self):

        for _ in range(20):

            if await self.cp.openai_conf() == True:
                return True

            await asyncio.sleep(3)

        print("\nKobold.cppとの通信に失敗しました")
        return False


    async def loop_aivis(self):

        for _ in range(20):

            if await self.cp.aivis_conf() == True:
                return True

            await asyncio.sleep(3)

        print("\nAivisSpeechとの通信に失敗しました")
        return False



class All_Confirm_Port():
    def __init__(self):
        self.aivis = AIVISSPEECH
        self.tts = TTS

        self.lc = Loop_Conf()


    async def all_conf(self):
        tasks = []

        openai_task = asyncio.create_task(self.lc.loop_openai())
        tasks.append(openai_task)

        if self.tts:
            if self.aivis:
                aivis_task = asyncio.create_task(self.lc.loop_aivis())
                tasks.append(aivis_task)

        if tasks:
            results = await asyncio.gather(*tasks)

            if False in results:
                print("サーバとの接続に失敗しました")
                return False

        return True



class Debug():
    def __init__(self):
        self.ar = All_Run()
        self.acp = All_Confirm_Port()


    async def debug(self):
        await self.ar.run()
        conf_task = await self.acp.all_conf()

        try:
            if conf_task:
                print("成功")

            else:
                print("失敗")

        finally:
            await asyncio.sleep(5)



if __name__ == "__main__":
    from .server import All_Run
    asyncio.run(Debug().debug())