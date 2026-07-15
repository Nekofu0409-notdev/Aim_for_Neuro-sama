import asyncio
import numpy as np
import sounddevice as sd
import io
import wave
import re
import httpx

#自作関数
from src.config import (
    AIVISSPEECH_PORT,
    AIVIS_SPEAKER,
    AIVIS_SPEED,

    AUDIO_OUTPUT_ID,
)



class Div_Texts():
    def __init__(self):
        self.div_texts = asyncio.Queue()



class Division():
    def __init__(self, globals_var, dt):
        self.before_text = ""
        self.globals = globals_var
        self.dt = dt


    async def loop_div(self):

        try:
            while True:
                self.before_text += await self.globals.tts_queue.get()
                self.globals.tts_queue.task_done()

                pattern = r"(！？|？！|⁉|。|！|？|!|\?|\n)"

                while True:
                    match = re.search(pattern, self.before_text)
                    if not match:
                        break

                    last_chara = match.end()
                    out_text = self.before_text[:last_chara]
                    self.before_text = self.before_text[last_chara:]

                    await self.dt.div_texts.put(out_text)

        except asyncio.CancelledError:
            raise



class AivisSpeech():
    def __init__(self, dt):
        self.aivis_port = f"http://localhost:{AIVISSPEECH_PORT}"
        self.speaker = AIVIS_SPEAKER
        self.speed = AIVIS_SPEED

        self.dt = dt
        self.out_jsons = asyncio.Queue()
        self.out_wavs = asyncio.Queue()

        self.task1 = None
        self.task2 = None

        self.client = httpx.AsyncClient()


    async def aivis_query(self, text):
        self.aivis_query_port = f"{self.aivis_port}/audio_query"
        out_text = text

        if out_text:

            params = {
                "speaker": self.speaker,
                "text": out_text,
            }

            response = await self.client.post(
                self.aivis_query_port, 
                params = params,
                timeout = 20,
            )

            if response.status_code == 200:
                query_data = response.json()
                return query_data

            else:
                print("サーバとの接続に失敗しました")


    async def aivis_wav(self, query_json):
        self.aivis_wav_port = f"{self.aivis_port}/synthesis"
        out_json = query_json

        if out_json:
            
            out_json["speedScale"] = self.speed
            params = {
                "speaker": self.speaker
            }

            response = await self.client.post(
                url = self.aivis_wav_port,
                params = params,
                json = out_json,
                timeout = 60,
            )

            if response.status_code == 200:
                return response.content
            
            else:
                print("サーバとの接続に失敗しました")


#下記の関数は、
#それぞれを別枠として起動させるためのもの
    async def output_json(self):
        try:
            while True:
                div_text = await self.dt.div_texts.get()
                self.dt.div_texts.task_done()

                out_json = await self.aivis_query(div_text)
                await self.out_jsons.put(out_json)
        
        except asyncio.CancelledError:
            raise


    async def output_wav(self):
        try:
            while True:
                out_json = await self.out_jsons.get()
                self.out_jsons.task_done()

                out_wav = await self.aivis_wav(out_json)
                await self.out_wavs.put(out_wav)

        except asyncio.CancelledError:
            raise



class Audio_Play():
    def __init__(self):
        self.id = AUDIO_OUTPUT_ID


    async def play_wav(self, wav):
        out_wav = wav

        if out_wav:
            try:
                wav_stream = io.BytesIO(out_wav)

                with wave.open(wav_stream, "rb") as wf:
                    f = wf.getframerate()
                    channels = wf.getnchannels()

                    audio_data = np.frombuffer(
                        wf.readframes(wf.getnframes()),
                        dtype=np.int16,
                    )

                    if channels == 2:
                        audio_data = audio_data.reshape(-1, 2)

                    sd.play(audio_data, f, device = self.id)

                while sd.get_stream().active:
                    await asyncio.sleep(0.1)

            finally:
                sd.stop()



class Run_TTS():
    def __init__(self, globals_var):
        #グローバルもどき(Run_TTS内のみ)
        self.dt = Div_Texts()

        self.d = Division(globals_var, self.dt)
        self.aivs = AivisSpeech(self.dt)
        self.ap = Audio_Play()


    async def aivis_loop(self):
        try:
            asyncio.create_task(self.aivs.output_json())
            asyncio.create_task(self.aivs.output_wav())
            asyncio.create_task(self.d.loop_div())

            while True:
                out_wav = await self.aivs.out_wavs.get()
                self.aivs.out_wavs.task_done()
                await self.ap.play_wav(out_wav)

        except asyncio.CancelledError:
            raise



if __name__ == "__main__":
    from src.globals import G_Var

    async def main():
        #グローバル変数もどき
        gv = G_Var()

        rt = Run_TTS(gv)

        await gv.tts_queue.put(
            "窓の外で、静かに夜が明けていく。"
            "遥か彼方の星から届いたデータが、今、画面の上で緑色に明滅している。"
            "「準備は、すべて整いました」"
            "人工知能は、少しだけ誇らしげに、そう呟いた。"
            "新しい旅が、ここから始まる。"
        )

        await rt.aivis_loop()


    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print("終了")

    except Exception as e:
        print(e)