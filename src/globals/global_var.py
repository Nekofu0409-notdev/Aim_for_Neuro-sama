import asyncio
from queue import Queue

class Globals_Var:
    def __init__(self):
        self.stt_queue = asyncio.Queue()
        self.tts_queue = asyncio.Queue()

        self.mic: dict[int, tuple[str, Queue]] = {}