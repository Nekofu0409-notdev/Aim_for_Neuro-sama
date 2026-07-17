import tkinter as tk
from tkinter import font

import asyncio
import threading
from abc import ABC, abstractmethod

#自作関数
from src.globals import G_Var



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




# 実行
if __name__ == "__main__":
    root = tk.Tk()
    root.title("AI")
    root.geometry("1280x720")
    title_font = font.Font(family = "Yu Gothic UI", size = 30)
    defoult_font = font.Font(family = "Yu Gothic UI", size = 20)

    label = tk.Label(root, text = "デバッグ", font = title_font)
    label.place(x = 640, y = 30, anchor = tk.CENTER)

    stt_run_button = tk.Button(root, text = "STT開始", font = defoult_font,)
    stt_run_button.bind("<Button-1>", stt.run)
    stt_run_button.place(x = 540, y = 100, anchor = tk.CENTER)


    root.mainloop()