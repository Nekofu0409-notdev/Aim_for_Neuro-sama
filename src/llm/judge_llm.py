import logging

logger = logging.getLogger(__name__)

import textwrap

from openai import AsyncOpenAI
from openai.types.responses import ResponseInputParam

#自作関数
from src.config import JUDGE_LLM_PORT


class Run_OpenAI_Judge:
    def __init__(self) -> None:
        self.client = AsyncOpenAI(
            base_url = f"http://localhost:{JUDGE_LLM_PORT}/v1",
            api_key = "empty",
        )
        self.systemprompt =textwrap.dedent(
        """
        あなたは対話のターン管理を行う分類器です。
        AIが発話している最中に、ユーザーの音声が逐次音声認識されて届きます。
        その認識テキストから、AIが話し続けてよいかどうかを判定してください。

        # 入力の性質
        - 入力はユーザー発話の途中経過であり、逐次的に伸びていきます（前回より長くなることがあります）。
        - 句読点の欠落、助詞抜け、誤認識が混ざることがあります。
        - 空白や改行は無視し、与えられたテキスト全体だけで判断してください。

        # y（話し続けてよい）
        - 実質的な情報を追加しない、聞いていることを示すだけの短い反応である。
        - 内容語（名詞・動詞・形容詞）を含まない。
        - 全体がごく短い。

        # n（話すのを止めるべき）
        - 新しい情報・意見・質問・訂正・反論を含む。
        - 内容語、または疑問を含む。
        - 発話が長く伸びている。
        - 聞き手としてではなく、自分が話そうとしている。

        # 補足規則
        - 談話標識だけで始まっていても、続きに内容語が来れば n とする。
        - 相槌にも発話の前置きにもなり得る語は、単体では判断材料にしない。

        # 出力
        - 必ず `y` または `n` の1文字だけを出力する。
        - 説明・記号・改行・その他の文字を一切出力しない。

        # 迷ったとき
        - 内容語が無く、ごく短いと解釈できる場合のみ y。
        - それ以外は n。
        """
        ).strip()


    async def run_judge(self, say: str) -> bool:
        demos = [
            ("うん", "y"), ("へえ", "y"), ("あ。", "y"), ("あー", "y"),
            ("なるほど", "y"), ("そうだね", "y"), ("んー", "y"), ("うんうん", "y"),
            ("ちょっと待って", "n"), ("んー、でもさ", "n"),
            ("なんでそうなったの?", "n"), ("でも明日は行けない", "n"),
        ]

        messages: ResponseInputParam = [
            {"role": "system", "content": self.systemprompt}
        ]
        for text, label in demos:
            messages.append({"role": "user", "content": f"入力: {text}\n出力:"})
            messages.append({"role": "assistant", "content": label})
        messages.append({"role": "user", "content": f"入力: {say}\n出力:"})

        res = await self.client.responses.create(
            model = "empty",
            input = messages,
            temperature = 0,
            max_output_tokens = 4,
        )
        text = res.output_text.strip()

        if text.startswith("y"):
            return True
        if text.startswith("n"):
            return False

        logger.warning("想定外の出力: %s", text)
        return False


    async def close(self):
        await self.client.close()



if __name__ == "__main__":
    pass
