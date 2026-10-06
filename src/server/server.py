import asyncio
import subprocess

#自作関数
from src.config import (
    GPU_LAYERS,
    KOBOLD_EXE_PATH,
    LLM_HOST,
    LLM_MODEL_PATH,
    LLM_PORT,
    STT_EXE_PATH,
    TTS_EXE_PATH,
    TTS_PORT,
)


class OpenAI_Server:
    def __init__(self):
        self.process = None


    async def start(self):
        cmd = [
            KOBOLD_EXE_PATH,
            "--model", LLM_MODEL_PATH,
            "--contextsize", "16384",
            "--smartcache",
            "--port", LLM_PORT,
            "--host", LLM_HOST,
            "--gpulayers", GPU_LAYERS,
            "--gendefaults", '{"max_tokens":4096}',
            "--usevulkan",
        ]

        self.process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW,
            # デバッグ用
            # creationflags = subprocess.CREATE_NEW_CONSOLE | subprocess.CREATE_NEW_PROCESS_GROUP,
            # stdout=None,
            # stderr=None,
        )


    def stop(self):
        if self.process:
            subprocess.run([
                "taskkill", "/PID", str(self.process.pid), "/T", "/F"],
                check=False
            )



class STT_Server:
    def __init__(self):
        self.process = None


    async def start(self):
        cmd = [
            STT_EXE_PATH,
            "--config", "server.json"
        ]

        self.process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW,
            # デバッグ用
            # creationflags = subprocess.CREATE_NEW_CONSOLE | subprocess.CREATE_NEW_PROCESS_GROUP,
            # stdout=None,
            # stderr=None,
        )


    def stop(self):
        if self.process:
            subprocess.run([
                "taskkill", "/PID", str(self.process.pid), "/T", "/F"],
                check=False
            )



class TTS_Server:
    def __init__(self):
        self.process = None


    async def start(self):
        cmd = [
            TTS_EXE_PATH,
            "--use_gpu",
            "--port", TTS_PORT,
        ]

        self.process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW,
            # デバッグ用
            # creationflags = subprocess.CREATE_NEW_CONSOLE | subprocess.CREATE_NEW_PROCESS_GROUP,
            # stdout=None,
            # stderr=None,
        )


    def stop(self):
        if self.process:
            subprocess.run([
                "taskkill", "/PID", str(self.process.pid), "/T", "/F"],
                check=False
            )



if __name__ == "__main__":
    async def debug():
        oas = OpenAI_Server()
        ss = STT_Server()
        ts = TTS_Server()

        await oas.start()
        await ss.start()
        await ts.start()

        await asyncio.sleep(60)

        oas.stop()
        ss.stop()
        ts.stop()

    asyncio.run(debug())
