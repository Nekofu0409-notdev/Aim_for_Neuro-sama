import asyncio
import sys
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout

#自作関数
from .run_llm import Run_OpenAI



class Prepare_LLM():
    def __init__(self):
        self.session = PromptSession()


    async def input_keyboard(self):
        self.kb_say = None

        try:
            self.kb_say = await self.session.prompt_async()
            return self.kb_say
        
        except asyncio.CancelledError:
            raise


    async def run_llm(self, say):
        self.say = say

        ro = Run_OpenAI()
        return asyncio.create_task(ro.run_openai(say = self.say))



class Call_LLM():
    def __init__(self, globals_var):
        self.pl = Prepare_LLM()
        self.globals = globals_var

    async def call_llm_stt(self):
        print("開始 ( Ctrl+C で終了)\n")

        try:
            while True:

                self.say = await self.globals.stt_queue.get()
                self.globals.stt_queue.task_done()

                while not self.globals.stt_queue.empty():
                    self.say += await self.globals.stt_queue.get()
                    self.globals.stt_queue.task_done()

                print("user:", self.say)
                
                await self.pl.run_llm(self.say)

        except asyncio.CancelledError:
            raise


    async def call_llm_keyboard(self):
        self.say = None

        print("開始 ( Ctrl+C で終了)\n")

        try:
            while True:
                print("user:")
                self.say = await self.pl.input_keyboard()
                
                task = await self.pl.run_llm(self.say)
                await task

        except asyncio.CancelledError:
            raise


if __name__ == "__main__":
    from src.memory import S_Memory
    from src.globals import G_Var

    #グローバル変数もどき
    gv = G_Var()

    cl = Call_LLM(gv)

    try:
        #stt = false
        asyncio.run(cl.call_llm_keyboard())

    except KeyboardInterrupt:
        print("\n終了")
        S_Memory().short_clear()