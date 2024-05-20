from typing import Callable,Mapping,Any
from tkinter import Tk,Toplevel,Canvas,Event
from tkinter.font import Font
from threading import Thread
from time import sleep,time
from ctypes import windll
from random import randint

from keyboard import add_hotkey
from PIL import Image,ImageTk
from PyQt6.QtWidgets import QMenu,QMainWindow,QApplication
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QPoint
from win32con import *
import pyautogui

import SystemTitleBarButtons
import ZoomEffect ; ZoomEffect
import NonlinearCloseOpenEffect
import SetWindowMoveWidget
import IconifyEffect
import AddWindowChangeSizeFrame

NullFunc = eval(f"lambda:{randint(0,2**31)}")
windll.gdi32.AddFontResourceW("./_font.ttf")
_menu_qt_application = QApplication([])
_menu_window = QMainWindow()
pyautogui.PAUSE = 0

class SystemTitleBar:
    def __init__(self,
                 master:Tk|Toplevel,
                 activeColor:str,
                 noactiveColor:str,
                 w:int,h:int,x:int,y:int,
                 icon:Image.Image,title:str,
                 titleFont:Any|Font=("荆南麦圆体"),
                 exit_call:Callable[[],Any]=NullFunc,
                 placeKwrags:Mapping={},
                 activeTextColor:str="#FFFFFF",
                 noactiveTextColor:str="#888888") -> None:
        self.last_zoom_or_normal_time = -float("inf")
        self._zoom_call = lambda self=self:[self.commands[1][0](),self.set_zoomed(True),exec("self.last_zoom_or_normal_time = time()")] if sleep(randint(0,1000)/10000) is None and time() - self.last_zoom_or_normal_time > NonlinearCloseOpenEffect.EffectTime * 2 else None
        self._normal_call = lambda self=self:[self.commands[1][1](),self.set_zoomed(False),exec("self.last_zoom_or_normal_time = time()")] if sleep(randint(0,1000)/10000) is None and time() - self.last_zoom_or_normal_time > NonlinearCloseOpenEffect.EffectTime * 2 else None
        self._iconify_call = lambda self=self:[self.commands[0](),exec("self.last_zoom_or_normal_time = time()")] if sleep(randint(0,1000)/10000) is None and time() - self.last_zoom_or_normal_time > NonlinearCloseOpenEffect.EffectTime * 2 else None
        self.master = master ; self.master.update()
        self.hwnd = int(self.master.frame(),16)
        self.icon = icon
        self.title = title
        self.w,self.h = w,h
        self.x,self.y = x,y
        self.titleFont = titleFont
        self.zoomed = False
        self.focus = True
        self.zoom_rect = (self.master.winfo_x(),self.master.winfo_y(),self.master.winfo_width(),self.master.winfo_height())
        self.zoom_full = True
        self.frame_width = 5
        self.frame_move_lastpos = [None,None,None]
        self.frames = [Canvas(self.master,highlightthickness=0) for i in [None]*4]
        self.commands = [lambda self=self:Thread(target=IconifyEffect.ShowIconifyEffect,args=(self.master,self.icon)).start(),
                            [
                                lambda self=self:_ZoomCall(self),
                                lambda self=self:_NormalCall(self)
                            ],
                        exit_call]
        self._exit = self.commands[-1]
        self.commands[-1] = lambda:_ExitCall(self)
        self.activeColor = activeColor
        self.noactiveColor = noactiveColor
        self.activeTextColor = activeTextColor
        self.noactiveTextColor = noactiveTextColor
        self.canvas = Canvas(
            self.master,
            width=w,height=h,
            bg=self.activeColor,
            highlightthickness=0
        ) ; self.canvas.place(x = x,y = y,
                              **placeKwrags) ; self.canvas.update()
        self._draw()
        self.canvas.bind("<Double-Button-1>",lambda e:{
            True:self._zoom_call,
            False:self._normal_call
        }[not self.zoomed](),add=True)
        self.master.bind("<Configure>",lambda e:[self.set_size(self.master.winfo_width(),self.h)],add=True)
        self.master.bind("<FocusIn>",lambda e:self.set_focus(True),add=True)
        self.master.bind("<FocusOut>",lambda e:self.set_focus(False),add=True)
        #self.canvas.tag_bind("SystemTitleBar-icon","<Double-Button-1>",lambda e:self.commands[-1](),add=True)
        self.master.protocol("WM_DELETE_WINDOW",self.commands[-1])
        add_hotkey("win+up",lambda:{
            True:lambda:None,
            False:self._zoom_call,
        }[self.zoomed]() if self.focus else None)
        add_hotkey("win+down",lambda:{
            True:self._normal_call,
            False:self._iconify_call
        }[self.zoomed]() if self.focus else None)
        SetWindowMoveWidget.SetWindowMoveWidget(self.master,self.canvas)
        self.master.configure(highlightthickness=self.frame_width,highlightbackground=self.noactiveColor,highlightcolor=self.activeColor)
        #self._remove_system_titlebar()
        AddWindowChangeSizeFrame.AddWindowChangeSizeFrame(self.master,self.frame_width)
        self._create_menu()
        Thread(target=self._loop,daemon=True).start()
    
    def _create_menu(self) -> None:
        self._menu = QMenu()
        self._menu_actions = [
            QAction("还原(&R)",_menu_window),
            QAction("最小化(&N)",_menu_window),
            QAction("最大化(&X)",_menu_window),
            QAction("关闭(&C)",_menu_window),
        ]
        self._menu_actions[3].setShortcut("Alt+f4")
        self._menu_actions[0].triggered.connect(lambda:Thread(target=lambda:[self._normal_call(),self.buttons.Setzoomed(False)]).start())
        self._menu_actions[1].triggered.connect(lambda:Thread(target=self._iconify_call).start())
        self._menu_actions[2].triggered.connect(lambda:Thread(target=lambda:[self._zoom_call(),self.set_zoomed(True)]).start())
        self._menu_actions[3].triggered.connect(self.commands[-1])
        self._menu.addActions(self._menu_actions)
        self._menu_state_1()
        self.canvas.bind("<Button-3>",self._pop_menu,add=True)

    def _menu_state_1(self) -> None:
        self._menu_actions[0].setEnabled(False)
        self._menu_actions[1].setEnabled(True)
        self._menu_actions[2].setEnabled(True)
        self._menu_actions[3].setEnabled(True)

    def _menu_state_2(self) -> None:
        self._menu_actions[0].setEnabled(True)
        self._menu_actions[1].setEnabled(True)
        self._menu_actions[2].setEnabled(False)
        self._menu_actions[3].setEnabled(True)
    
    def _pop_menu(self,e:Event) -> None:
        if self.buttons.Iszoomed():
            self._menu_state_2()
        else:
            self._menu_state_1()
        self._menu.popup(QPoint(e.x_root,e.y_root))

    def _remove_system_titlebar(self) -> None:
        style = windll.user32.GetWindowLongPtrW(self.hwnd,GWL_STYLE)
        style = style & ~WS_CAPTION
        style = style & ~WS_SYSMENU
        style = style & ~WS_MINIMIZEBOX
        style = style & ~WS_MAXIMIZEBOX
        windll.user32.SetWindowLongPtrW(self.hwnd,GWL_STYLE, style)
        windll.user32.SetWindowPos(
            self.hwnd,0,0,0,0,0,
            SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_FRAMECHANGED | SWP_SHOWWINDOW
        )

    def _draw(self) -> None:
        self.canvas.update()
        try:self.buttons.Destroy()
        except AttributeError:pass
        self._icon = ImageTk.PhotoImage(self.icon.resize((int(self.h * 0.85),)*2))
        self.canvas.delete("all")
        self.canvas.create_image(
            self.h / 2,self.h / 2,
            image=self._icon,tag="SystemTitleBar-icon"
        )
        self.canvas.create_text(
            self.h,self.h / 2,
            text=self.title,font=self.titleFont,
            fill=self.activeTextColor,anchor="w",
            tag="SystemTitleBar-text"
        )
        self.buttons = SystemTitleBarButtons.CreateTitleBarButtons(
            self.canvas,
            self.w - SystemTitleBarButtons._Width * 3 - self.frame_width * 2,0,
            self.commands,self.focus,self.zoomed
        )

    def _loop(self) -> None:
        while True:
            sleep(1 / 5)
            self.zoomed = self.buttons.Iszoomed()

    def set_pos(self,x:int,y:int) -> None:
        self.canvas.place_forget()
        self.canvas.place(x=x,y=y)

    def set_size(self,w:int,h:int) -> None:
        wh_bak = (self.w,self.h)
        self.canvas.config(width=w-self.frame_width,height=h)
        self.w,self.h = w,h
        self.buttons.Move(
            self.w - wh_bak[0],
            self.h - wh_bak[1]
        )

    def set_focus(self,focus:bool) -> None:
        self.focus = focus
        if self.focus:
            self.canvas["bg"] = self.activeColor
            self.canvas.itemconfig("SystemTitleBar-text",fill=self.activeTextColor)
        else:
            self.canvas["bg"] = self.noactiveColor
            self.canvas.itemconfig("SystemTitleBar-text",fill=self.noactiveTextColor)
        self.buttons.SetFocus(self.focus)

    def set_zoomed(self,zoomed:bool) -> None:
        self.zoomed = zoomed
        self.buttons.Setzoomed(self.zoomed)
        
    def showopeneffect(self) -> None:
        NonlinearCloseOpenEffect.ShowOpenEffect(self.master)

