import sys
import time

# 一時的に標準出力を抑える
class DummyFile(object):
    def write(self, x): pass

save_stdout = sys.stdout
sys.stdout = DummyFile()

import pygame

# 標準出力を戻す
sys.stdout = save_stdout

pygame.mixer.init()

def play_sound(file):
    pygame.mixer.music.load(file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)