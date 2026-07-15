import json
import asyncio
import re
from ollama import AsyncClient
from openai import AsyncOpenAI

#自作関数
from src.config import (
    LLM_PORT,
    STREAM,
    THINK,

    SP_PATH,
    SMEMO_PATH,

    TTS,
)
from src.memory import S_Memory



class Create_input():
    def __init__(self):
        self.sp_p = SP_PATH
        self.smemo_p = SMEMO_PATH

    async def create(self, say):
        try:
            self.messages = []
            self.say = say

            #メッセージ作成
            with open(self.sp_p, 'r', encoding='utf-8') as f:
                self.sp = f.read().strip()
                self.messages.append({'role': 'system', 'content': self.sp})
            with open(self.smemo_p, 'r', encoding='utf-8') as f:
                for line in f:
                    self.messages.append(json.loads(line))
            self.messages.append({'role': 'user', 'content': self.say})

            return self.messages

        except asyncio.CancelledError:
            raise



class Short_Delete():
    def __init__(self):
        self.sm = S_Memory()
        self.sm_p = SMEMO_PATH

    async def delete(self):
        try:
            if await self.sm.short_count() > 11:

                #短期記憶読み込み
                with open(self.sm_p, 'r', encoding = 'utf-8') as f:
                    all_lines = f.readlines()

                old_lines = all_lines[:-10] 
                keep_lines = all_lines[-10:]

                with open(self.sm_p, 'w', encoding = 'utf-8') as f:
                    f.writelines(keep_lines)

        except asyncio.CancelledError:
            raise



class Run_OpenAI():
    def __init__(self):
        self.llm_port = f"http://localhost:{LLM_PORT}/v1"
        self.llm_name = "empty"
        self.stream = STREAM
        self.think = THINK
        self.api_key = "empty"

        self.sm = S_Memory()
        self.ci = Create_input()
        self.sd = Short_Delete()
        self.sm_p = SMEMO_PATH

        self.tts = TTS


    async def run_openai(self, say):
        self.say = say

        response = ""
        res = ""
        messages = []

        doubt_text = ""
        doubt = False

        client = AsyncOpenAI(
            base_url = self.llm_port,
            api_key = self.api_key,
        )

        try:
            #メッセージ作成
            messages = await self.ci.create(say = self.say)

            #短期記憶部分消去
            delete_task = asyncio.create_task(self.sd.delete())

            if self.think:
                self.effort = "medium"
            else:
                self.effort = "none"

            res = await client.responses.create(
                model = self.llm_name,
                input = messages,
                stream = self.stream,
                reasoning={"effort": f"{self.effort}"},
            )

            #消去待ち
            await delete_task

            print("\nAI:")
            if self.stream:
                async for part in res:
                    if part.type == 'response.output_text.delta':
                        content = part.delta

                        if doubt:
                            doubt_text += content
                            
                            if re.search(r"<\|channel\|?>.*?<channel\|?>", doubt_text, flags=re.DOTALL):
                                clean_text = re.sub(r"<\|channel\|?>.*?<channel\|?>", "", doubt_text, flags=re.DOTALL)
                                content = clean_text
                                doubt_text = ""
                                doubt = False

                            elif re.search(r"---+[ \t]*\n", doubt_text, flags=re.DOTALL):
                                clean_text = re.sub(r"^---+[ \t]*\n", "", doubt_text, flags=re.DOTALL)
                                content = clean_text
                                doubt_text = ""
                                doubt = False

                            #セリフだった場合
                            elif re.search(r"---+(.+)", doubt_text, flags=re.DOTALL):
                                content = doubt_text
                                doubt_text = ""
                                doubt = False
                            
                            elif "<|" in doubt_text:
                                continue

                            elif "--" in doubt_text:
                                continue
                            
                            #セリフだった場合
                            else:
                                content = doubt_text
                                doubt_text = ""
                                doubt = False

                        elif "<" in content:
                            doubt_text += content
                            doubt = True
                            continue

                        elif "-" in content:
                            doubt_text += content
                            doubt = True
                            continue

                        print(content, end = "", flush = True)
                        response += content

                        #TTS = True
                        if self.tts:
                            pass

            else:
                raw_text = res.output[0].content[0].text

                clean_text = re.sub(r"<\|channel\|?>.*?<channel\|?>", "", raw_text, flags=re.DOTALL)
                clean_text = re.sub(r"---+[ \t]*\n", "", clean_text)
                clean_text = clean_text.strip()

                print(clean_text)
                response = clean_text

                #TTS = True
                if self.tts:
                    pass

            print("\n")

            await self.sm.short_write(say = self.say, answer = response)

        except asyncio.CancelledError:
            raise



class Debug():
    def __init__(self):
        self.say = "ここはどこ？"
        self.rl = Run_OpenAI()

    async def run(self):
        await self.rl.run_openai(say = self.say)



if __name__ == "__main__":
    dg = Debug()
    asyncio.run(dg.run())

    sm = S_Memory()
    sm.short_clear()