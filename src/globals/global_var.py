import asyncio
from dataclasses import dataclass, field
from queue import Queue


@dataclass
class Global_Var:
    mic: dict[int, tuple[str, Queue]] = field(default_factory = dict)
    vad_q = Queue()

    stt_q = asyncio.Queue()
    tts_q = asyncio.Queue()
    wav_q = Queue()
