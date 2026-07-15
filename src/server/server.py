from os.path import join
import asyncio
import atexit
import subprocess
import signal

#自作関数
from src.config import (
    LLM_PORT,
    LLM_MODEL,
    LLMSERVER_FILE_PATH,
    LLM_HOST,

    AIVISSPEECH,
    AIVIS_EXE,
    AIVISSPEECH_PORT,

    TTS,
)



class OpenAI_Server():
    def __init__(self):
        self.exe_path = join(LLMSERVER_FILE_PATH, "koboldcpp", "koboldcpp.exe")
        self.port = LLM_PORT
        self.model_path = join(LLMSERVER_FILE_PATH, "LLM_models", LLM_MODEL)
        self.process = None

        if LLM_HOST:
            self.host = "0.0.0.0"
        else:
            self.host = "localhost"


    async def start(self):
        cmd = [
            self.exe_path,
            "--model", self.model_path,
            "--contextsize", "16384",
            "--gpulayers", "0",
            "--smartcache",
            "--port", self.port,
            "--host", self.host,
            "--multiuser",
            "--gendefaults", '{"max_tokens":4096}'
        ]
        
        self.process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout = subprocess.DEVNULL,
            stderr = subprocess.DEVNULL,
            creationflags = subprocess.CREATE_NO_WINDOW,
            # デバッグ用
            # creationflags = subprocess.CREATE_NEW_CONSOLE | subprocess.CREATE_NEW_PROCESS_GROUP,
        )
        
        atexit.register(self.stop)

    
    def stop(self):
        if self.process:
            subprocess.run([
                "taskkill",
                "/PID", str(self.process.pid),
                "/T",
                "/F"
            ])



class AivisSpeech_Server():
    def __init__(self):
        self.exe_path = AIVIS_EXE
        self.port = AIVISSPEECH_PORT
        self.process = None


    async def start(self):
        cmd = [
            self.exe_path,
            "--use_gpu",
            "--port", self.port,
        ]
        
        self.process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout = subprocess.DEVNULL,
            stderr = subprocess.DEVNULL,
            creationflags = subprocess.CREATE_NO_WINDOW,
            # デバッグ用
            # creationflags = subprocess.CREATE_NEW_CONSOLE | subprocess.CREATE_NEW_PROCESS_GROUP,
        )
        
        atexit.register(self.stop)

    
    def stop(self):
        if self.process:
            subprocess.run([
                "taskkill",
                "/PID", str(self.process.pid),
                "/T",
                "/F"
            ])



class All_Run():
    def __init__(self):
        self.oas = OpenAI_Server()
        self.ass = AivisSpeech_Server()

        self.aivis = AIVISSPEECH
        self.tts = TTS

    async def run(self):
        await self.oas.start()

        if self.tts:
            if self.aivis:
                await self.ass.start()



class Debug():
    def __init__(self):
        self.oas = OpenAI_Server()
        self.ass = AivisSpeech_Server()

    async def openai(self):
        await self.oas.start()
        await asyncio.sleep(20)

    async def aivis(self):
        await self.ass.start()
        await asyncio.sleep(20)



if __name__ == "__main__":
    asyncio.run(Debug().openai())