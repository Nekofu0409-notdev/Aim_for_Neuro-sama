import numpy as np
import asyncio
from queue import Queue, Empty
from typing import Callable, Awaitable
from silero_vad import load_silero_vad, VADIterator



RATE = 16000
THRETHOLD = 0.5
SILENCE_DURATION = 300
PAD = 100
CHUNK = 512

class silero_VAD:
    def __init__(self, voice: Queue):
        self.voice = voice
        self.audio = Queue()
        self.task = asyncio.create_task(self.fill())

        self.model = load_silero_vad(onnx = True)
        self.iter = VADIterator(
            self.model,
            threshold = THRETHOLD,
            sampling_rate = RATE,
            min_silence_duration_ms = SILENCE_DURATION,
            speech_pad_ms = PAD,
            )
        
        self.speaking = False
        self.buffer = []


    async def fill(self):
        try:
            while True:
                try:
                    f32 = self.voice.get_nowait()
                except Empty:
                    f32 = np.zeros(CHUNK, dtype = np.float32)
                self.audio.put_nowait(f32)
                await asyncio.sleep(CHUNK / RATE)
                
        except asyncio.CancelledError:
            raise
        
        
    def vad(self) -> np.ndarray | None:
        try:
            f32 = self.audio.get_nowait()
        except Empty:
            return None

        event = self.iter(f32)

        if event is not None:
            if "start" in event:
                self.speaking = True

            if "end" in event:
                self.speaking = False
                self.buffer.append(f32)
                speech = np.concatenate(self.buffer).astype(np.float32)
                self.buffer.clear()
                return speech

        if self.speaking:
            self.buffer.append(f32)

        return None



class VADs_Operater:
    def __init__(self, mic: dict[int, tuple[str, Queue]]):
        self.mic = mic
        self.vads: dict[int, silero_VAD] = {}


    def operater(self, callback: Callable[[int, str, np.ndarray], Awaitable[None]]) -> None:
        for user_id in self.mic:
            user_name, queue = self.mic[user_id]

            if user_id not in self.vads:
                self.vads[user_id] = silero_VAD(queue)

            vad = self.vads[user_id]
            chunk = vad.vad()

            if chunk is not None:
                asyncio.create_task(callback(user_id, user_name, chunk))