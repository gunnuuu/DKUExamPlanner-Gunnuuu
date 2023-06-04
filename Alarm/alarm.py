import tkinter as tki
import sys
import os
from alarm_ui import AlarmUI

def alarm():
    window = tki.Tk()

    window.minsize(600, 395)
    window.maxsize(600, 395)
    window.title("알람 설정")

    img = tki.PhotoImage(file='C:\\Users\\pkunw\\OneDrive\\바탕 화면\\Alarm\\icons\\alarm-clock.gif')
    window.tk.call('wm', 'iconphoto', window._w, img)

    AlarmUI(window)

    window.mainloop()
