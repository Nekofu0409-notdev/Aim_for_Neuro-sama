import os
def force_copy_symlink(src, dst, target_is_directory = False):
    import shutil
    if target_is_directory:
        shutil.copytree(src, dst)
    else:
        shutil.copy2(src, dst)
os.symlink = force_copy_symlink

import asyncio
from multiprocessing import Process, Queue

# 自作関数
from .mic import Audio_VAD
from .diart import diart
from .speech_create import Speech_Create



class Run_STT():
    def __init__(self, globals_var):
        self.av = Audio_VAD()
        self.sc = Speech_Create()
        
        self.fin_q = asyncio.Queue()
        self.fin_audio = asyncio.Queue()
        self.fin_return = asyncio.Queue()


    async def fin(self):
        await self.fin_q.put(None)
        await self.fin_return.get()


    async def debug(self, speech_finalize_q: asyncio.Queue):
        import soundfile as sf
        i = 0

        try:
            while True:
                i += 1
                speech = await speech_finalize_q.get()
                
                if speech is None:
                    break

                sf.write(fr"src\voice\stt_src\output_waves\test{i}.wav", speech, 16000)
            
        except asyncio.CancelledError:
            raise

        except Exception as e:
            print(f"stt_core_debugエラー: {e}")

        finally:
            pass


    async def diart_run(self):
        block_multi_q = Queue()
        speech_q = asyncio.Queue()
        speaker_diarization_q = Queue()
        speech_finalize_q = asyncio.Queue()

        audio_task = asyncio.create_task(
            self.av.audio_input(block_multi_q, self.fin_audio)
        )
        vad_task = asyncio.create_task(
            self.av.silero_vad(speech_q)
        )
        p = Process(
            target = diart,
            args = (block_multi_q, speaker_diarization_q),
            daemon = True,
        )
        p.start()
        finalize_task = asyncio.create_task(
            self.sc.create(speech_q, speaker_diarization_q, speech_finalize_q,)
        )

        # debug
        debug_task = asyncio.create_task(
            self.debug(speech_finalize_q,)
        )

        try:
            while True:
                if not self.fin_q.empty():
                    msg = await self.fin_q.get()
                    self.fin_q.task_done()

                    if msg is None:
                        await self.fin_audio.put(None)
                        block_multi_q.put_nowait(None)
                        await speech_q.put(None)
                        await speech_finalize_q.put(None)
                        break

                await asyncio.sleep(0.1)

        except asyncio.CancelledError:
            raise

        except Exception as e:
            print(f"STT実行エラー: {e}")

        finally:
            await audio_task
            await vad_task
            p.join()
            await finalize_task

            # debug
            await debug_task

            print("終了")
            await self.fin_return.put(None)



class Debug():
    def __init__(self, globals_var):
        self.gv = globals_var
        self.rs = Run_STT(self.gv)


    async def speaker_i(self):
        try:
            await self.rs.diart_run()

        except asyncio.CancelledError:
            raise



if __name__ == "__main__":
    from src.globals import G_Var

    gv = G_Var()

    try:
        print("開始")
        asyncio.run(Debug(gv).speaker_i())

    except KeyboardInterrupt:
        print("終了")