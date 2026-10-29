import io

import httpx
import numpy as np
import scipy.io.wavfile as wav

# import torch
# from torchao.quantization import Int4WeightOnlyConfig, quantize_
# from torchao.quantization.quantize_.workflows import (
#     Int4ChooseQParamsAlgorithm,
#     Int4PackingFormat,
# )
# from transformers import AutoModelForMultimodalLM, AutoProcessor
#
# 自作関数
from src.config import STT_PORT

RATE = 16000



class Qwen3_ASR_Main:
    def __init__(self):
        self.client = httpx.AsyncClient(
            base_url = f"http://127.0.0.1:{STT_PORT}",
            timeout = httpx.Timeout(30.0, connect = 5.0),
            limits = httpx.Limits(max_keepalive_connections = 1),
        )


    async def main(self, chunk: np.ndarray) -> str | None:
        buf = io.BytesIO()
        wav.write(buf, RATE, chunk)
        buf.seek(0)

        try:
            res = await self.client.post(
                "/v1/audio/transcriptions",
                files = {"file": ("audio.wav", buf, "audio/wav")},
                data = {"model": "qwen3-asr", "language": "ja"},
            )

            res.raise_for_status()
            data = res.json()

        except httpx.HTTPError as e:
            print(f"Qwen3_ASR_Main Request Error: {e}")
            return None

        if "text" not in data:
            print(data)
            return ""

        return data["text"]


    async def aclose(self):
        await self.client.aclose()



# class Qwen3_ASR_Streaming:
#     def __init__(self):
#         if torch.cuda.is_available():
#             device = "cuda"
#         elif torch.xpu.is_available():
#             device = "xpu"
#         else:
#             device = "cpu"

#         self.processor = AutoProcessor.from_pretrained(STT_STREAMING_PATH)
#         self.model = AutoModelForMultimodalLM.from_pretrained(
#             STT_STREAMING_PATH,
#             dtype = torch.bfloat16,
#             device_map = device,
#         )

#         if device == "cuda":
#             quantize_(self.model, Int4WeightOnlyConfig(
#                 group_size = 32,
#                 int4_packing_format = Int4PackingFormat.TILE_PACKED_TO_4D,
#                 int4_choose_qparams_algorithm = Int4ChooseQParamsAlgorithm.HQQ,
#             ))
#         elif device == "xpu":
#             quantize_(self.model, Int4WeightOnlyConfig(
#                 group_size = 32,
#                 int4_packing_format = Int4PackingFormat.PLAIN_INT32,
#             ))
#         else:
#             print("CPUではint4は未対応。bf16で動かします。")

#         torch.xpu.empty_cache()


#     def _recognition(self, chunk: np.ndarray) -> str:
#         inputs = self.processor.apply_transcription_request(
#             audio = chunk,
#             language = "ja",
#         ).to(self.model.device, self.model.dtype)

#         with torch.inference_mode():
#             output = self.model.generate(**inputs)

#         generated = output[:, inputs["input_ids"].shape[1]:]
#         return self.processor.decode(generated, return_format = "transcription_only")[0]


#     async def streaming(self, chunk: np.ndarray) -> str:
#         return await asyncio.to_thread(self._recognition, chunk)



# class Moonshine_Voice:
#     def __init__(self):
#         self.transcriber = Transcriber(
#             model_path = MOONSHINE_PATH,  model_arch = MOONSHINE_ARCH
#         )

#     async def streaming(self, chunk: np.ndarray) -> str:
#         # transcript = await asyncio.to_thread(
#         #     self.transcriber.transcribe_without_streaming, chunk, RATE, 0
#         # )
#         # return "".join(line.text for line in transcript.lines).strip()
#         return "dummy"



class Qwen3_ASR_Streaming:
    def __init__(self):
        self.client = httpx.AsyncClient(
            base_url = "http://127.0.0.1:40611",
            timeout = httpx.Timeout(30.0, connect = 5.0),
            limits = httpx.Limits(max_keepalive_connections = 1),
        )


    async def streaming(self, chunk: np.ndarray) -> str | None:
        buf = io.BytesIO()
        wav.write(buf, RATE, chunk)
        buf.seek(0)

        try:
            res = await self.client.post(
                "/v1/audio/transcriptions",
                files = {"file": ("audio.wav", buf, "audio/wav")},
                data = {"model": "qwen3-asr", "language": "ja"},
            )

            res.raise_for_status()
            data = res.json()

        except httpx.HTTPError as e:
            print(f"Qwen3_ASR_Streaming Request Error: {e}")
            return None

        if "text" not in data:
            print(data)
            return ""

        return data["text"]


    async def aclose(self):
        await self.client.aclose()
