import os
import math
import numpy as np
import asyncio
import sounddevice as sd
from multiprocessing import Process, Queue

from scipy.signal import resample_poly
from scipy.spatial.distance import cosine
import librosa
from silero_vad import load_silero_vad, VADIterator
import sherpa_onnx
from moonshine_voice import MicTranscriber, TranscriptEventListener, ModelArch

#自作関数
from src.config import (
    BASE_DIR,

    STT_MODELS,
    SHERPA_SEG,
    SHERPA_REC,

    MOONSHINE,
    MOONSHINE_PATH,
    MOONSHINE_ARCH,

    QWENASR,

    AUDIO_INPUT_ID,
)



# VAD処理
class Audio_VAD():
    def __init__(self):
        self.id = AUDIO_INPUT_ID

        device_info = sd.query_devices(self.id, 'input')
        self.sample_rate = int(device_info['default_samplerate'])
        self.block_size = math.ceil(512 * (self.sample_rate / 16000))
        
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


    async def silero_vad(self, speech_q):
        speaking = False
        buffer = []

        try:
            while True:
                block = await self.block_q.get()
                self.block_q.task_done()

                event = self.iter(block)

                if event is not None:
                    print(event)

                    if "start" in event:
                        speaking = True
                        buffer = [block]

                    if "end" in event:
                        buffer.append(block)
                        speech = np.concatenate(buffer)
                        buffer = []
                        speaking = False
                        await speech_q.put(speech)

                if speaking:
                    buffer.append(block)

        except asyncio.CancelledError:
            raise



# embedding処理
class Sherpa_Onnx():
    def __init__(self):
        self.segmentation_model = SHERPA_SEG
        self.embedding_extractor_model = SHERPA_REC

        self.config = sherpa_onnx.OfflineSpeakerDiarizationConfig(
            segmentation = sherpa_onnx.OfflineSpeakerSegmentationModelConfig(
                pyannote = sherpa_onnx.OfflineSpeakerSegmentationPyannoteModelConfig(
                    model = self.segmentation_model
                ),
            ),
            embedding = sherpa_onnx.SpeakerEmbeddingExtractorConfig(
                model = self.embedding_extractor_model
            ),
            clustering = sherpa_onnx.FastClusteringConfig(
                num_clusters = -1,
                threshold = 0.3,
            ),
            min_duration_on = 0,
            min_duration_off = 0.1,
        )

        self.sd = sherpa_onnx.OfflineSpeakerDiarization(self.config)


def sherpa_dia(speech_q, result_q):

    so = Sherpa_Onnx()

    try:
        while True:
            speech = speech_q.get()
            result = so.sd.process(speech).sort_by_start_time()

            for r in result:
                print(f"{r.start:.3f} -- {r.end:.3f} speaker_{r.speaker:02}")
                result_q.put(f"{r.start:.3f} -- {r.end:.3f} speaker_{r.speaker:02}")

    except KeyboardInterrupt:
        pass



class MFCC_Embedding():
    def __init__(self):
        self.threshold = 0.20

        self.frame_ms = 32
        self.frame_size = int(16000 / 1000 * self.frame_ms)
        self.hop_ms = 16
        self.hop_size = int(16000 / 1000 * self.hop_ms)

        self.prev_speech = None


    async def speech_separate(self, speech):
        mfcc = librosa.feature.mfcc(
            y = speech,
            sr = 16000,
            n_mfcc = 13,
            n_fft = self.frame_size,
            hop_length = self.hop_size,
        )

        delta = librosa.feature.delta(mfcc)
        delta2 = librosa.feature.delta(mfcc, order=2)

        mfcc_all = np.vstack([mfcc, delta, delta2])

        speech_frames = mfcc_all.shape[1]
        change_points = []

        for i in range(speech_frames):
            new_speech = mfcc[:, i]

            if self.prev_speech is None:
                self.prev_speech = new_speech
            
            else:
                dist = cosine(self.prev_speech, new_speech)
                print(dist)

                if dist > self.threshold:
                    change_points.append((i + 1) * self.hop_ms / 1000)
                    self.prev_speech = new_speech

                else:
                    self.prev_speech = self.prev_speech * 0.98 + new_speech * 0.02

        return change_points



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
        self.me = MFCC_Embedding()

        self.ms = Moonshine()
        self.qa = Qwen3_ASR()

        self.speech_q = asyncio.Queue()


    async def sherpa_run(self):
        # デバッグ用
        import soundfile as sf
        i = 0

        speech_sherpa_q = Queue()
        result_sherpa_q = Queue()

        asyncio.create_task(self.av.audio_input())
        asyncio.create_task(self.av.silero_vad(self.speech_q))

        p = Process(
            target = sherpa_dia,
            args = (speech_sherpa_q, result_sherpa_q)
        )
        p.start()

        try:
            while True:
                speech = await self.speech_q.get()

                # デバッグ用
                i += 1
                sf.write(fr"src\voice\output_waves\test{i}.wav", speech, 16000)

                await asyncio.to_thread(speech_sherpa_q.put, speech)
                result = await asyncio.to_thread(result_sherpa_q.get)

        except asyncio.CancelledError:
            raise


    async def separate_run(self):
        # デバッグ用
        import soundfile as sf
        i = 0

        change_points = []

        asyncio.create_task(self.av.audio_input())
        asyncio.create_task(self.av.silero_vad(self.speech_q))

        try:
            while True:
                speech = await self.speech_q.get()

                # デバッグ用
                i += 1
                sf.write(fr"src\voice\output_waves\test{i}.wav", speech, 16000)

                change_points = await self.me.speech_separate(speech)
                print(change_points)

        except asyncio.CancelledError:
            raise



class Debug():
    def __init__(self, globals_var):
        self.gv = globals_var
        self.rs = Run_STT(self.gv)


    async def speaker_i(self):
        print("開始")

        try:
            await self.rs.sherpa_run()

        except asyncio.CancelledError:
            raise



if __name__ == "__main__":
    from src.globals import G_Var

    gv = G_Var()

    try:
        asyncio.run(Debug(gv).speaker_i())

    except KeyboardInterrupt:
        print("終了")