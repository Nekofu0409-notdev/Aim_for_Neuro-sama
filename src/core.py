import asyncio

#自作関数
from src.config import STT, TTS, confirm
from src.globals import Global_Var
from src.llm import LLM_Core
from src.memory import short_clear
from src.voice import STT_Core, TTS_Core


async def main():
    if not confirm():
        return

    #グローバル変数もどき
    gv = Global_Var()
    llm = LLM_Core(gv.stt_q, gv.tts_q)

    try:
        tasks = [llm.core()]

        if STT:
            stt = STT_Core(gv.vad_q, gv.stt_q, llm, gv.wav_q)
            tasks.append(stt.core())
        if TTS:
            tts = TTS_Core(gv.tts_q, gv.wav_q)
            tasks.append(tts.core())

        await asyncio.gather(*tasks)

    finally:
        short_clear()



if __name__ == "__main__":
    try:
        asyncio.run(main(), debug = False)

    except KeyboardInterrupt:
        print("終了")
