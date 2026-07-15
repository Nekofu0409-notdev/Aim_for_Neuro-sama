import tkinter as tk
from tkinter import font
from tkinter import messagebox

import asyncio
import threading
import sounddevice as sd
from abc import ABC, abstractmethod

#自作関数
from src.voice import R_stt
from src.globals import G_Var



# オーディオ関連
class ID_Conf():
    def __init__(self):
        pass
        
    def audio_in(self, event) -> None:
        print()
        print("ID, Name, method\n")

        for i, dev in enumerate(sd.query_devices()):
            if dev["max_input_channels"] > 0:
                hostapi = sd.query_hostapis(dev["hostapi"])["name"]
                print(f"{i}, {dev['name']}, {hostapi}")

    def audio_out(self, event):
        print()
        print("ID, Name, method\n")

        for i, dev in enumerate(sd.query_devices()):
            if dev["max_output_channels"] > 0:
                hostapi = sd.query_hostapis(dev["hostapi"])["name"]
                print(f"{i}, {dev['name']}, {hostapi}")



# Async関連すべて
class Loop(ABC):
    def __init__(self):
        self.gv = G_Var()
        self.exist = None
        self.fin_done = True

        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target = self._start_loop, daemon = True)
        self.thread.start()

    
    def _start_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()


    def _fin_complete(self, future):
        try:
            future.result()
        except Exception as e:
            print(f"終了処理エラー: {e}")

        self.exist = None
        self.fin_done = True


    @abstractmethod
    def run(self, event):
        pass

    
    @abstractmethod
    def fin(self, event):
        pass



class STT(Loop):
    def __init__(self):
        super().__init__()
        self.rs = R_stt(self.gv)


    def run(self, event):
        if self.exist is not None:
            messagebox.showwarning("警告", "既にSTTは実行中です")
            return False

        if self.fin_done is not True:
            messagebox.showwarning("警告", "STTは終了処理中です")
            return False

        self.exist = self.rs
        asyncio.run_coroutine_threadsafe(self.exist.diart_run(), self.loop)


    def fin(self, event):
        if self.exist is None:
            messagebox.showwarning("警告", "STTは実行されていません")
            return False

        if self.fin_done is not True:
            messagebox.showwarning("警告", "STTは終了処理中です")
            return False

        self.fin_done = False
        fin_signal = asyncio.run_coroutine_threadsafe(self.exist.fin(), self.loop)
        fin_signal.add_done_callback(self._fin_complete)




# 実行
if __name__ == "__main__":
    root = tk.Tk()
    root.title("AI")
    root.geometry("1280x720")
    title_font = font.Font(family = "Yu Gothic UI", size = 30)
    defoult_font = font.Font(family = "Yu Gothic UI", size = 20)

    stt = STT()
    id_conf = ID_Conf()

    label = tk.Label(root, text = "デバッグ", font = title_font)
    label.place(x = 640, y = 30, anchor = tk.CENTER)

    stt_run_button = tk.Button(root, text = "STT開始", font = defoult_font,)
    stt_run_button.bind("<Button-1>", stt.run)
    stt_run_button.place(x = 540, y = 100, anchor = tk.CENTER)

    stt_fin_button = tk.Button(root, text = "STT終了", font = defoult_font,)
    stt_fin_button.bind("<Button-1>", stt.fin)
    stt_fin_button.place(x = 740, y = 100, anchor = tk.CENTER)

    stt_fin_button = tk.Button(root, text = "入力デバイス確認", font = defoult_font,)
    stt_fin_button.bind("<Button-1>", id_conf.audio_in)
    stt_fin_button.place(x = 520, y = 170, anchor = tk.CENTER)

    stt_fin_button = tk.Button(root, text = "出力デバイス確認", font = defoult_font,)
    stt_fin_button.bind("<Button-1>", id_conf.audio_out)
    stt_fin_button.place(x = 760, y = 170, anchor = tk.CENTER)


    root.mainloop()