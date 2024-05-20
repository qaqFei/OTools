from tkinter import Tk,Toplevel,Canvas
from threading import Thread
from time import time,sleep
from math import cos,pi
from random import randint

from PIL import Image,ImageTk

import SetWindowMoveWidget

IconWindows = {}
IconTemps = {}
IconWindowCanvasTransparentBackgroundColor = "#000001"
IconWindowCanvasSize = 150
EffectTime = 0.35
EffectFps = 60
EffectGrX = int(EffectFps * EffectTime) + 1
z = 0.5
EffectGr = [z * cos(x / EffectGrX * pi) + z for x in range(0,EffectGrX)] ; del z
EffectGrSum = sum(EffectGr)
EffectGr = [x / EffectGrSum for x in EffectGr] ; del EffectGrSum
EffectStepTime = EffectTime / len(EffectGr)

def ShowIconifyEffect(Window:Tk|Toplevel,Icon:Image.Image) -> int:
    for x in range(Icon.width):
        for y in range(Icon.height):
            pixel = Icon.getpixel((x,y))
            if pixel[-1] < 255 and sum(pixel[:3]) != 0:
                Icon.putpixel((x,y),(0,0,0,0))
    state = Window.state()
    Window.state("normal")
    Window.update()
    to_screen_frame = 50
    yx,yy,yw,yh = Window.winfo_x(),Window.winfo_y(),Window.winfo_width(),Window.winfo_height()
    target_rect = (
        to_screen_frame,
        Window.winfo_screenheight() - to_screen_frame * 2,
        to_screen_frame,to_screen_frame
    )
    dx,dy,dw,dh = (
        target_rect[0] - yx,
        target_rect[1] - yy,
        target_rect[2] - yw,
        target_rect[3] - yh
    )
    x,y,w,h = yx,yy,yw,yh
    alpha = 1.0
    for step in EffectGr:
        start_time = time()
        alpha -= step * 1.0
        x,y,w,h = (
            x + dx * step,
            y + dy * step,
            w + dw * step,
            h + dh * step
        )
        Window.attributes("-alpha",alpha)
        Window.geometry(f"{int(w)}x{int(h)}+{int(x)}+{int(y)}")
        sleep(EffectStepTime - min(EffectStepTime,time() - start_time))
    Window.withdraw()
    Window.geometry(f"{yw}x{yh}+{yx}+{yy}")
    Window.attributes("-alpha",1.0)
    IconWindow_id = randint(0,2**31)
    IconWindow = Toplevel()
    IconWindow.geometry("+65536+65536")
    IconWindow.withdraw()
    IconWindow.geometry(f"+{int(target_rect[0])}+{int(target_rect[1]-IconWindowCanvasSize)}")
    IconWindows.update({IconWindow_id:IconWindow})
    IconWindow["bg"] = IconWindowCanvasTransparentBackgroundColor
    IconWindow.attributes("-transparentcolor",IconWindowCanvasTransparentBackgroundColor)
    IconWindow.protocol("WM_DELETE_WINDOW",lambda:None)
    IconCanvas = Canvas(IconWindow,width=IconWindowCanvasSize,height=IconWindowCanvasSize,highlightthickness=0,background=IconWindowCanvasTransparentBackgroundColor)
    IconCanvas.pack()
    IconCanvasIconSize = 0.0
    IconWindow.update() ; IconCanvas.update()
    IconCanvasShowIconLastId = None
    alpha = 0.0
    ims = []
    for step in EffectGr:
        IconCanvasIconSize += IconWindowCanvasSize * step
        temp = Icon.resize((int(IconCanvasIconSize),int(IconCanvasIconSize)))
        for x in range(temp.width):
            for y in range(temp.height):
                pixel = temp.getpixel((x,y))
                if pixel[-1] < 255 and sum(pixel[:3]) != 0:
                    temp.putpixel((x,y),(0,0,0,0))
        ims.append(ImageTk.PhotoImage(temp))
    IconWindow.overrideredirect(True)
    IconWindow.deiconify()
    i = -1
    for step in EffectGr:
        start_time = time()
        i += 1
        alpha += step * 1.0
        ThisIconId = IconCanvas.create_image(IconWindowCanvasSize/2,IconWindowCanvasSize/2,image=ims[i])
        IconWindow.update() ; IconCanvas.update()
        if IconCanvasShowIconLastId is not None:
            IconCanvas.delete(IconCanvasShowIconLastId)
        IconCanvasShowIconLastId = ThisIconId
        IconWindow.attributes("-alpha",alpha)
        IconWindow.update() ; IconCanvas.update()
        sleep(EffectStepTime - min(EffectStepTime,time() - start_time))
    image_pos_start = (IconWindowCanvasSize/2-ims[-1].width()/2,IconWindowCanvasSize/2-ims[-1].height()/2)
    image_pos_end = (IconWindowCanvasSize/2+ims[-1].width()/2,IconWindowCanvasSize/2+ims[-1].height()/2)
    button_event_lasttime = -float("inf")
    def b1_event_callback(e):
        nonlocal button_event_lasttime
        button_event_lasttime = time()
    IconCanvas.bind("<Button-1>",b1_event_callback,add=True)
    IconCanvas.bind("<ButtonRelease-1>",lambda e:{
        True:lambda:Thread(target=ShowDeiconifyEffect,args=(Window,IconWindow_id)).start(),
        False:lambda:None
    }[image_pos_start[0] < e.x < image_pos_end[0] and image_pos_start[1] < e.y < image_pos_end[1] and time() - button_event_lasttime < 0.2](),add=True)
    IconTemps.update({IconWindow_id:ims})
    SetWindowMoveWidget.SetWindowMoveWidget(IconWindow,IconCanvas)
    IconWindow._parent_state = state
    return IconWindow_id

