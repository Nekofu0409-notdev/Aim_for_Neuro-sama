import asyncio
import io
import time
import traceback
from contextlib import suppress
from queue import Empty, Queue

import discord
import numpy as np
from discord.ext import commands, voice_recv
from scipy.signal import resample_poly

# 自作関数
from src.config import FFMPEG_PATH
from src.llm import LLM_Core
from src.memory import short_write

CHUNK = 512
CONVERSATION_BLANK = 1.5
CONVERSATION_OVERLAP = 0.5



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
    def __init__(self, vad_q: Queue, llm_core: LLM_Core, wav_q: Queue):
        self.vc = None
        self.vad_q = vad_q
        self.llm = llm_core
        self.wav_q = wav_q
        self.blank_start = time.monotonic()
        self.talk_start = None
        self.task = None
        self.allow_id = None
        self.id = None
        self.pending_wavs = []


    def set_vc(self, vc):
        self.vc = vc
        if self.task is None or self.task.done():
            self.task = asyncio.create_task(self.run())


    async def _wait(self) -> bytes:
        assert self.vc is not None
        count = 0
        speaking = False

        while True:
            try:
                vad = self.vad_q.get_nowait()

                if vad == "start":
                    count += 1
                    speaking = True
                    if self.talk_start is not None:
                        overlap = time.monotonic() - self.talk_start
                        if overlap < CONVERSATION_OVERLAP and self.vc.is_playing():
                            self.vc.source.cleanup()
                            self.allow_id = None

                elif vad == "end":
                    count -= 1
                    if count <= 0:
                        speaking = False
                        self.blank_start = time.monotonic()

            except Empty:
                with suppress(Empty):
                    id, w = self.wav_q.get_nowait()
                    self.pending_wavs.append((id, w))

                if self.pending_wavs:
                    self.id, wav = self.pending_wavs[0]

                    if self.allow_id is self.id:
                        self.pending_wavs.pop(0)
                        if isinstance(wav, bytes):
                            return wav
                        else:
                            short_write(wav[0], wav[1])
                            continue

                    else:
                        # overlap 発動 -> list が到着する前に speaking が終わり、推論が始まったときのため、nowait にしてある
                        # speaking が続いていた場合は if speaking に入るため問題なし
                        if isinstance(wav, list):
                            self.pending_wavs.pop(0)
                            self.llm.reasoning_cancel_nowait(wav[0])

                if speaking:
                    self.llm.reasoning_cancel_wait()

                if self.pending_wavs:
                    blank_time = time.monotonic() - self.blank_start

                    if blank_time >= CONVERSATION_BLANK:
                        self.allow_id = self.llm.return_id()
                        self.id, wav = self.pending_wavs.pop(0)

                        if self.allow_id is self.id:
                            if isinstance(wav, bytes):
                                return wav
                            else:
                                short_write(wav[0], wav[1])

                await asyncio.sleep(0.01)


    async def run(self):
        try:
            while True:
                while self.vc is None:
                    await asyncio.sleep(0.01)

                wav = await self._wait()

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

                self.talk_start = time.monotonic()

        except asyncio.CancelledError:
            pass

        except Exception:   # noqa: BLE001
            print("run: exception")
            traceback.print_exc()



class Order(commands.Cog):
    def __init__(
            self,
            sources: dict[int, tuple[str, Queue]],
            vad_q: Queue,
            llm_core: LLM_Core,
            wav_q: Queue
        ):
        self.sources = sources
        self.player = Wav_Player(vad_q, llm_core, wav_q)


    def _start_listening(self, vc):
        vc.listen(AudioSink(self.sources, asyncio.get_running_loop()))
        self.player.set_vc(vc)


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
