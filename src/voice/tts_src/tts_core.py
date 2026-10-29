import asyncio
import re
from queue import Queue

# 自作関数
from .engines import AivisSpeech


class Text_Division:
    def __init__(self, tts_q: asyncio.Queue):
        self.id = None
        self.tts_q = tts_q
        self.before_text = ""
        self.pattern = r"(！？|？！|⁉|。|！|？|!|\?|\n)"


    async def div(self) -> tuple[object, str, str]:
        while True:
            match = re.search(self.pattern, self.before_text)

            if match:
                last_chara = match.end()
                out_text = self.before_text[:last_chara]
                self.before_text = self.before_text[last_chara:]
                return (self.id, "assistant", out_text)

            self.id, role, text = await self.tts_q.get()

            if role == "assistant":
                self.before_text += text

            elif role == "system":
                return (self.id, "system", text)



class TTS_Core:
    def __init__(self, tts_q: asyncio.Queue, wav_q: asyncio.Queue):
        self.div = Text_Division(tts_q)
        self.aivis = AivisSpeech()
        self.wav_q = wav_q
        self.task = None


    async def _turn_control(self, id: object, role: str, text: str):
        if role == "assistant":
            r_wav = await self.aivis.r_wav(text)
            self.wav_q.put_nowait((id, r_wav))

        elif role == "system":
            self.wav_q.put_nowait((id, text))


    async def output(self) -> None:
        id, role, text = await self.div.div()

        if self.task is not None:
            await self.task

        self.task = asyncio.create_task(self._turn_control(id, role, text))


    async def core(self):
        try:
            while True:
                await self.output()

        except asyncio.CancelledError:
            await self.aivis.aclose()



if __name__ == "__main__":
    from src.globals import Global_Var

    gv = Global_Var()
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
