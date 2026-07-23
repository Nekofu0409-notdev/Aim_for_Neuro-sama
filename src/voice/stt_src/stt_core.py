import json
import asyncio
from queue import Queue

# 自作関数
from .mic import VADs_Operater
from .engines import qwen3_asr
from src.bot import run_bot
from src.config import USERID_PATH



RATE = 16000

class STT_Core:
    def __init__(self, stt_q: asyncio.Queue):
        self.stt_q = stt_q
        self.mic: dict[int, tuple[str, Queue]] = {}
        self.operater = VADs_Operater(self.mic)
        with open(USERID_PATH, encoding = "utf-8") as f:
            self.table = json.load(f)

        # 実験的
        # self.moonshine = Moonshine_Voice()

        # Debug
        # self.i = 0


    async def request(self, user_id, user_name, chunk) -> None:
        text = await qwen3_asr(chunk)
        user = self.table.get(str(user_id))

        if user is not None:
            self.stt_q.put_nowait(f"{user}: {text}")
        else:
            self.stt_q.put_nowait(f"{user_name}: {text}")

        # 実験的
        # await self.moonshine.moonshine(chunk)

        # Debug
        # import numpy as np
        # from scipy.io import wavfile
        # from src.config import STT_SRC_PATH
        # self.i += 1
        # wavfile.write(f"{STT_SRC_PATH}/output_waves/output{self.i}.wav", RATE, chunk.astype(np.float32))


    async def core(self):
        asyncio.create_task(run_bot(self.mic))

        try:
            while True:
                self.operater.operater(self.request)
                await asyncio.sleep(0.001)

        except asyncio.CancelledError:
            raise



if __name__ == "__main__":
    try:
        asyncio.run(STT_Core().core())
    except KeyboardInterrupt:
        pass