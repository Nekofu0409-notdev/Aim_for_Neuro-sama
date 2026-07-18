import asyncio
from queue import Queue

# 自作関数
from .mic import VADs_Operater
from src.bot import run_bot



RATE = 16000

class STT_Core:
    def __init__(self):
        self.mic: dict[int, tuple[str, Queue]] = {}
        self.operater = VADs_Operater(self.mic)

        # Debug
        # self.i = 0


    async def request(self, user_id, user_name, chunk):
        print(user_name)

        # Debug
        # import numpy as np
        # from scipy.io import wavfile
        # from src.config import STT_SRC
        # self.i += 1
        # wavfile.write(f"{STT_SRC}/output_waves/output{self.i}.wav", RATE, chunk.astype(np.float32))


    async def core(self):
        asyncio.create_task(run_bot(self.mic))

        while True:
            self.operater.operater(self.request)
            await asyncio.sleep(0.001)



if __name__ == "__main__":
    try:
        asyncio.run(STT_Core().core())
    except KeyboardInterrupt:
        pass