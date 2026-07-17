import os
import sys
from os.path import join, dirname, abspath


# 相対パス定義
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = abspath(join(dirname(__file__), '..', '..'))

EXAMPLE_PATH = join(BASE_DIR, '.env.example')
ENV_PATH = join(BASE_DIR, '.env')
SP_PATH = join(BASE_DIR, 'SystemPrompt.txt')

DB_PATH = join(BASE_DIR, 'DB')
CHROMA_PATH = join(DB_PATH, 'chroma.sqlite3')
SMEMO_PATH = join(DB_PATH, 'short_memory.jsonl')
MMEMO_PATH = join(DB_PATH, 'middle_memory.txt')

LLMSERVER_FILE_PATH = join(BASE_DIR, "src", "llm", "LLM_server_models")

STT_SRC = join(BASE_DIR, "src", "voice", "stt_src")
TTS_SRC = join(BASE_DIR, "src", "voice", "tts_src")