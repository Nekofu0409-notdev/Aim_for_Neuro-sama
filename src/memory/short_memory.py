import json
from typing import List

#自作関数
from src.config import SMEMO_PATH, SYSTEMPROMPT_PATH



CONTEXT_LIMIT = 11   # 奇数のみ(往復回数 × 2 - 1)

def short_write(say: str, answer: str) -> None:
    with open(SMEMO_PATH, 'a', encoding = 'utf-8') as f:
        f.write(json.dumps({'role': 'user', 'content': say}, ensure_ascii = False) + "\n")
        f.write(json.dumps({'role': 'assistant', 'content': answer}, ensure_ascii = False) + "\n")


def short_count() -> int:
    with open(SMEMO_PATH, 'r', encoding='utf-8') as f:
        count = sum(1 for _ in f)
    return count


def short_clear() -> None:
    with open(SMEMO_PATH, 'w', encoding='utf-8'):
        pass
    print(f"{SMEMO_PATH}の中身を空にしました")


def short_delete() -> None:
    if short_count() > CONTEXT_LIMIT:

        #短期記憶読み込み
        with open(SMEMO_PATH, 'r', encoding = 'utf-8') as f:
            all_lines = f.readlines()

        old_lines = all_lines[:-(CONTEXT_LIMIT - 1)] 
        keep_lines = all_lines[-(CONTEXT_LIMIT - 1):]

        with open(SMEMO_PATH, 'w', encoding = 'utf-8') as f:
            f.writelines(keep_lines)



class Create_Input:
    def __init__(self):
        with open(SYSTEMPROMPT_PATH, 'r', encoding = 'utf-8') as f:
            systemprompt = f.read().strip()

        self.sp = {'role': 'system', 'content': systemprompt}
        

    def create(self, say) -> List:
        messages = []

        #メッセージ作成
        messages.append(self.sp)
        with open(SMEMO_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                messages.append(json.loads(line))
        messages.append({'role': 'user', 'content': say})

        return messages



if __name__ == "__main__":
    short_write("a", "b")
    print(short_count())
    short_clear()