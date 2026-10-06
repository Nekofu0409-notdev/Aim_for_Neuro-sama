import io
from typing import Text

import httpx
import numpy as np
import scipy.io.wavfile as wav

# from moonshine_voice import ModelArch, Transcriber
# 自作関数
from src.config import STT_PORT

RATE = 16000

# M_MODEL_PATH = join(STT_SRC_PATH, "STT_models", "moonshine", "model", "base-ja")
# M_MODEL_ARCH = ModelArch.BASE

# class Moonshine_Voice:
#     def __init__(self):
#         self.transcriber = Transcriber(
#             model_path = M_MODEL_PATH,  model_arch = M_MODEL_ARCH
#         )

#     async def moonshine(self, chunk: np.ndarray) -> Text:
#         transcript = await asyncio.to_thread(
#             self.transcriber.transcribe_without_streaming, chunk, RATE, 0
#         )
#         for line in transcript.lines:
#             print(
#                 f"Transcript: [{line.start_time:.2f}s - {line.start_time + line.duration:.2f}s] {line.text}"
#             )



async def qwen3_asr(chunk: np.ndarray) -> Text | None:
    buf = io.BytesIO()
    wav.write(buf, RATE, chunk)
    buf.seek(0)

    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(
                f"http://127.0.0.1:{STT_PORT}/v1/audio/transcriptions",
                files = {"file": ("audio.wav", buf, "audio/wav"),},
                data = {"model": "qwen3-asr", "language": "ja"}
            )

    except httpx.ReadTimeout:
        return None

    data = res.json()
    if "text" not in data:
        print(data)
        return ""
    return data["text"]
