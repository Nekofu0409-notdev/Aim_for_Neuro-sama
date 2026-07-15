#main.py

import asyncio
import os
import atexit

#必要ファイルの存在有無
from py.config.need_create import Prepare_Run

pr = Prepare_Run()
pr.run()

#自作関数
from py.llm.call_llm import Call_LLM
from py.memory.short_memory import Short_Memory
from py.memory.middle_memory import Middle_Memory
from py.config.confirm import Confirm_Run
from py.config.return_env import *
from py.voice.tts import Run_TTS
from py.globals.global_var import *


#main関数
async def main():
    #確認
    cr = Confirm_Run()
    confirm_bool = cr.run()

    if confirm_bool:

        #サーバの起動、確認

        if conf_task:
            sm = Short_Memory()
            mm = Middle_Memory()

            try:
                sm.short_clear()

                #消去する必要なし
                #mm.middle_clear()

                #グローバル変数もどき
                gv = Globals_Var()

                #LLMとかTTSとか
                cl = Call_LLM(gv)
                rt = Run_TTS(gv)
                rs = Run_STT(gv)

                tasks = []

                # TTSが増えてきたら用改造
                if TTS:
                    tasks.append(asyncio.create_task(rt.aivis_loop()))

                if STT:
                    await rs.stt_run()
                    tasks.append(asyncio.create_task(cl.call_llm_stt()))

                else:
                    tasks.append(asyncio.create_task(cl.call_llm_keyboard()))

                try:
                    results = await asyncio.gather(*tasks)
                except (asyncio.CancelledError, KeyboardInterrupt):
                    pass

            except KeyboardInterrupt:
                print("\n終了")

            except Exception as e:
                print(f"\n予期せぬエラー: {e}")

            finally:
                #短期記憶、サーバの消去
                sm.short_clear()
                ba.kill_bat()

                #消去する必要なし
                #mm.middle_clear()

        else:
            ba.kill_bat()



#実行
if __name__ == "__main__":
    asyncio.run(main(), debug = False)