import re
import asyncio
from queue import Queue
from typing import Text

# 自作関数
from .engines import AivisSpeech



class Text_Division:
    def __init__(self, tts_q: asyncio.Queue):
        self.tts_q = tts_q
        self.before_text = ""
        self.pattern = r"(！？|？！|⁉|。|！|？|!|\?|\n)"


    async def div(self) -> Text:
        while True:
            match = re.search(self.pattern, self.before_text)

            if match:
                last_chara = match.end()
                out_text = self.before_text[:last_chara]
                self.before_text = self.before_text[last_chara:]
                return out_text

            self.before_text += await self.tts_q.get()



class TTS_Core:
    def __init__(self, tts_q: asyncio.Queue, wav_q: Queue):
        self.div = Text_Division(tts_q)
        self.aivis = AivisSpeech()
        self.wav_q = wav_q

        # Debug
        # self.i = 0


    async def output(self) -> None:
        text = await self.div.div()
        r_json = await self.aivis.r_json(text)
        r_wav = await self.aivis.r_wav(r_json)
        self.wav_q.put_nowait(r_wav)

        # Debug
        # from src.config import TTS_SRC_PATH
        # self.i += 1
        # with open(f"{TTS_SRC_PATH}/output_waves/output{self.i}.wav", "wb") as f:
        #     f.write(r_wav)


    async def core(self):
        try:
            while True:
                await self.output()

        except asyncio.CancelledError:
            raise



if __name__ == "__main__":
    from src.globals import Globals_Var

    gv = Globals_Var()
    tc = TTS_Core(gv.tts_q, gv.wav_q)

    async def main():
        gv.tts_q.put_nowait(
            "窓の外で、静かに夜が明けていく。"
            "遥か彼方の星から届いたデータが、今、画面の上で緑色に明滅している。"
            "「準備は、すべて整いました」"
            "人工知能は、少しだけ誇らしげに、そう呟いた。"
            "新しい旅が、ここから始まる。"
        )

        await tc.core()


    try:
        print("開始")
        asyncio.run(main())

    except KeyboardInterrupt:
        print("終了")