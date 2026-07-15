import torch
from os.path import join
from multiprocessing import Queue

from rx.core import Observer
from typing import Union, Tuple
from pyannote.core import Annotation

from diart.sources import AudioSource
from diart import SpeakerDiarization, SpeakerDiarizationConfig
from diart.inference import StreamingInference
import diart.models as m

# 自作関数
from src.config import STT_MODELS



# diart処理(multiprocess)
# Queueから音声を取るための自前クラス
class QueueAudioSource(AudioSource):
    def __init__(self, q: Queue, uri = "dummy", sample_rate = 16000):
        super().__init__(uri, sample_rate)
        self.q = q


    def read(self) -> None:
        try:
            while True:
                audio = self.q.get()

                if audio is None:
                    break

                audio = audio.reshape(1, -1)
                self.stream.on_next(audio)

        except KeyboardInterrupt:
            self.close()

        except Exception as e:
            print(f"diartエラー: {e}")

        finally:
            self.close()


    def close(self):
        self.stream.on_completed()



# 自前オブザーバー
def _extract_prediction(value: Union[Tuple, Annotation]) -> Annotation:
    if isinstance(value, tuple):
        return value[0]
    
    if isinstance(value, Annotation):
        return value
    
    msg = f"Expected tuple or Annotation, but got {type(value)}"
    raise ValueError(msg)


class QueueWriter(Observer):
    def __init__(self, speaker_q: Queue):
        super().__init__()
        self.q = speaker_q


    def on_next(self, value: Union[Tuple, Annotation]) -> None:
        prediction = _extract_prediction(value)
        for _, _, label in prediction.itertracks(yield_label = True):
            self.q.put(label)
            print(label)


    def on_error(self, error: Exception):
        print(f"QueueWriterエラー: {Exception}")


    def on_completed(self):
        pass



def diart(block_multi_q: Queue, speaker_diarization_q: Queue) -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    segmentation = m.SegmentationModel.from_pretrained("pyannote/segmentation-3.0")
    embedding = m.EmbeddingModel.from_pretrained("speechbrain/spkrec-ecapa-voxceleb")

    config = SpeakerDiarizationConfig(
        segmentation = segmentation,
        embedding = embedding,
        device = device,
    )
    pipeline = SpeakerDiarization(config)

    mic = QueueAudioSource(block_multi_q)
    inference = StreamingInference(pipeline, mic, do_plot = False)
    inference.attach_observers(QueueWriter(speaker_diarization_q))

    prediction = inference()