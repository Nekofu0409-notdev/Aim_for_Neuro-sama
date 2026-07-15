#py\memory\middle_memory.py
#現在必要なし

# import os
# from os.path import exists
# import json

# #自作関数
# from py.config.return_path import *


# class Middle_Memory():
#     def __init__(self):
#         self.mm_p = MMEMO_PATH

#     def middle_write(self, summary):
#         self.summary = summary

#         with open(self.mm_p, 'w', encoding='utf-8') as f:
#             f.write(self.summary + "\n")

#     def middle_clear(self):
#         with open(self.mm_p, 'w', encoding='utf-8') as f:
#             pass
#         print(f"{self.mm_p}の中身を空にしました")


# if __name__ == "__main__":
#     mm = Middle_Memory()
#     mm.middle_write(summary = "hello")
#     #消去
#     #mm.middle_clear()