import asyncio

from prompt_toolkit import PromptSession

#自作関数
from src.config import STT
from src.memory import short_write_user

from .run_llm import Run_OpenAI


class LLM_Core:
    def __init__(self, tts_q: asyncio.Queue):
        self.run = Run_OpenAI(tts_q)
        self.session = PromptSession()


    def return_id(self) -> object:
        return self.run.id


    async def call(self) -> None:
        if STT:
            await self.run.run_openai()

        else:
            print("user:")
            say = await self.session.prompt_async()
            short_write_user(say)
            await self.run.run_openai()


    async def core(self):
        try:
            while True:
                await self.call()

        except asyncio.CancelledError:
            await self.run.close()



if __name__ == "__main__":
    from src.globals import Global_Var
    from src.memory import short_clear
    from src.voice import STT_Core, TTS_Core

    gv = Global_Var()
    llm = LLM_Core(gv.tts_q)
    stt = STT_Core()
    tts = TTS_Core(gv.tts_q, gv.wav_q)

    async def run():
        task1 = llm.core()
        task2 = stt.core()
        task3 = tts.core()

        await asyncio.gather(task1, task2, task3)

    try:
        asyncio.run(run())

    except KeyboardInterrupt:
        print("\n終了")
        short_clear()
