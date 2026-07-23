import re
import asyncio
from openai import AsyncOpenAI

#自作関数
from src.config import LLM_PORT, STREAM, THINK, TTS
from src.memory import Create_Input, short_delete, short_write



class Run_OpenAI:
    def __init__(self):
        self.llm_port = f"http://localhost:{LLM_PORT}/v1"
        self.llm_name = "empty"
        self.api_key = "empty"
        self.create = Create_Input()


    async def run_openai(self, say):
        response = ""
        doubt_text = ""
        doubt = False

        client = AsyncOpenAI(
            base_url = self.llm_port,
            api_key = self.api_key,
        )

        messages = self.create.create(say)
        short_delete()

        if THINK:
            effort = "medium"
        else:
            effort = "none"

        res = await client.responses.create(
            model = self.llm_name,
            input = messages,
            stream = STREAM,
            reasoning={"effort": f"{effort}"},
        )

        print("\nAI:")
        if STREAM:
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

                    if TTS:
                        pass

        else:
            raw_text = res.output[0].content[0].text

            clean_text = re.sub(r"<\|channel\|?>.*?<channel\|?>", "", raw_text, flags=re.DOTALL)
            clean_text = re.sub(r"---+[ \t]*\n", "", clean_text)
            clean_text = clean_text.strip()

            print(clean_text)
            response = clean_text

            if TTS:
                pass

        print("\n")
        short_write(say, response)



if __name__ == "__main__":
    from src.memory import short_clear

    asyncio.run(Run_OpenAI().run_openai("ハロー"))
    short_clear()