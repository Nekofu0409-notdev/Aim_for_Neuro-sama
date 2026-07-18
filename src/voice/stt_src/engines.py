import asyncio
import numpy as np
from typing import Text
from os.path import join
from moonshine_voice import Transcriber, ModelArch

# 自作関数
from src.config import STT_SRC



RATE = 16000

M_MODEL_PATH = join(STT_SRC, "STT_models", "moonshine", "model", "base-ja")
M_MODEL_ARCH = ModelArch.BASE

class Moonshine_Voice:
    def __init__(self):
        self.transcriber = Transcriber(
            model_path = M_MODEL_PATH,  model_arch = M_MODEL_ARCH
        )

    async def moonshine(self, chunk: np.ndarray) -> Text:
        transcript = await asyncio.to_thread(
            self.transcriber.transcribe_without_streaming, chunk, RATE, 0
        )
        for line in transcript.lines:
            print(
                f"Transcript: [{line.start_time:.2f}s - {line.start_time + line.duration:.2f}s] {line.text}"
            )



class Qwen3_ASR():
    def __init__(self):
        pass

    async def run_qwen3():
        pass