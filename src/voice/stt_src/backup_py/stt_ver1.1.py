#自作関数
from src.config import (
    BASE_DIR,

    STT_MODELS,

    MOONSHINE,
    MOONSHINE_PATH,
    MOONSHINE_ARCH,

    QWENASR,

    AUDIO_INPUT_ID,
)

#ライブラリ
import os
from os.path import join
os.add_dll_directory(join(STT_MODELS, "ffmpeg", "ffmpeg-8.0.1-full_build-shared", "bin"))

import logging
logging.getLogger("torch.utils.flop_counter").setLevel(logging.ERROR)

import torch
import math
import numpy as np
import asyncio
import sounddevice as sd
from multiprocessing import Process, Queue
from collections import deque

from silero_vad import load_silero_vad, VADIterator
from pyannote.audio import Pipeline
from scipy.signal import resample_poly
from moonshine_voice import MicTranscriber, TranscriptEventListener, ModelArch



# VAD処理
class Audio_VAD():
    def __init__(self):
        self.id = AUDIO_INPUT_ID

        device_info = sd.query_devices(self.id, 'input')
        self.sample_rate = int(device_info['default_samplerate'])
        self.block_ms = 32
        self.block_size = math.ceil(self.block_ms * 16 * (self.sample_rate / 16000))
        
        self.loop = None
        self.audio_q = asyncio.Queue()
        self.block_q = asyncio.Queue()
        self.speech_q = asyncio.Queue()

        self.model = load_silero_vad(onnx = True)

        self.iter = VADIterator(
            self.model,
            threshold=0.5,
            sampling_rate=16000,
            min_silence_duration_ms=100,
            speech_pad_ms=30,
            )


    def callback(self, indata, frames, time, status):
        if status:
            print("status:", status)

        self.loop.call_soon_threadsafe(
            self.audio_q.put_nowait,
            indata[:, 0].copy()
            )


    async def audio_input(self):
        self.loop = asyncio.get_running_loop() 

        stream = sd.InputStream(
                samplerate = self.sample_rate,
                channels = 1,
                dtype = "float32",
                blocksize = self.block_size,
                callback = self.callback,
                device = self.id
                )

        try:
            with stream:
                while True:
                    block = await self.audio_q.get()
                    self.audio_q.task_done()

                    # 16000Hzに変換
                    if self.sample_rate != 16000:
                        gcd = np.gcd(self.sample_rate, 16000)
                        up = 16000 // gcd
                        down = self.sample_rate // gcd

                        block = resample_poly(block, up, down).astype(np.float32)
                        block = block[:512]
                    
                    await self.block_q.put(block)

        except asyncio.CancelledError:
            raise


    async def bridge_blocks(self, block_return_q: Queue):
        try:
            while True:
                block = await self.block_q.get()
                self.block_q.task_done()

                await asyncio.to_thread(block_return_q.put, block)

        except asyncio.CancelledError:
            raise



# diarization処理
def pyannote(block_q: Queue, result_q: Queue, time_q: Queue):
    model_path = join(
        STT_MODELS,
        "pyannote",
        "models",
        "models--pyannote--speaker-diarization-community-1",
        "snapshots",
        "3533c8cf8e369892e6b79ff1bf80f7b0286a54ee"
    )

    buffer_sec = 3.0
    window_sec = 0.5
    buffer_size = int(buffer_sec * 16000)
    window_size = int(window_sec * 16000)
    buffer = deque(maxlen = buffer_size)
    window = deque(maxlen = window_size)

    pipeline = Pipeline.from_pretrained(model_path)
    pipeline.to(torch.device("cuda" if torch.cuda.is_available() else "cpu"))

    try:
        while True:
            block = block_q.get()

            if len(window) < window_size:
                window.extend(block)
                continue

            buffer.extend(window)
            window.clear()

            if len(buffer) < buffer_size:
                continue

            audio = np.array(buffer)
            waveform = torch.from_numpy(audio).unsqueeze(0)
            audio_input = {"waveform": waveform, "sample_rate": 16000}

            output = pipeline(audio_input)
            embeddings = output.speaker_embeddings

            print(embeddings)
    
    except KeyboardInterrupt:
        pass



# STT処理
class Moonshine():
    def __init__(self):
        self.model_path = MOONSHINE_PATH
        self.model_arch = None


    async def run_moon(self):

        if MOONSHINE_ARCH == "base":
            self.model_arch = ModelArch.BASE
        elif MOONSHINE_ARCH == "tiny":
            self.model_arch = ModelArch.TINY

        mic_transcriber = MicTranscriber(
            model_path = self.model_path,
            model_arch = self.model_arch,
            update_interval=1.0, 
            device=84,
            samplerate=44100, 
            channels=1,
            blocksize=32768,
            options={
                "vad_max_segment_duration": "15.0",
                "max_tokens_per_second": "13.0",
            }
        )

        class MyListener(TranscriptEventListener):
            def __init__(self):
                self.ga = py.globals.global_var.Globals_Add()

            def on_line_completed(self, event):
                clean_text = event.line.text.replace(" ", "")
                asyncio.run(self.ga.add_stt(clean_text))

        mic_transcriber.add_listener(MyListener())
        mic_transcriber.start()

        try:
            while True:
                await asyncio.sleep(0.1)

        except KeyboardInterrupt:
            mic_transcriber.stop()
            mic_transcriber.close()
            raise



class Qwen3_ASR():
    def __init__(self):
        pass

    async def run_qwen3():
        pass



# それぞれを組み合わせて実行
class Run_STT():
    def __init__(self, globals_var):
        self.av = Audio_VAD()

        self.ms = Moonshine()
        self.qa = Qwen3_ASR()


    async def pyannote_run(self):
        # デバッグ用
        import soundfile as sf
        i = 0

        block_pyannote_q = Queue()
        result_pyannote_q = Queue()
        time_pyannote_q = Queue()

        asyncio.create_task(self.av.audio_input())
        asyncio.create_task(self.av.bridge_blocks(block_pyannote_q))

        p = Process(
            target = pyannote, 
            args = (block_pyannote_q, result_pyannote_q, time_pyannote_q),
            daemon = True
        )
        p.start()

        try:
            while True:
                await asyncio.sleep(0.1)

                # デバッグ用
                # i += 1
                # sf.write(fr"src\voice\output_waves\test{i}.wav", speech, 16000)

        except asyncio.CancelledError:
            raise



class Debug():
    def __init__(self, globals_var):
        self.gv = globals_var
        self.rs = Run_STT(self.gv)


    async def speaker_i(self):
        print("開始")

        try:
            await self.rs.pyannote_run()

        except asyncio.CancelledError:
            raise



if __name__ == "__main__":
    from src.globals import G_Var

    gv = G_Var()

    try:
        asyncio.run(Debug(gv).speaker_i())

    except KeyboardInterrupt:
        print("終了")