from tkinter import Tk,Toplevel
from typing import Literal
from time import time,sleep
from math import cos,pi

EffectTime = 0.4
EffectFps = 70
EffectGrX = int(EffectFps * EffectTime) + 1
z = 0.5
EffectGr = [z * cos(x / EffectGrX * pi) + z for x in range(0,EffectGrX)] ; del z
EffectGrSum = sum(EffectGr)
EffectGr = [x / EffectGrSum for x in EffectGr] ; del EffectGrSum
EffectStepTime = EffectTime / len(EffectGr)

def _BaseEffect(Window:Tk|Toplevel,Effect:Literal[1,-1]):
    Window.update()
    yx,yy,yw,yh = Window.winfo_x(),Window.winfo_y(),Window.winfo_width(),Window.winfo_height()
    Window.state("normal") ; Window.geometry(f"{yw}x{yh}+{yx}+{yy}") ; Window.update()
    dx,dy,dw,dh = yw * 0.2,yh * 0.2,yw * 0.4,yh * 0.4
    if Effect == 1:
        x,y,w,h = (
            yx + dx,
            yy + dy,
            yw - dw,
            yh - dh
        )
    else:
        x,y,w,h = yx,yy,yw,yh
    alpha = {-1:1.0,1:0.0}[Effect]
    for step in EffectGr:
        start_time = time()
        alpha += step * Effect
        x,y,w,h = (
            x - dx * step * Effect,
            y - dy * step * Effect,
            w + dw * step * Effect,
            h + dh * step * Effect
        )
        Window.attributes("-alpha",alpha)
        Window.geometry(f"{int(w)}x{int(h)}+{int(x)}+{int(y)}")
        sleep(EffectStepTime - min(EffectStepTime,time() - start_time))
    Window.attributes("-alpha",{1:1.0,-1:0.0}[Effect])
    Window.geometry(f"{yw}x{yh}+{yx}+{yy}")

def ShowOpenEffect(Window:Tk|Toplevel):
    _BaseEffect(Window,1)

def ShowCloseEffect(Window:Tk|Toplevel):
    _BaseEffect(Window,-1)

def _test():
    from tkinter.ttk import Button
    from threading import Thread
    import SetWindowMoveWidget
    root = Tk()
    SetWindowMoveWidget.SetWindowMoveWidget(root,root)
    root.overrideredirect(True)
    root.geometry(f"{int(root.winfo_screenwidth() * 0.75)}x{int(root.winfo_screenheight() * 0.75)}")
    Button(root,text="OpenEffect",command=lambda:Thread(target=lambda:(root.attributes("-alpha",0.0),root.update(),sleep(0.5),ShowOpenEffect(root))).start()).pack()
    Button(root,text="CloseEffect",command=lambda:Thread(target=lambda:(ShowCloseEffect(root),sleep(0.5),root.attributes("-alpha",1.0))).start()).pack()
    root.mainloop()

if __name__ == "__main__":
    _test()