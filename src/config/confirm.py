import shutil
from pathlib import Path

import chromadb

#自作関数
from .return_env import *
from .return_path import *


# env関連
def env():
    if not Path(ENV_PATH).exists():
        shutil.copy(ENV_EXAMPLE_PATH, ENV_PATH)

    return True


# LLM関連
def llm():
    if LLM_MODEL == "please_set":
        print("LLMモデルを設定してください")
        return False

    if not Path(LLM_MODEL_PATH).exists():
        print(f"{LLM_MODEL_PATH}が存在しません")
        return False

    return True


# DB関連
def db():
    if not Path(DB_PATH).exists():
        Path(DB_PATH).mkdir()
        print(f"{DB_PATH}を作成しました")

    if not Path(CHROMA_PATH).exists():
        chroma_client = chromadb.PersistentClient(path=DB_PATH)
        chroma_client.get_or_create_collection(name="memory")
        print(f"{CHROMA_PATH}を作成しました")
        print(f"{CHROMA_PATH}に領域「memory」を追加しました")

    if not Path(SMEMO_PATH).exists():
        with open(SMEMO_PATH, 'w', encoding='utf-8'):
            print(f"{SMEMO_PATH}を作成しました")

    return True


#STT関連
def stt():
    if STT:
        if STT_MODEL == "please_set":
            print("STTモデルを設定してください")
            return False

        if not Path(STT_MODEL_PATH).exists():
            print(f"{STT_MODEL_PATH}が存在しません")
            return False

        if TOKEN == "please_set":
            print("Discord bot Tokenを設定してください")
            return False

    return True


#TTS関連
def tts():
    if TTS:
        pass

    return True


# チェック
def confirm():
    if not env():
        return False
    if not llm():
        return False
    if not db():
        return False
    if not stt():
        return False

    return tts()



if __name__ == "__main__":
    print(confirm())
