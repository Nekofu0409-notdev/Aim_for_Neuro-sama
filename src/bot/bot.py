from queue import Queue
from typing import cast

import discord
from discord.ext import commands

# 自作関数
from src.config import TOKEN
from src.llm import LLM_Core

from .commands import Order

intent = discord.Intents.default()
intent.message_content = True
intent.voice_states = True


async def run_bot(sources: dict[int, tuple[str, Queue]], vad_q: Queue, llm_core: LLM_Core, wav_q: Queue) -> commands.Bot:
    client = commands.Bot(
        command_prefix="~",
        intents=intent,
        cls=discord.ext.voice_recv.VoiceRecvClient,   # type: ignore[call-arg]
    )

    @client.event
    async def on_ready():
        print(f"ログイン: {client.user}")
        print("開始")

    await client.add_cog(Order(sources, vad_q, llm_core, wav_q))
    await client.start(TOKEN)

    return client


async def stop_bot(client: commands.Bot) -> None:
    order = client.get_cog("Order")
    if order is None:
        return

    order = cast(Order, order)
    if order.player.task is not None:
        order.player.task.cancel()

    await client.close()


if __name__ == "__main__":
    pass

    # sources: dict[int, tuple[str, Queue]] = {}
    # asyncio.run(run_bot(sources, Queue(), None, Queue()))
