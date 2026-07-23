#py\config\return_env.py

import os
import json
from dotenv import load_dotenv

#自作関数
from .return_path import *


load_dotenv(ENV_PATH, override=True, verbose=True)

#基本
LLM_MODEL = os.environ.get("LLM_model", "please_set")
LLM_PORT = os.environ.get("LLM_port", "please_set")
LLM_HOST = os.environ.get("LLM_host", "localhost")

STREAM = json.loads(os.environ.get("stream", "true").lower())
THINK = json.loads(os.environ.get("think", "false").lower())
TOP_K = int(os.environ.get("top_k", "5"))


#Discord関連
TOKEN = os.environ.get("Token", "please_set")


#音声認識
STT = json.loads(os.environ.get("STT", "false").lower())

QWEN_PORT = os.environ.get("Qwen3_Port", "please_set")


#音声合成
TTS = json.loads(os.environ.get("TTS", "false").lower())

AIVIS_PORT = os.environ.get("Aivis_Port", "please_set")
AIVIS_SPEAKER = os.environ.get("Aivis_Speaker", "please_set")
AIVIS_SPEED = os.environ.get("Aivis_Speed", "1.0")