def ShowDeiconifyEffect(Window:Tk|Toplevel,IconWindowId:int):
    Window.attributes("-alpha",0.0)
    Window.deiconify()
    Window.update()
    target_rect = (Window.winfo_width(),Window.winfo_height(),Window.winfo_x(),Window.winfo_y())
    IconWindow:Tk|Toplevel = IconWindows[IconWindowId]
    yx,yy,yw,yh = (
        IconWindow.winfo_x(),IconWindow.winfo_y(),
        IconWindow.winfo_width(),IconWindow.winfo_height()
    )
    dx,dy,dw,dh = (
        target_rect[2] - yx,
        target_rect[3] - yy,
        target_rect[0] - yw,
        target_rect[1] - yh
    )
    x,y,w,h = yx,yy,yw,yh
    alpha = 0.0
    Window.focus_force()
    IconWindow.destroy()
    for step in EffectGr:
        start_time = time()
        alpha += step * 1.0
        x,y,w,h = (
            x + dx * step,
            y + dy * step,
            w + dw * step,
            h + dh * step
        )
        Window.attributes("-alpha",alpha)
        Window.geometry(f"{int(w)}x{int(h)}+{int(x)}+{int(y)}")
        sleep(EffectStepTime - min(EffectStepTime,time() - start_time))
    Window.geometry(f"{target_rect[0]}x{target_rect[1]}+{target_rect[2]}+{target_rect[3]}")
    Window.attributes("-alpha",1.0)
    Window.state(IconWindow._parent_state)
    del IconWindows[IconWindowId]

def _test():
    global ICON
    from tkinter.ttk import Button
    from threading import Thread
    import SetWindowMoveWidget
    ICON = Image.open("_imageres_15.ico")
    root = Tk()
    SetWindowMoveWidget.SetWindowMoveWidget(root,root)
    root.overrideredirect(True)
    root.geometry(f"{int(root.winfo_screenwidth() * 0.75)}x{int(root.winfo_screenheight() * 0.75)}")
    Button(root,text="ShowEffect",command=lambda:Thread(target=lambda:(ShowIconifyEffect(root,ICON))).start()).pack()
    root.mainloop()

if __name__ == "__main__":
    _test()