import asyncio
from contextlib import suppress

from prompt_toolkit import PromptSession

#自作関数
from src.config import STT

from .run_llm import Run_OpenAI


class LLM_Core:
    def __init__(self, stt_q: asyncio.Queue, tts_q: asyncio.Queue):
        self.run = Run_OpenAI(tts_q)
        self.session = PromptSession()
        self.stt_q = stt_q
        self.say = ""
        self.task = None
        self.nowait = False


    def return_id(self) -> object:
        return self.run.id


    def reasoning_cancel_wait(self):
        self.nowait = False
        if self.task is not None:
            self.task.cancel()


    def reasoning_cancel_nowait(self, text):
        self.nowait = True
        if self.task is not None:
            self.task.cancel()
        self.say = text + self.say


    async def call(self) -> None:
        say = ""
        cancelled = self.task and self.task.cancelled()

        if STT:
            if not (cancelled and self.nowait):
                say = await self.stt_q.get()

            while not self.stt_q.empty():
                say = say + "\n" + await self.stt_q.get()

            self.say = self.say + "\n" + say
            self.task = asyncio.create_task(self.run.run_openai(self.say))
            res = await self.task

            if res != "cancelled":
                self.say = ""

        else:
            print("user:")
            say = await self.session.prompt_async()
            await self.run.run_openai(say)


    async def core(self):
        with suppress(asyncio.CancelledError):
            while True:
                await self.call()



if __name__ == "__main__":
    from src.globals import Global_Var
    from src.memory import short_clear
    from src.voice import STT_Core, TTS_Core

    gv = Global_Var()
    llm = LLM_Core(gv.stt_q, gv.tts_q)
    stt = STT_Core(gv.vad_q, gv.stt_q, llm, gv.wav_q)
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
