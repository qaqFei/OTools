from tkinter import Tk,Toplevel
from time import time,sleep
from math import cos,pi

AnimationTime = 0.5
AnimationFps = 60
AnimationGrX = int(AnimationFps * AnimationTime) + 1
z = 0.5
AnimationGr = [z * cos(x / AnimationGrX * pi) + z for x in range(0,AnimationGrX)] ; del z
AnimationGrSum = sum(AnimationGr)
AnimationGr = [x / AnimationGrSum for x in AnimationGr] ; del AnimationGrSum
AnimationStepTime = AnimationTime / len(AnimationGr)

def RectEffect(Window:Tk|Toplevel,TargetRect:tuple[int|float]):
    Window.update()
    yx,yy,yw,yh = Window.winfo_x(),Window.winfo_y(),Window.winfo_width(),Window.winfo_height()
    dx,dy,dw,dh = TargetRect[2]-yx,TargetRect[3]-yy,TargetRect[0]-yw,TargetRect[1]-yh
    x,y,w,h = yx,yy,yw,yh
    for step in AnimationGr:
        st = time()
        x,y,w,h = (
            x + step * dx,
            y + step * dy,
            w + step * dw,
            h + step * dh
        )
        Window.geometry(f"{int(w)}x{int(h)}+{int(x)}+{int(y)}")
        sleep(AnimationStepTime - min(time() - st,AnimationStepTime))

def _test():
    from ctypes import windll
    from threading import Thread
    from random import randint
    root = Tk()
    root.title("Tkinter.Window.NonlinearChangeWindowRect")
    def Main():
        while True:
            rect = [randint(0,int(root.winfo_screenwidth() * 0.75)),randint(0,int(root.winfo_screenheight() * 0.75))]
            rect += [randint(0,root.winfo_screenwidth() - rect[0]),randint(0,root.winfo_screenheight() - rect[1])]
            RectEffect(root,rect)
    Thread(target=Main,daemon=True).start()
    root.protocol("WM_DELETE_WINDOW",lambda:windll.kernel32.ExitProcess(0))
    root.mainloop()

if __name__ == "__main__":
    _test()