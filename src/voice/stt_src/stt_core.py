import asyncio
import json
from contextlib import suppress
from queue import Queue

# 自作関数
from src.bot import run_bot
from src.config import USERID_PATH
from src.llm import LLM_Core

from .engines import qwen3_asr
from .mic import VADs_Operater

RATE = 16000

class STT_Core:
    def __init__(self, vad_q: Queue, stt_q: asyncio.Queue, llm_core: LLM_Core, wav_q: Queue):
        self.vad_q = vad_q
        self.stt_q = stt_q
        self.wav_q = wav_q
        self.llm = llm_core
        self.request_q = asyncio.Queue()
        self.mic: dict[int, tuple[str, Queue]] = {}
        self.operater = VADs_Operater(self.mic, vad_q, self.request_q)
        with open(USERID_PATH, encoding = "utf-8") as f:
            self.table = json.load(f)

        # 実験的
        # self.moonshine = Moonshine_Voice()

        # Debug
        # self.i = 0


    async def request(self):
        with suppress(asyncio.CancelledError):
            while True:
                user_id, user_name, chunk = await self.request_q.get()
                text = await qwen3_asr(chunk)

                if text is None:
                    return
                user = self.table.get(str(user_id))

                if user is not None:
                    await self.stt_q.put(f"{user}: {text}")
                else:
                    await self.stt_q.put(f"{user_name}: {text}")

        # 実験的
        # await self.moonshine.moonshine(chunk)

        # Debug
        # import numpy as np
        # from scipy.io import wavfile
        # from src.config import STT_SRC_PATH
        # self.i += 1
        # wavfile.write(f"{STT_SRC_PATH}/output_waves/output{self.i}.wav", RATE, chunk.astype(np.float32))


    async def core(self):
        asyncio.create_task(run_bot(self.mic, self.vad_q, self.llm, self.wav_q))
        task = asyncio.create_task(self.request())

        try:
            while True:
                self.operater.operater()
                await asyncio.sleep(0.001)

        except asyncio.CancelledError:
            task.cancel()
            for vad in self.operater.vads.values():
                vad.task.cancel()



if __name__ == "__main__":
    pass

    # try:
    #     asyncio.run(STT_Core().core())
    # except KeyboardInterrupt:
    #     pass
