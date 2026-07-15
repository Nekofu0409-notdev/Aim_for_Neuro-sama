#py\memory\short_memory.py

import os
from os.path import exists
import json
import asyncio

#自作関数
from src.config import SMEMO_PATH


class Short_Memory():
    def __init__(self):
        self.sm_p = SMEMO_PATH

    async def short_write(self, say, answer):
        self.say = say
        self.answer = answer

        if exists(self.sm_p):
            with open(self.sm_p, 'a', encoding='utf-8') as f:
                f.write(json.dumps({'role': 'user', 'content': self.say}, ensure_ascii=False) + "\n")
                f.write(json.dumps({'role': 'assistant', 'content': self.answer}, ensure_ascii=False) + "\n")

    async def short_count(self):
        with open(self.sm_p, 'r', encoding='utf-8') as f:
            count = sum(1 for _ in f)
        return count

    def short_clear(self):
        with open(self.sm_p, 'w', encoding='utf-8') as f:
            pass
        print(f"{self.sm_p}の中身を空にしました")


if __name__ == "__main__":
    sm = Short_Memory()
    asyncio.run(sm.short_write("a","b"))
    print(sm.short_count())
    #消去
    #sm.short_clear()