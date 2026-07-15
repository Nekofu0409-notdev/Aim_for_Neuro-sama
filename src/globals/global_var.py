#py\globals\global_var.py

import asyncio

class Globals_Var():
    def __init__(self):
        self.stt_queue = asyncio.Queue()
        self.tts_queue = asyncio.Queue()