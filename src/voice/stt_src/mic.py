import time
import asyncio
import numpy as np
from os.path import join
from scipy.io import wavfile
from silero_vad import load_silero_vad, VADIterator

# 自作関数
from .inference import predict_endpoint
from src.config import STT_SRC

RATE = 16000
THRETHOLD = 0.5
SILENCE_DURATION = 200
PAD = 100
CHUNK = 512



def _process_segment(segment_audio_f32: np.ndarray):
    i += 1
    wavfile.write(
        join(STT_SRC, "output_waves", f"sample{i}.wav"),
        RATE,
        (segment_audio_f32 * 32767.0).astype(np.int16)
    )

    dur_sec = segment_audio_f32.size / RATE
    print(f"Processing segment ({dur_sec:.2f}s)...")

    t0 = time.perf_counter()
    result = predict_endpoint(segment_audio_f32)  # expects 16 kHz float32 mono
    dt_ms = (time.perf_counter() - t0) * 1000.0

    pred = result.get("prediction", 0)
    prob = result.get("probability", float("nan"))

    print("--------")
    print(f"Prediction: {'Complete' if pred == 1 else 'Incomplete'}")
    print(f"Probability of complete: {prob:.4f}")
    print(f"Inference time: {dt_ms:.2f} ms")



class silero_VAD:
    def __init__(self, audio: asyncio.Queue):
        self.audio = audio

        self.model = load_silero_vad(onnx = True)
        self.iter = VADIterator(
            self.model,
            threshold = THRETHOLD,
            sampling_rate = RATE,
            min_silence_duration_ms = SILENCE_DURATION,
            speech_pad_ms = PAD,
            )
        
        
    async def predict_turn(self) -> None:
        speaking = False
        buffer = []

        try:
            while True:
                try:
                    f32 = self.audio.get_nowait()
                except asyncio.QueueEmpty:
                    f32 = np.zeros(CHUNK, dtype = np.float32)
                
                # None -> fin
                if f32 is None:
                    break

                event = self.iter(f32)

                if event is not None:
                    if "start" in event:
                        speaking = True

                    if "end" in event:
                        speaking = False
                        buffer.append(f32)
                        _process_segment(np.concatenate(buffer, dtype = np.float32))
                        buffer.clear()

                if speaking:
                    buffer.append(f32)

        except asyncio.CancelledError:
            raise

        except Exception as e:
            print(f"predict_turnエラー: {e}")

        finally:
            pass



if __name__ == "__main__":
    pass