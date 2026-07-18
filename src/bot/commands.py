from discord.ext import commands, voice_recv
import asyncio
import numpy as np
from queue import Queue
from scipy.signal import resample_poly



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

        audio = np.frombuffer(pcm, dtype = np.int16)
        audio = audio.astype(np.float32) / 32768.0

        # 2channel -> 1channel
        stereo = audio.reshape(-1, 2)
        audio = stereo[:, 0]

        # 48000Hz -> 16000Hz
        audio = resample_poly(audio, 1, 3)

        self.buffers[user_id] = np.concatenate([self.buffers[user_id], audio])

        while len(self.buffers[user_id]) >= CHUNK:
            block = self.buffers[user_id][:CHUNK]
            self.buffers[user_id] = self.buffers[user_id][CHUNK:]
            self.sources[user_id][1].put_nowait(block)


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



class Order(commands.Cog):
    def __init__(self, client, sources: dict[int, tuple[str, Queue]]):
        self.client = client
        self.sources = sources


    @commands.command(name = "join")
    async def join(self, ctx):
        if ctx.author.voice is None:
            await ctx.send("~joinを実行する場合はVCに入ってください")
            return

        channel = ctx.author.voice.channel

        if ctx.voice_client:
            vc = ctx.voice_client

            if vc.channel != channel:
                vc.stop_listening()
                await vc.move_to(channel)
                vc.listen(AudioSink(self.sources, asyncio.get_running_loop()))
                await ctx.send("VCを変更しました")
            else:
                await ctx.send("botは既に参加済みです")

        else:
            vc = await channel.connect(cls = voice_recv.VoiceRecvClient)
            vc.listen(AudioSink(self.sources, asyncio.get_running_loop()))
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