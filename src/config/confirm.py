#py\config\confirm.py

import os
from os.path import exists

#自作関数
from .return_env import *


class Confirm_All():
    def __init__(self):
        self.env_p = ENV_PATH

        self.llm_model = LLM_MODEL
        self.llm_port = LLM_PORT

        self.stt = STT
        self.ms = MOONSHINE
        self.ms_p = MOONSHINE_PATH
        self.ms_a = MOONSHINE_ARCH
        self.qa = QWENASR
        self.stt_engines = [self.ms, self.qa]

        self.tts = TTS
        self.aivis = AIVISSPEECH
        self.aivis_port = AIVISSPEECH_PORT
        self.aivis_speaker = AIVIS_SPEAKER
        self.tts_engines = [self.aivis]


    #.env関連
    def env_confirm(self):
        if not exists(self.env_p):
            print(f"{self.env_p}が見つかりません")
            return False
        
        return True


    #LLM関連
    def llm_confirm(self):
        if self.llm_model == "please_set":
            print("LLMの名前を設定してください")
            return False

        if self.llm_port == "please_set":
            print("LLMのポート番号を設定してください")
            return False

        return True


    #STT関連
    def stt_confirm(self):

        #STTを使わない場合
        if not self.stt:
            return True

        #エンジン数確認
        if self.stt and sum(self.stt_engines) != 1:
            print("使うSTTは一種類にしてください")
            return False

        #moonshine_voice
        if self.ms:
            if self.ms_p == "please_set":
                print("moonshine voiceモデルのパスを設定してください")
                return False

            if not exists (self.ms_p):
                print(f"{self.ms_p}がありません")
                return False

            if self.ms_a == "please_set":
                print("moonshine voiceのアーキテクチャを設定してください")
                return False

        #qwen3_asr
        if self.qa:
            pass
        
        return True


    #TTS関連
    def tts_confirm(self):

        #TTSを使わない場合
        if not self.tts:
            return True

        #エンジン数確認
        if self.tts and sum(self.tts_engines) != 1:
            print("使うTTSは一種類にしてください")
            return False

        #AivisSpeech
        if self.aivis:
            if self.aivis_speaker == "please_set":
                print("AivisSpeechの話者IDを設定してください")
                return False

        return True


class Confirm_Run():
    #全てチェック
    def run(self):
        ca = Confirm_All()

        if not ca.env_confirm():
            return False
        if not ca.llm_confirm():
            return False
        if not ca.stt_confirm():
            return False
        if not ca.tts_confirm():
            return False

        return True



if __name__ == "__main__":
    print(Confirm_Run().run())