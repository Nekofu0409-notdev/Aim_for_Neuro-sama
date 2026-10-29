import asyncio
from collections import deque
from contextlib import suppress
from queue import Empty, Queue

import numpy as np

# from maai import Maai, MaaiInput
from silero_vad import VADIterator, load_silero_vad

RATE = 16000
THRETHOLD = 0.7
SILENCE_DURATION = 300
PAD = 100
CHUNK = 512
STREAMING_SECOND = 0.5



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
        self.asr_sent_samples = 0
        self.last_stream_count = 0


    async def fill(self):
        with suppress(asyncio.CancelledError):
            while True:
                try:
                    f32 = self.voice.get_nowait()
                except Empty:
                    f32 = np.zeros(CHUNK, dtype = np.float32)
                self.audio.put(f32)
                await asyncio.sleep(CHUNK / RATE)


    def vad(self) -> tuple:
        try:
            f32 = self.audio.get_nowait()
        except Empty:
            return (None, None)

        event = self.iter(f32)

        if event is not None:
            if "start" in event:
                self.buffer.append(f32)
                self.speaking = True
                return (None, None)

            if "end" in event:
                self.speaking = False
                self.asr_sent_samples = 0
                self.last_stream_count = 0
                self.buffer.append(f32)
                speech = np.concatenate(self.buffer).astype(np.float32)
                self.buffer.clear()
                return ("end", speech)

        if self.speaking:
            self.buffer.append(f32)
            self.asr_sent_samples += len(f32)
            count = self.asr_sent_samples // (RATE * STREAMING_SECOND)

            if count > self.last_stream_count:
                self.last_stream_count = count
                return ("speaking", np.concatenate(self.buffer).astype(np.float32))

        return (None, None)



# class BcDet:
#     def __init__(self):
#         self.ch1 = MaaiInput.Chunk()
#         self.maai = Maai(
#             mode = "bc_det", lang = "jp", frame_rate = 12.5,
#             audio_ch1 = self.ch1,
#             device = "cpu", model_type = "normal-ver2",
#         )
#         self.maai.start()
#         self._buf = np.zeros(0, dtype = np.float32)
#         self.chunk = 160


#     def feed(self, f32):
#         self._buf = np.concatenate([self._buf, np.asarray(f32, dtype = np.float32)])
#         while len(self._buf) >= self.chunk:
#             self.ch1.put_chunk(self._buf[:self.chunk])
#             self._buf = self._buf[self.chunk:]

#         try:
#             r = self.maai.result_dict_queue.get_nowait()
#         except Empty:
#             return

#         p = r["p_bc_det"]
#         print(p)
#         text = "backchannel" if p >= 0.45 else "interruption"
#         print(text)



class VADs_Operater:
    def __init__(self,
        mic: dict[int, tuple[str, Queue]],
        request_main_q: asyncio.Queue,
        request_streaming_q: deque):

        self.mic = mic
        self.vads: dict[int, silero_VAD] = {}
        self.request_main_q = request_main_q
        self.request_streaming_q = request_streaming_q


    def operater(self) -> None:
        for user_id in self.mic:
            user_name, queue = self.mic[user_id]

            if user_id not in self.vads:
                self.vads[user_id] = silero_VAD(queue)

            vad = self.vads[user_id]
            type, npay = vad.vad()

            if type == "speaking":
                self.request_streaming_q.append(npay)
            elif type == "end":
                self.request_main_q.put_nowait((user_id, user_name, npay))
