import asyncio
from typing import Text
import numpy as np
from multiprocessing import Queue
from queue import Empty
from collections import deque



class Speech_Create():
    def __init__(self):
        self.counts = [0, 0, 0]
        self.judge = ("doubt", "continue", "tentchange")
        self.tentative = None

        # 1frame = 32ms
        self.delay_frame = 5
        self.frames = deque()


    def count_speaker(self, label) -> Text:
        idx = int(label[-1])

        # カウント追加
        for i, count in enumerate(self.counts):
            if i == idx:
                self.counts[i] = min(count + 1, 3)
            else:
                self.counts[i] = max(count - 1, 0)

        # returnを確定
        for i, count in enumerate(self.counts):
            if count == 3:
                if self.tentative == i:
                    print(self.judge[1])
                    return self.judge[1]
                else:
                    self.tentative = i
                    print(self.judge[2])
                    return self.judge[2]
        
        print(self.judge[0])
        return self.judge[0]
        

    def speech_split(self, speech: np.ndarray, buffer: list, state: Text) -> np.ndarray:
        finalize = None

        if state == self.judge[0]:
            buffer[1].append(speech)
            return None

        elif state == self.judge[1]:
            if buffer[1]:
                buffer[0].append(np.concatenate(buffer[1]))
                buffer[1].clear()

            buffer[0].append(speech)
            return None
        
        elif state == self.judge[2]:
            if buffer[0]:
                finalize = np.concatenate(buffer[0])
            
            buffer[0].clear()
            buffer[0].append(np.concatenate(buffer[1]))
            buffer[1].clear()
            return finalize
        

    def delay(self, speech_fast: np.ndarray | bool) -> np.ndarray | bool | None:
        if speech_fast is False:
            if self.frames:
                speech = np.concatenate(self.frames)
                self.frames.clear()
                return speech
            
            return False

        self.frames.append(speech_fast)

        if len(self.frames) > self.delay_frame:
            speech = self.frames.popleft()
            return speech
        
        return None


    async def create(
            self,
            speech_q: asyncio.Queue,
            speaker_diarization_q: Queue,
            speech_finalize_q: asyncio.Queue,
        ) -> None:

        speech = None
        buffer = [[], []]
        speaking = False
        label = None
        judge = None
        finalize = None

        try:
            while True:
                speech_fast = await speech_q.get()

                # 終了を受け取った場合
                if speech_fast is None:
                    break

                # VAD_endを受け取った場合
                if speech_fast is False:
                    speech = self.delay(speech_fast)
                    if speech is not False:
                        buffer[1].append(speech)
                        speech = False
                # 通常
                else:
                    speech = self.delay(speech_fast)

                # 今話し始めた時
                if speaking is False:
                    while True:
                        try:
                            speaker_diarization_q.get_nowait()
                        except Empty:
                            break

                # VADで切り抜いた場所のみ判定
                if speech is None:
                    continue

                elif speech is not False:
                    try:
                        label = speaker_diarization_q.get_nowait()
                    except Empty:
                        label = None

                    if label is not None:
                        judge = self.count_speaker(label)
                        finalize = self.speech_split(speech, buffer, judge)

                        if finalize is not None:
                            await speech_finalize_q.put(finalize)

                    else:
                        buffer[1].append(speech)
                    
                    speaking = True
                
                elif speech is False:
                    if buffer[1]:
                        buffer[0].append(np.concatenate(buffer[1]))

                    if buffer[0]:
                        finalize = np.concatenate(buffer[0])
                        await speech_finalize_q.put(finalize)

                    # 初期化
                    buffer = [[], []]
                    speaking = False
                    self.counts = [0, 0, 0]
                    self.tentative = None

        except asyncio.CancelledError:
            raise

        except Exception as e:
            print(f"Speech_Createエラー: {e}")

        finally:
            pass