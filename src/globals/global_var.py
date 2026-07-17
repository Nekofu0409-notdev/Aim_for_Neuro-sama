import asyncio

class Globals_Var():
    def __init__(self):
        self.stt_queue = asyncio.Queue()
        self.tts_queue = asyncio.Queue()

        self.mic: dict[int, asyncio.Queue] = {}