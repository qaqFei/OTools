from tkinter import Tk,Toplevel
from threading import Thread
from math import cos,pi
from time import time,sleep

from win32api import GetMonitorInfo,MonitorFromPoint

monitor_info = GetMonitorInfo(MonitorFromPoint((0,0)))
_TaskBarHeight = monitor_info.get("Monitor")[3]-monitor_info.get("Work")[3] ; del monitor_info
AnimationTime = 0.75
AnimationFps = 60
AnimationGrX = int(AnimationFps * AnimationTime) + 1
z = 0.5
AnimationGr = [z * cos(x / AnimationGrX * pi) + z for x in range(0,AnimationGrX)] ; del z
AnimationGrSum = sum(AnimationGr)
AnimationGr = [x / AnimationGrSum for x in AnimationGr] ; del AnimationGrSum
AnimationStepTime = AnimationTime / len(AnimationGr)
offset_zoom = AnimationTime / 6
offset_normal = AnimationTime / 3

def ShowZoomEffect(Window:Tk|Toplevel,ToTaskBar:bool=False) -> tuple[int,int,int,int]:
    Window.update()
    ThisRect = (Window.winfo_width(),Window.winfo_height(),Window.winfo_x(),Window.winfo_y())
    _Rect = list(ThisRect)
    dx_1 = Window.winfo_screenwidth() / 2 - ThisRect[2] - ThisRect[0] / 2
    dy_1 = Window.winfo_screenheight() / 2 - ThisRect[3] - ThisRect[1] / 2
    dx_2 = - (Window.winfo_screenwidth() / 2 - ThisRect[0] / 2)
    dy_2 = - (Window.winfo_screenheight() / 2 - ThisRect[1] / 2)
    dw_1 = Window.winfo_screenwidth() - ThisRect[0]
    dh_1 = Window.winfo_screenheight() - ThisRect[1]
    def _f1():
        for step in AnimationGr:
            st = time()
            _Rect[2] += dx_1 * step
            _Rect[3] += dy_1 * step
            Window.geometry(f"{int(_Rect[0])}x{int(_Rect[1])}+{int(_Rect[2])}+{int(_Rect[3])}")
            sleep(AnimationStepTime - min(st - time(),AnimationStepTime))
    def _f2():
        for step in AnimationGr:
            st = time()
            _Rect[2] += dx_2 * step
            _Rect[3] += dy_2 * step
            _Rect[0] += dw_1 * step
            _Rect[1] += dh_1 * step
            Window.geometry(f"{int(_Rect[0])}x{int(_Rect[1])}+{int(_Rect[2])}+{int(_Rect[3])}")
            sleep(AnimationStepTime - min(st - time(),AnimationStepTime))
    threads = [Thread(target=_f1),Thread(target=_f2)]
    threads[0].start()
    sleep(offset_zoom)
    threads[1].start()
    for thread in threads:
        thread.join()
    Window.state("zoom")
    return ThisRect

def ShowNormalEffect(Window:Tk|Toplevel,Target:tuple[int,int,int,int]):
    Window.state("normal")
    Window.update()
    ThisRect = Target
    _Rect = [Window.winfo_width(),Window.winfo_height(),0,0]
    dx_1 = - (Window.winfo_screenwidth() / 2 - ThisRect[0] / 2 - ThisRect[2])
    dy_1 = - (Window.winfo_screenheight() / 2 - ThisRect[1] / 2 - ThisRect[3])
    dx_2 = Window.winfo_screenwidth() / 2 - ThisRect[0] / 2
    dy_2 = Window.winfo_screenheight() / 2 - ThisRect[1] / 2
    dw_1 =   - (Window.winfo_width() - ThisRect[0])
    dh_1 =   - (Window.winfo_height() - ThisRect[1])
    def _f1():
        for step in AnimationGr:
            st = time()
            _Rect[2] += dx_1 * step
            _Rect[3] += dy_1 * step
            Window.geometry(f"{int(_Rect[0])}x{int(_Rect[1])}+{int(_Rect[2])}+{int(_Rect[3])}")
            sleep(AnimationStepTime - min(st - time(),AnimationStepTime))
    def _f2():
        for step in AnimationGr:
            st = time()
            _Rect[2] += dx_2 * step
            _Rect[3] += dy_2 * step
            _Rect[0] += dw_1 * step
            _Rect[1] += dh_1 * step
            Window.geometry(f"{int(_Rect[0])}x{int(_Rect[1])}+{int(_Rect[2])}+{int(_Rect[3])}")
            sleep(AnimationStepTime - min(st - time(),AnimationStepTime))
    threads = [Thread(target=_f2),Thread(target=_f1)]
    for thread in threads:
        thread.start()
        sleep(offset_normal)
    for thread in threads:
        thread.join()

def _test():
    from tkinter.ttk import Button
    from threading import Thread
    import SetWindowMoveWidget
    root = Tk()
    root.overrideredirect(True)
    SetWindowMoveWidget.SetWindowMoveWidget(root,root)
    w,h = int(root.winfo_screenwidth() * 0.2),int(root.winfo_screenheight() * 0.2)
    root.geometry(f"{w}x{h}")
    rect = (root.winfo_x(),root.winfo_y(),root.winfo_width(),root.winfo_height())
    Button(root,text="ZoomEffect",command=lambda:Thread(target=lambda root=root:exec("global rect ; rect = ShowZoomEffect(root,False)")).start()).place(x=0,y=0,width=w,height=int(h/2))
    Button(root,text="NormalEffect",command=lambda:Thread(target=lambda root=root:exec("ShowNormalEffect(root,rect)")).start()).place(x=0,y=int(h/2)-1,width=w,height=int(h/3))
    root.mainloop()

if __name__ == "__main__":
    _test()