def _ZoomCall(self:SystemTitleBar):
    ZoomThread = Thread(target=lambda self=self: exec("self.zoom_rect = ZoomEffect.ShowZoomEffect(self.master,self.zoom_full)"))
    ZoomThread.start()
    self.set_size(self.master.winfo_screenwidth(),self.h)

def _NormalCall(self:SystemTitleBar):
    NormalThread = Thread(target=lambda self=self: exec("ZoomEffect.ShowNormalEffect(self.master,self.zoom_rect)"))
    NormalThread.start()
    self.master.update()
    self.set_size(self.master.winfo_width(),self.h)

def _ExitCall(self:SystemTitleBar,thread:bool=False):
    if not thread:
        Thread(target=_ExitCall,args=(self,True)).start()
        return None
    NonlinearCloseOpenEffect.ShowCloseEffect(self.master)
    self.master.quit()
    self._exit()

def _test():
    global w,h,root,tb
    from PIL import Image
    from ctypes import windll
    import _Widgets
    root = Tk()
    root.overrideredirect(True)
    root.attributes("-alpha",0.0)
    root["bg"] = "#f0f0f0"
    root.update()
    tb = SystemTitleBar(root,"#0078d7","#FFFFFF",
                        root.winfo_width(),30,0,0,Image.open("_imageres_15.ico"),
                        "Hello World!",exit_call=lambda:windll.kernel32.ExitProcess(0))
    tb.canvas.pack()
    s = 0.65
    w,h = int(root.winfo_screenwidth() * s),int(root.winfo_screenheight() * s)
    root.geometry(f"{w}x{h}+{int(root.winfo_screenwidth()/2-w/2)}+{int(root.winfo_screenheight()/2-h/2)}")
    root.bind("<Configure>",lambda e:Thread(target=lambda:exec(f"global w,h ; w,h = root.winfo_width(),root.winfo_height()")).start(),add=True)
    root.update()
    def _create_widget():
        global web
        web = _Widgets.VideoPlayer(
            root,"./../Widget/test.mp4",
            root.winfo_width()-tb.frame_width*2,root.winfo_height()-30-tb.frame_width*2,
            tb.frame_width,30 + tb.frame_width
        )
        root.bind("<Configure>",lambda e:web.resize(root.winfo_width()-tb.frame_width*2,root.winfo_height()-30-tb.frame_width*2),add=True)
        Thread(target=tb.showopeneffect).start()
    Thread(target=_create_widget).start()
    while True:
        try:
            root.mainloop()
        except:
            pass

if __name__ == "__main__":
    _test()