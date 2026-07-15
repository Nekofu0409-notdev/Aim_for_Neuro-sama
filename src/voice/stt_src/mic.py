import asyncio
import pythoncom
import sounddevice as sd
import numpy as np
from scipy.signal import resample_poly
from silero_vad import load_silero_vad, VADIterator
from multiprocessing import Queue

#自作関数
from src.config import AUDIO_INPUT_ID



# MIC入力 + VAD処理
class Audio_VAD():
    def __init__(self):
        device_info = sd.query_devices(AUDIO_INPUT_ID, 'input')
        self.sample_rate = int(device_info['default_samplerate'])
        self.frame_size = 512
        
        self.loop = None
        self.audio_q = asyncio.Queue()
        self.block_q = asyncio.Queue()

        self.model = load_silero_vad(onnx = True)
        self.iter = VADIterator(
            self.model,
            threshold=0.5,
            sampling_rate=16000,
            min_silence_duration_ms=300,
            speech_pad_ms=30,
            )


    def callback(self, indata, frames, time, status) -> None:
        if status:
            print("status:", status)

        self.loop.call_soon_threadsafe(
            self.audio_q.put_nowait,
            indata[:, 0].copy()
            )


    async def audio_input(self, block_multi_q: Queue, fin_q: asyncio.Queue) -> None:
        self.loop = asyncio.get_running_loop() 
        buffer = []
        pythoncom.CoInitialize()

        stream = sd.InputStream(
                samplerate = self.sample_rate,
                channels = 1,
                dtype = "float32",
                blocksize = 1024,
                callback = self.callback,
                device = AUDIO_INPUT_ID
                )

        try:
            with stream:
                while True:
                    # 終了条件
                    if not fin_q.empty():
                        msg = await fin_q.get()
                        fin_q.task_done()
                        if msg is None:
                            break

                    audio = await self.audio_q.get()
                    self.audio_q.task_done()

                    # 16000Hzに変換
                    if self.sample_rate != 16000:
                        gcd = np.gcd(self.sample_rate, 16000)
                        up = 16000 // gcd
                        down = self.sample_rate // gcd
                        audio = resample_poly(audio, up, down)

                    buffer = np.concatenate([buffer, audio.astype(np.float32)])

                    while len(buffer) >= self.frame_size:
                        block = buffer[:self.frame_size]
                        buffer = buffer[self.frame_size:]
                        await self.block_q.put(block)
                        block_multi_q.put_nowait(block)

        except asyncio.CancelledError:
            raise

        except Exception as e:
            print(f"audio_inputエラー: {e}")

        finally:
            await self.block_q.put(None)


    async def silero_vad(self, speech_q: asyncio.Queue) -> None:
        speaking = False

        try:
            while True:
                block = await self.block_q.get()
                self.block_q.task_done()

                if block is None:
                    break

                event = self.iter(block)

                if event is not None:
                    if "start" in event:
                        speaking = True
                        await speech_q.put(block)

                    if "end" in event:
                        speaking = False
                        await speech_q.put(block)
                        await speech_q.put(False)

                if speaking:
                    await speech_q.put(block)

        except asyncio.CancelledError:
            raise

        except Exception as e:
            print(f"silero_vadエラー: {e}")

        finally:
            pass