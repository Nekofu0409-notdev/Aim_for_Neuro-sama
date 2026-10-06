import json
import os

from dotenv import load_dotenv

#自作関数
from .return_path import BASE_DIR, ENV_PATH

load_dotenv(ENV_PATH, override=True, verbose=True)


# 基本
LLM_MODEL = os.environ.get("LLM_model", "please_set")
LLM_PORT = os.environ.get("LLM_port", "9001")
LLM_HOST = os.environ.get("LLM_host", "localhost")
GPU_LAYERS = os.environ.get("GPU_layers", "-1")

TOP_K = int(os.environ.get("top_k", "5"))


# 音声認識
STT = json.loads(os.environ.get("STT", "false").lower())
STT_MODEL = os.environ.get("STT_model", "please_set")
STT_PORT = os.environ.get("STT_port", "40610")


# Discord関連
TOKEN = os.environ.get("Token", "please_set")


# 音声合成
TTS = json.loads(os.environ.get("TTS", "false").lower())
TTS_PORT = os.environ.get("TTS_port", "41715")
TTS_SPEAKER = os.environ.get("TTS_speaker", "1878365378")
TTS_SPEED = os.environ.get("TTS_speed", "1.3")


# path
LLM_MODEL_PATH = BASE_DIR / "models" / "LLM_server_models" / "LLM_models" / LLM_MODEL
STT_MODEL_PATH = BASE_DIR / "models" / "STT_models" / "audio_cpp" / "models" / STT_MODEL
