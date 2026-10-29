import asyncio
from dataclasses import dataclass, field
from queue import Queue


@dataclass
class Global_Var:
    mic: dict[int, tuple[str, Queue]] = field(default_factory = dict)

    tts_q = asyncio.Queue()
    wav_q = asyncio.Queue()
