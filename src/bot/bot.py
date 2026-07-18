import discord
from discord.ext import commands
import asyncio
from queue import Queue

# 自作関数
from src.config import TOKEN
from .commands import Order



discord.opus._load_default()

token = TOKEN
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

client = commands.Bot(
    command_prefix = "~",
    intents = intents,
    cls = discord.ext.voice_recv.VoiceRecvClient
)


@client.event
async def on_ready():
    print(f"ログイン: {client.user}")


async def setup(sources: dict[int, tuple[str, Queue]]):
    await client.add_cog(Order(client, sources))


async def run_bot(sources: dict[int, tuple[str, Queue]]) -> None:
    await setup(sources)
    await client.start(token)


async def stop_bot():
    await client.close()



if __name__ == "__main__":
    sources: dict[int, tuple[str, Queue]] = {}
    asyncio.run(run_bot(sources))