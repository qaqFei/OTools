from tkinter import Tk,Toplevel
from time import time,sleep
from math import cos,pi

AnimationTime = 0.3
AnimationFps = 60
AnimationGrX = int(AnimationFps * AnimationTime) + 1
z = 0.5
AnimationGr = [z * cos(x / AnimationGrX * pi) + z for x in range(0,AnimationGrX)] ; del z
AnimationGrSum = sum(AnimationGr)
AnimationGr = [x / AnimationGrSum for x in AnimationGr] ; del AnimationGrSum
AnimationStepTime = AnimationTime / len(AnimationGr)

def Move(Window:Tk|Toplevel,dx:int|float,dy:int|float):
    Window.update()
    x,y = Window.winfo_x(),Window.winfo_y()
    for step in AnimationGr:
        st = time()
        x,y = x + dx * step,y + dy * step
        Window.geometry(f"+{int(x)}+{int(y)}")
        sleep(AnimationStepTime - min(time() - st,AnimationStepTime))

def _test():
    from ctypes import windll
    from threading import Thread
    root = Tk()
    root.title("Tkinter.Window.NonlinearMoveWindow")
    def Main():
        while True:
            v = root.winfo_screenheight() / 5
            Move(root,v,0)
            Move(root,0,v)
            Move(root,-v,0)
            Move(root,0,-v)
    Thread(target=Main,daemon=True).start()
    root.protocol("WM_DELETE_WINDOW",lambda:windll.kernel32.ExitProcess(0))
    root.mainloop()

if __name__ == "__main__":
    _test()