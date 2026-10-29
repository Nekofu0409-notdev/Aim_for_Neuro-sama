import asyncio
import io
from queue import Queue

import discord
import numpy as np
from discord.ext import commands, voice_recv
from scipy.signal import resample_poly

# 自作関数
from src.config import FFMPEG_PATH

# from src.memory import short_write

CHUNK = 512



class AudioSink(voice_recv.AudioSink):
    def __init__(self, sources: dict[int, tuple[str, Queue]], main_loop):
        super().__init__()
        self.sources = sources
        self.buffers: dict[int, np.ndarray] = {}
        self.loop = main_loop


    def push(self, user_id, user_name, pcm):
        if user_id not in self.sources:
            self.sources[user_id] = (user_name, Queue())

        if user_id not in self.buffers:
            self.buffers[user_id] = np.array([], dtype=np.float32)

        audio = np.frombuffer(pcm, dtype=np.int16)

        # 2channel -> 1channel
        if len(audio) % 2 == 0:
            audio = audio.reshape(-1, 2).mean(axis=1)

        audio = audio.astype(np.float32) / 32768.0

        # 48000Hz -> 16000Hz
        audio = resample_poly(audio, 1, 3)

        self.buffers[user_id] = np.concatenate([self.buffers[user_id], audio])

        while len(self.buffers[user_id]) >= CHUNK:
            block = self.buffers[user_id][:CHUNK]
            self.buffers[user_id] = self.buffers[user_id][CHUNK:]
            self.sources[user_id][1].put(block)


    def wants_opus(self) -> bool:
        return False


    def write(self, user, data):
        if user is None:
            return

        if user.bot:
            return

        self.loop.call_soon_threadsafe(self.push, user.id, user.name, data.pcm)


    def cleanup(self):
        pass



class Wav_Player:
    def __init__(self, wav_q: asyncio.Queue):
        self.vc = None
        self.id = None
        self.wav_q = wav_q


    def set_vc(self, vc):
        self.vc = vc


    async def play(self):
        while True:
            wav = await self.wav_q.get()

            if self.vc is None:
                continue

            while self.vc.is_playing():
                await asyncio.sleep(0.01)

            origin = discord.FFmpegPCMAudio(
                source = io.BytesIO(wav),
                pipe = True,
                executable = str(FFMPEG_PATH)
                )
            source = discord.PCMVolumeTransformer(
                origin,
                volume = 0.05
            )
            self.vc.play(source)



class Order(commands.Cog):
    def __init__(self, mic: dict[int, tuple[str, Queue]], wav_q: asyncio.Queue):
        self.mic = mic
        self.player = Wav_Player(wav_q)


    def _start_listening(self, vc):
        vc.listen(AudioSink(self.mic, asyncio.get_running_loop()))
        self.player.set_vc(vc)


    @commands.command(name = "join")
    async def join(self, ctx):
        if ctx.author.voice is None:
            await ctx.send("-joinを実行する場合はVCに入ってください")
            return

        channel = ctx.author.voice.channel

        if ctx.voice_client:
            vc = ctx.voice_client

            if vc.channel != channel:
                vc.stop_listening()
                await vc.move_to(channel)
                self._start_listening(vc)
                await ctx.send("VCを変更しました")
            else:
                await ctx.send("botは既に参加済みです")

        else:
            vc = await channel.connect(cls=voice_recv.VoiceRecvClient)
            self._start_listening(vc)
            await ctx.send("VCに接続しました")


    @commands.command(name = "leave")
    async def leave(self, ctx):
        vc = ctx.voice_client

        if vc is None:
            await ctx.send("botはVCに参加していません")
            return

        vc.stop_listening()
        await vc.disconnect()
        await ctx.send("VCから切断しました")
