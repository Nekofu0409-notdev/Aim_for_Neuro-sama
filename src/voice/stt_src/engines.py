from moonshine_voice import MicTranscriber, TranscriptEventListener, ModelArch



class Moonshine():
    def __init__(self):
        self.model_path = MOONSHINE_PATH
        self.model_arch = None


    async def run_moon(self):

        if MOONSHINE_ARCH == "base":
            self.model_arch = ModelArch.BASE
        elif MOONSHINE_ARCH == "tiny":
            self.model_arch = ModelArch.TINY

        mic_transcriber = MicTranscriber(
            model_path = self.model_path,
            model_arch = self.model_arch,
            update_interval=1.0, 
            device=84,
            samplerate=44100, 
            channels=1,
            blocksize=32768,
            options={
                "vad_max_segment_duration": "15.0",
                "max_tokens_per_second": "13.0",
            }
        )

        class MyListener(TranscriptEventListener):
            def __init__(self):
                self.ga = py.globals.global_var.Globals_Add()

            def on_line_completed(self, event):
                clean_text = event.line.text.replace(" ", "")
                asyncio.run(self.ga.add_stt(clean_text))

        mic_transcriber.add_listener(MyListener())
        mic_transcriber.start()

        try:
            while True:
                await asyncio.sleep(0.1)

        except KeyboardInterrupt:
            mic_transcriber.stop()
            mic_transcriber.close()
            raise



class Qwen3_ASR():
    def __init__(self):
        pass

    async def run_qwen3():
        pass