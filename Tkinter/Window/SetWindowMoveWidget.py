from typing import Any,Callable
from tkinter import Tk,Toplevel,Event,Misc,IntVar
from warnings import warn

import SystemTitleBarButtons

IsWarning = True

class _MoveItemCallBacks:
    def __init__(self,
                 Window:Tk|Toplevel,
                 dxVar:IntVar,
                 dyVar:IntVar,
                 MoveCallBack:Callable[[int,int,Tk|Toplevel],Any],
                 MoveWidget:Misc) -> None:
        self.Window = Window
        self.dx = dxVar
        self.dy = dyVar
        self.lastx = 0.0
        self.lasty = 0.0
        self.MoveCallBack = MoveCallBack
        self.MoveWidget = MoveWidget
        self._is_move = True
    def Button_1_Down(self,event:Event) -> None:
        self.lastx = event.x
        self.lasty = event.y
        self._is_move = True
        if hasattr(self.MoveWidget,"_is_system_title_bar_buttons_widget"):
            if event.y <= SystemTitleBarButtons._Height and event.x >= self.MoveWidget.winfo_width() - SystemTitleBarButtons._Width * 3:
                self._is_move = False
        if hasattr(self.MoveWidget,"_window_change_size_frame_cursor_style"):
            self._is_move = False
    def Button_1_Move(self,event:Event) -> None:
        self.dx.set(self.dx.get() + (event.x - self.lastx))
        self.dy.set(self.dy.get() + (event.y - self.lasty))
        self.lastx = event.x - self.dx.get()
        self.lasty = event.y - self.dy.get()
        if self._is_move:
            self.MoveCallBack(self.dx.get(),self.dy.get(),self.Window)
        self.dx.set(0.0)
        self.dy.set(0.0)
    def Button_1_Up(self,event:Event) -> None:
        self.lastx = 0.0
        self.lasty = 0.0
        self._is_move = True
        
def _WindowMoveCallBack(dx:int,dy:int,Window:Tk|Toplevel) -> None:
    Window.update()
    Window.geometry(f"+{Window.winfo_x() + dx}+{Window.winfo_y() + dy}")
        
def SetWindowMoveWidget(Window:Tk|Toplevel,MoveWidget:Misc) -> _MoveItemCallBacks:
    if IsWarning and id(Window) == id(MoveWidget):
        warn("MoveWidget is Window,So this may cause a decrease in the smoothness of movement.")
    dxVar = IntVar(Window,value=0.0)
    dyVar = IntVar(Window,value=0.0)
    CallBacks = _MoveItemCallBacks(Window,dxVar,dyVar,_WindowMoveCallBack,MoveWidget)
    MoveWidget.bind("<ButtonPress-1>",CallBacks.Button_1_Down,add=True)
    MoveWidget.bind("<B1-Motion>",CallBacks.Button_1_Move,add=True)
    MoveWidget.bind("<ButtonRelease-1>",CallBacks.Button_1_Up,add=True)
    return CallBacks

def _test():
    from tkinter import Canvas
    root = Tk()
    root.title("Tkinter.Window.SetWindowMoveWidget")
    root.resizable(False,False)
    canvas = Canvas(root,width=400,height=400)
    canvas.create_text(200,200,text="可拖动")
    canvas.pack()
    SetWindowMoveWidget(root,canvas)
    root.mainloop()

if __name__ == "__main__":
    _test()
    