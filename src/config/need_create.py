#py\config\need_create.py

import os
from os.path import exists
import shutil
import chromadb

#自作関数
from .return_path import *


class Prepare_Environment():
    def __init__(self):
        self.env_p = ENV_PATH
        self.ex_p = EXAMPLE_PATH
        self.db_p = DB_PATH
        self.crm_p = CHROMA_PATH
        self.sm_p = SMEMO_PATH
        self.mm_p = MMEMO_PATH
        self.msp_p = MSP_PATH

    def env(self):
        #.envの存在有無
        if not exists(self.env_p):
            shutil.copy(self.ex_p, self.env_p)
            print(f"{self.env_p}を作成しました")

    def db(self):
        #DB_dir、chromaの存在有無
        if not exists(self.db_p):
            os.makedirs(self.db_p)
            print(f"{self.db_p}を作成しました")

        if not exists(self.crm_p):
            chroma_client = chromadb.PersistentClient(path=self.db_p)
            chroma_client.get_or_create_collection(name="memory")
            print(f"{self.crm_p}を作成しました")
            print(f"{self.crm_p}に領域「memory」を追加しました")

        if not exists(self.sm_p):
            with open(self.sm_p, 'w', encoding='utf-8') as f:
                print(f"{self.sm_p}を作成しました")


# middle_memoryは現在必要なし

#         if not exists(self.mm_p):
#             with open(self.mm_p, 'w', encoding='utf-8') as f:
#                 print(f"{self.mm_p}を作成しました")
        

        if not exists(self.msp_p):
            with open(self.msp_p, 'w', encoding='utf-8') as f:
                print(f"{self.msp_p}を作成しました")


class Prepare_Run():
    def run(self):
        setup = Prepare_Environment()

        setup.env()
        setup.db()


if __name__ == "__main__":
    pr = Prepare_Run()
    pr.run()