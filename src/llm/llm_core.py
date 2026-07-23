import asyncio
from prompt_toolkit import PromptSession

#自作関数
from .run_llm import Run_OpenAI
from src.config import STT



class LLM_Core:
    def __init__(self, stt_q: asyncio.Queue):
        self.run = Run_OpenAI()
        self.session = PromptSession()
        self.stt_q = stt_q


    async def call(self) -> None:
        if STT:
            say = await self.stt_q.get()

            while not self.stt_q.empty():
                say += await self.stt_q.get()

            print(f"user:\n{say}")
            await self.run.run_openai(say)

        else:
            print("user:")
            say = await self.session.prompt_async()
            await self.run.run_openai(say)

    
    async def core(self):
        try:
            while True:
                await self.call()

        except asyncio.CancelledError:
            raise



if __name__ == "__main__":
    from src.memory import short_clear
    from src.globals import Globals_Var
    from src.voice import STT_Core

    q = Globals_Var().stt_q
    llm_core = LLM_Core(q)
    stt_core = STT_Core(q)

    async def run():
        task1 = llm_core.core()
        task2 = stt_core.core()

        await asyncio.gather(task1, task2)

    try:
        print("開始")
        asyncio.run(run())

    except KeyboardInterrupt:
        print("\n終了")
        short_clear()