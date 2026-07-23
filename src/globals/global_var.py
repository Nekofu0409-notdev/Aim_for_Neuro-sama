import asyncio
from queue import Queue


class Globals_Var:
    def __init__(self):
        self.stt_q = asyncio.Queue()
        self.tts_q = asyncio.Queue()

        self.wav_q = Queue()

        self.mic: dict[int, tuple[str, Queue]] = {}