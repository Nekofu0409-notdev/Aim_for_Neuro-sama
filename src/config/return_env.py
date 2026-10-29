import os

from dotenv import load_dotenv

#自作関数
from .return_path import ENV_PATH

load_dotenv(ENV_PATH, override=True, verbose=True)


# 基本
LLM_MODEL = os.environ.get("LLM_model", "please_set")
LLM_PORT = os.environ.get("LLM_port", "9001")
LLM_HOST = os.environ.get("LLM_host", "localhost")
LLM_GPU_LAYERS = os.environ.get("GPU_layers", "-1")

JUDGE_LLM_MODEL = os.environ.get("judge_LLM_model", "please_set")
JUDGE_LLM_PORT = os.environ.get("judge_LLM_port", "9002")
JUDGE_LLM_HOST = os.environ.get("judge_LLM_host", "localhost")
JUDGE_GPU_LAYERS = os.environ.get("judge_GPU_layers", "-1")

TOP_K = int(os.environ.get("top_k", "5"))


# 音声認識
STT_MODEL = os.environ.get("STT_model", "please_set")
STT_PORT = os.environ.get("STT_port", "40610")
JUDGE_STT_MODEL = os.environ.get("judge_STT_model", "please_set")
JUDGE_STT_PORT = os.environ.get("judge_STT_port", "40611")


# Discord関連
TOKEN = os.environ.get("Token", "please_set")


# 音声合成
TTS_PORT = os.environ.get("TTS_port", "41715")
TTS_SPEAKER = os.environ.get("TTS_speaker", "1878365378")
TTS_SPEED = os.environ.get("TTS_speed", "1.3")


# 視覚設定
VLM_MODEL = os.environ.get("VLM_model", "please_set")
VLM_MMPROJ = os.environ.get("VLM_mmproj", "please_set")
VLM_PORT = os.environ.get("VLM_port", "9003")
VLM_HOST = os.environ.get("VLM_host", "localhost")
VLM_GPU_LAYERS = os.environ.get("VLM_GPU_layers", "-1")
