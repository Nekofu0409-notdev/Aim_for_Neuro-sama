import logging

logger = logging.getLogger(__name__)

import asyncio
import json
from collections import deque
from contextlib import suppress
from queue import Queue

# 自作関数
from src.bot import run_bot
from src.config import USERID_PATH
from src.llm import Run_OpenAI_Judge
from src.memory import short_write_user

from .engines import Qwen3_ASR_Main, Qwen3_ASR_Streaming
from .mic import VADs_Operater

RATE = 16000
STREAMING_SECOND = 0.5



class STT_Core:
    def __init__(self, wav_q: asyncio.Queue):
        self.wav_q = wav_q
        self.stt_main = Qwen3_ASR_Main()
        self.stt_streaming = Qwen3_ASR_Streaming()
        self.judge = Run_OpenAI_Judge()
        self.request_main_q = asyncio.Queue()
        self.request_streaming_q = deque(maxlen = 1)
        self.mic: dict[int, tuple[str, Queue]] = {}
        self.operater = VADs_Operater(self.mic, self.request_main_q, self.request_streaming_q)
        with open(USERID_PATH, encoding = "utf-8") as f:
            self.table = json.load(f)


    async def request_main(self):
        with suppress(asyncio.CancelledError):
            while True:
                user_id, user_name, chunk = await self.request_main_q.get()
                text = await self.stt_main.main(chunk)

                if text is None:
                    continue

                user = self.table.get(str(user_id))
                name = user if user is not None else user_name
                print(f"{name}: {text}")
                short_write_user(f"{name}: {text}")


    async def request_streaming(self):
        with suppress(asyncio.CancelledError):
            while True:
                if not self.request_streaming_q:
                    await asyncio.sleep(STREAMING_SECOND)
                    continue

                chunk = self.request_streaming_q.popleft()
                text = await self.stt_streaming.streaming(chunk)

                if text is None:
                    continue

                judge = await self.judge.run_judge(text)
                logger.info(judge, text)


    async def core(self):
        asyncio.create_task(run_bot(self.mic, self.wav_q))
        task1 = asyncio.create_task(self.request_main())
        task2 = asyncio.create_task(self.request_streaming())

        try:
            while True:
                self.operater.operater()
                await asyncio.sleep(0.001)

        except asyncio.CancelledError:
            task1.cancel()
            task2.cancel()
            await self.stt_main.aclose()
            await self.stt_streaming.aclose()
            await self.judge.close()
            for vad in self.operater.vads.values():
                vad.task.cancel()



if __name__ == "__main__":
    import logging

    logging.basicConfig(
        level = logging.WARNING,
        format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    logger = logging.getLogger(__name__)

    from src.globals.global_var import Global_Var
    from src.memory import short_clear
    from src.server import *


    gv = Global_Var
    oas = OpenAI_Server()
    ss = STT_Server()

    async def main():
        await oas.start_judge()
        await ss.start_main()
        await ss.start_judge()

        try:
            confs = await asyncio.gather(
                llm_judge_conf(),
                stt_main_conf(),
                stt_judge_conf(),
            )

            if not all(confs):
                logger.error(
                    "サーバの起動に失敗しました (llm_judge=%s, stt_main=%s, stt_judge=%s)",
                    confs[0], confs[1], confs[2],
                )
                return

            await STT_Core(gv.wav_q).core()

        finally:
            ss.stop_main()
            ss.stop_judge()
            oas.stop_judge()
            short_clear()

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
