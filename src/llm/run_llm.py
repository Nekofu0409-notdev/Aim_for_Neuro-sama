import asyncio
import re

from openai import AsyncOpenAI

#自作関数
from src.config import LLM_PORT, TTS
from src.memory import Create_Input, short_delete


class Run_OpenAI:
    def __init__(self, tts_q: asyncio.Queue) -> None:
        self.llm_port = f"http://localhost:{LLM_PORT}/v1"
        self.llm_name = "empty"
        self.api_key = "empty"
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


    async def run_openai(self, say):
        self.id = object()
        client = AsyncOpenAI(
            base_url = self.llm_port,
            api_key = self.api_key,
        )
        messages = self.create.create(say)
        short_delete()

        res = None
        doubt = False
        doubt_text = ""
        response = ""

        try:
            res = await client.responses.create(
                model = self.llm_name,
                input = messages,
                stream = True,
                reasoning={"effort": "none"},
            )

            print(f"user:\n{say}")
            print("\nAI:")

            async for part in res:
                if part.type != "response.output_text.delta":
                    continue

                content, doubt, doubt_text = self._process_content(part.delta, doubt, doubt_text)
                if content is None:
                    continue

                print(content, end="", flush=True)
                response += content

                if TTS:
                    await self.tts_q.put((self.id, "assistant", content))

            if TTS:
                await self.tts_q.put((self.id, "system", [say, response]))

        except asyncio.CancelledError:
            await self.tts_q.put((self.id, "system", "cancelled"))
            if res is not None:
                await res.close()
            print(" cancelled.\n")
            return "cancelled"


# 使用しない
# else:
#     raw_text = res.output[0].content[0].text

#     clean_text = re.sub(r"<\|channel\|?>.*?<channel\|?>", "", raw_text, flags = re.DOTALL)
#     clean_text = re.sub(r"---+[ \t]*\n", "", clean_text)
#     clean_text = clean_text.strip()

#     print(clean_text)
#     response = clean_text

#     if TTS:
#         if self.stt_q.empty():
#             self.tts_q.put_nowait(content)
#         else:
#             self.tts_q.put_nowait(None)
#             fin = True



if __name__ == "__main__":
    pass
    # from src.memory import short_clear

    # asyncio.run(Run_OpenAI().run_openai("ハロー"))
    # short_clear()
