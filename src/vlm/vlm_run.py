import asyncio
import re

from openai import AsyncOpenAI

#自作関数
from src.config import LLM_HOST, LLM_PORT
from src.memory import Create_Input


class Run_OpenAI:
    def __init__(self, tts_q: asyncio.Queue) -> None:
        self.client = AsyncOpenAI(
            base_url = f"http://{LLM_HOST}:{LLM_PORT}/v1",
            api_key = "empty",
        )
        self.create = Create_Input()
        self.tts_q = tts_q
        self.id = None


    def _process_content(self, content: str, doubt: bool, doubt_text: str):
        if doubt:
            doubt_text += content

            if re.search(r"<\|channel\|>.*?<channel\|>", doubt_text, flags=re.DOTALL):
                content = re.sub(r"<\|channel\|>.*?<channel\|>", "", doubt_text, flags=re.DOTALL)
                doubt_text = ""
                doubt = False

            elif re.search(r"---+[ \t]\*\n", doubt_text, flags=re.DOTALL):
                content = re.sub(r"^---+[ \t]\*\n", "", doubt_text, flags=re.DOTALL,)
                doubt_text = ""
                doubt = False

            elif re.search(r"---+(.+)", doubt_text, flags=re.DOTALL):
                content = doubt_text
                doubt_text = ""
                doubt = False

            elif "<|" in doubt_text or "--" in doubt_text:
                return None, doubt, doubt_text

            else:
                content = doubt_text
                doubt_text = ""
                doubt = False

        elif "<" in content or "-" in content:
            doubt_text = content
            doubt = True
            return None, doubt, doubt_text

        return content, doubt, doubt_text


    async def run_openai(self):
        self.id = object()
        messages = self.create.create()

        res = None
        doubt = False
        doubt_text = ""
        response = ""

        res = await self.client.responses.create(
            model = "empty",
            input = messages,
            stream = True,
            reasoning={"effort": "none"},
        )

        print("AI:")

        async for part in res:
            if part.type != "response.output_text.delta":
                continue

            content, doubt, doubt_text = self._process_content(part.delta, doubt, doubt_text)
            if content is None:
                continue

            print(content, end="", flush=True)
            response += content

            await self.tts_q.put((self.id, "assistant", content))

        await self.tts_q.put((self.id, "system", response))


    async def close(self):
        await self.client.close()



if __name__ == "__main__":
    pass
