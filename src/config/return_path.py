import sys
from pathlib import Path

# 相対パス定義
if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).resolve().parents[2]

ENV_EXAMPLE_PATH = BASE_DIR / ".env.example"
ENV_PATH = BASE_DIR / ".env"

SYSTEMPROMPT_PATH = BASE_DIR / "SystemPrompt.txt"
USERID_PATH = BASE_DIR / "user_id.json"

DB_PATH = BASE_DIR / "DB"
CHROMA_PATH = DB_PATH / "chroma.sqlite3"
SMEMO_PATH = DB_PATH / "short_memory.jsonl"

KOBOLD_EXE_PATH = BASE_DIR / "models" / "LLM_server_models" / "koboldcpp" / "koboldcpp-nocuda.exe"
STT_EXE_PATH = BASE_DIR / "models" / "STT_models" / "audio_cpp" / "audiocpp-vulkan" / "audiocpp_server.exe"
TTS_EXE_PATH = BASE_DIR / "models" / "TTS_models" / "AivisSpeech" / "Windows-x64" / "run.exe"

FFMPEG_PATH = BASE_DIR / "models" / "ffmpeg" / "ffmpeg.exe"
TTS_SRC_PATH = BASE_DIR / "src" / "voice" / "tts_src"
