import logging

logger = logging.getLogger(__name__)

import asyncio
import json
import subprocess
from pathlib import Path

#自作関数
from src.config import (
    BASE_DIR,
    JUDGE_GPU_LAYERS,
    JUDGE_LLM_HOST,
    JUDGE_LLM_MODEL,
    JUDGE_LLM_PORT,
    JUDGE_STT_MODEL,
    JUDGE_STT_PORT,
    KOBOLD_EXE_PATH,
    LLM_GPU_LAYERS,
    LLM_HOST,
    LLM_MODEL,
    LLM_PORT,
    STT_EXE_PATH,
    STT_MODEL,
    STT_PORT,
    TTS_EXE_PATH,
    TTS_PORT,
    VLM_GPU_LAYERS,
    VLM_HOST,
    VLM_MMPROJ,
    VLM_MODEL,
    VLM_PORT,
)

LLM_MODEL_PATH = BASE_DIR / "models" / "LLM_models" / LLM_MODEL
JUDGE_LLM_MODEL_PATH = BASE_DIR / "models" / "LLM_models" / JUDGE_LLM_MODEL
STT_MODEL_PATH = BASE_DIR / "models" / "STT_models" / "audio_cpp" / "models" / STT_MODEL
STT_DIR = STT_EXE_PATH.parents[1]
VLM_MODEL_PATH = BASE_DIR / "models" / "VLM_models" / VLM_MODEL
VLM_MMPROJ_PATH = BASE_DIR / "models" / "VLM_models" / VLM_MMPROJ

STT_MAIN_CONFIG = {
    "host": "127.0.0.1",
    "port": int(STT_PORT),
    "backend": "vulkan",
    "device": 0,
    "threads": 1,
    "lazy_load": False,
    "models": [
        {
            "id": "qwen3-asr",
            "family": "qwen3_asr",
            "path": f"./models/{STT_MODEL}",
            "task": "asr",
            "mode": "offline",
        }
    ],
}

STT_STREAMING_CONFIG = {
    **STT_MAIN_CONFIG,
    "port": int(JUDGE_STT_PORT),
    "models": [
        {
            "id": "qwen3-asr",
            "family": "qwen3_asr",
            "path": f"./models/{JUDGE_STT_MODEL}",
            "task": "asr",
            "mode": "offline",
        }
    ],
}


def _kill_tree(pid: int) -> None:
    result = subprocess.run(
        ["taskkill", "/PID", str(pid), "/T", "/F"],
        capture_output=True,
        text=True,
        check=False,
    )

    for line in (result.stdout or "").splitlines():
        logger.info("%s", line)

    for line in (result.stderr or "").splitlines():
        logger.warning("%s", line)



class OpenAI_Server:
    def __init__(self):
        self.process1 = None
        self.process2 = None
        self.process3 = None


    async def start_main(self):
        cmd = [
            KOBOLD_EXE_PATH,
            "--model", LLM_MODEL_PATH,
            "--contextsize", "16384",
            "--smartcache",
            "--port", LLM_PORT,
            "--host", LLM_HOST,
            "--gpulayers", LLM_GPU_LAYERS,
            "--gendefaults", '{"max_tokens":4096}',
            "--usevulkan",
        ]

        self.process1 = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )


    def stop_main(self):
        if self.process1:
            _kill_tree(self.process1.pid)


    async def start_judge(self):
        cmd = [
            KOBOLD_EXE_PATH,
            "--model", JUDGE_LLM_MODEL_PATH,
            "--contextsize", "4096",
            "--smartcache",
            "--port", JUDGE_LLM_PORT,
            "--host", JUDGE_LLM_HOST,
            "--gpulayers", JUDGE_GPU_LAYERS,
            "--gendefaults", '{"max_tokens":128}',
            "--usevulkan",
        ]

        self.process2 = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )


    def stop_judge(self):
        if self.process2:
            _kill_tree(self.process2.pid)


    async def start_vision(self):
        cmd = [
            KOBOLD_EXE_PATH,
            "--model", VLM_MODEL_PATH,
            "--mmproj", VLM_MMPROJ_PATH,
            "--contextsize", "8192",
            "--smartcache",
            "--port", VLM_PORT,
            "--host", VLM_HOST,
            "--gpulayers", VLM_GPU_LAYERS,
            "--gendefaults", '{"max_tokens":512}',
            "--usevulkan",
        ]

        self.process3 = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )


    def stop_vision(self):
        if self.process3:
            _kill_tree(self.process3.pid)



class STT_Server:
    def __init__(self):
        self.process1 = None
        self.process2 = None
        self.config1 = None
        self.config2 = None

    @staticmethod
    def _write_config(config: dict, filename: str) -> Path:
        path = STT_DIR / filename
        path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
        return path


    @staticmethod
    def _remove_config(path: Path | None):
        if path is None:
            return
        try:
            path.unlink(missing_ok=True)
        except OSError:
            pass


    async def start_main(self):
        self.config1 = self._write_config(STT_MAIN_CONFIG, "server1.json")
        cmd = [
            STT_EXE_PATH,
            "--config", str(self.config1),
        ]

        self.process1 = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )


    def stop_main(self):
        if self.process1:
            _kill_tree(self.process1.pid)
        self._remove_config(self.config1)


    async def start_judge(self):
        self.config2 = self._write_config(STT_STREAMING_CONFIG, "server2.json")
        cmd = [
            STT_EXE_PATH,
            "--config", str(self.config2),
        ]

        self.process2 = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )


    def stop_judge(self):
        if self.process2:
            _kill_tree(self.process2.pid)
        self._remove_config(self.config2)



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
        )


    def stop(self):
        if self.process:
            _kill_tree(self.process.pid)



if __name__ == "__main__":
    pass
