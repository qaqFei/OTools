from typing import Callable,Iterable,NoReturn,Any
from tkinter import Canvas,Event
from time import time,sleep
from threading import Thread

from PIL.Image import new
from PIL.ImageTk import PhotoImage

_Width = 45
_Height = 30
_animationSleeptime = 0.2
_TransParentImages = [
    new("RGBA",(_Width,_Height),color=(255,0,0,0)),
]
_ClosedImages = [
    new("RGBA",(_Width,_Height),color=(232,17,35,255)),
    new("RGBA",(_Width,_Height),color=(232,17,35,128)),
]
_MouseInImages = [
    new("RGBA",(_Width,_Height),color=(0,0,0,64)),
    new("RGBA",(_Width,_Height),color=(255,255,255,64)),
    new("RGBA",(_Width,_Height),color=(255,0,0,255)),
]
_MouseInDownImages = [
    new("RGBA",(_Width,_Height),color=(255,255,255,96)),
    new("RGBA",(_Width,_Height),color=(255,0,0,192)),
]
_MouseInImagesAnimation = [
    [new("RGBA",(_Width,_Height),color=(0,0,0,alpha)) for alpha in range(0,64+1,4)],
    [new("RGBA",(_Width,_Height),color=(255,255,255,alpha)) for alpha in range(0,64+1,4)],
    [new("RGBA",(_Width,_Height),color=(255,0,0,alpha)) for alpha in range(0,256+1,16)]
]

Imagess = []

def RgbIterToStr(value:Iterable[int]) -> str:
    strs = [hex(i).replace("0x","") for i in value]
    for i in range(len(strs)):
        if len(strs[i]) == 1:
            strs[i] = "0" + strs[i]
    return "#"+"".join(strs)

def _TryFunc(f:Callable[[],Any]) -> Any:
    try:
        return f()
    except Exception as e:
        return e

class _TitleBarButtons:
    def __init__(self,
                 focus:list[
                     Callable[[],bool],
                     Callable[[bool],None]
                 ],
                 zoomed:list[
                     Callable[[],bool],
                     Callable[[bool],None]
                 ],
                 callbacks:list[list[
                     Callable[[Event],None]
                 ]],
                 destroy:Callable[[],None],
                 move:Callable[[int|float,int|float],None]) -> None:
        self.focus = focus
        self.zoomed = zoomed
        self.callbacks = callbacks
        self._destroy = destroy
        self._move = move
        self._destroyed = False
        
    def IsFocus(self) -> bool:
        self._TestDestroyed()
        return self.focus[0]()
    
    def SetFocus(self,value:bool) -> None:
        self._TestDestroyed()
        self.focus[1](value)
        
    def Iszoomed(self) -> bool:
        self._TestDestroyed()
        return self.zoomed[0]()
    
    def Setzoomed(self,value:bool) -> None:
        self._TestDestroyed()
        self.zoomed[1](value)
    
    def Move(self,dx:int|float,dy:int|float) -> None:
        self._TestDestroyed()
        self._move(dx,dy)
        
    def Destroy(self) -> None:
        self._TestDestroyed()
        self._destroyed = True
        self._destroy()
        
    def _TestDestroyed(self) -> None|NoReturn:
        if self._destroyed:
            raise Exception("buttons already destroyed")

class _ImageDataClass:
    TransParentImage:list[PhotoImage]
    ClosedImages:list[PhotoImage]
    MouseInImages:list[PhotoImage]
    MouseInImagesAnimation:list[PhotoImage]
    MouseInDownImages:list[PhotoImage]

class _BoolDataClass:
    value:bool

def CreateTitleBarButtons(Widget:Canvas,
                          x:int|float,y:int|float,
                          commands:list[Callable,list[Callable,Callable],Callable],
                          focus_:bool=True,
                          zoomed_:bool=False) -> _TitleBarButtons:
    Images = _ImageDataClass()
    focus = _BoolDataClass()
    focus.value = focus_
    zoomed = _BoolDataClass()
    zoomed.value = zoomed_
    IsIn = [False,False,False]
    WhoAnimationing = [False,False,False]
    Imagess.append(Images)
    Images.TransParentImage = [PhotoImage(item) for item in _TransParentImages]
    Images.ClosedImages = [PhotoImage(item) for item in _ClosedImages]
    Images.MouseInImages = [PhotoImage(item) for item in _MouseInImages]
    Images.MouseInDownImages = [PhotoImage(item) for item in _MouseInDownImages]
    Images.MouseInImagesAnimation = [[PhotoImage(item_j) for item_j in item_i] for item_i in _MouseInImagesAnimation]
    Width,Height = _Width,_Height
    WidgetBindFunIdMap:dict[str,str] = {}
    destroyed = False
    NowTime = time()
    Widget._is_system_title_bar_buttons_widget = True
    Widget.create_line(
        x + Width / 2 - Width / 9,
        y + Height / 2,
        x + Width / 2 + Width / 9,
        y + Height / 2,smooth=True,
        fill="white",tag=f"Minimized_{NowTime}"
    )
    #Widget.create_rectangle(  #In Setzoomed functnion
    #    x + Width + Width / 2 - Width / 9,
    #    y + Height / 2 - Width / 9,
    #    x + Width + Width / 2 + Width / 9,
    #    y + Height / 2 + Width / 9,
    #    outline="white",tag=f"Maximized_{NowTime}"
    #)
    Widget.create_line(
        x + Width * 2 + Width / 2 - Width / 9,
        y + Height / 2 - Width / 9,
        x + Width * 2 + Width / 2 + Width / 9 + 1,
        y + Height / 2 + Width / 9 + 1,smooth=True,
        fill="white",tag=f"Closed_{NowTime}"
    )
    Widget.create_line(
        x + Width * 2 + Width / 2 + Width / 9,
        y + Height / 2 - Width / 9,
        x + Width * 2 + Width / 2 - Width / 9 - 1,
        y + Height / 2 + Width / 9 + 1,smooth=True,
        fill="white",tag=f"Closed_{NowTime}"
    )
    Widget.create_image(
        x,y,
        image=Images.TransParentImage[0],anchor="nw",
        tag=f"ShowImageMinimized_{NowTime}"
    )
    Widget.create_image(
        x + Width,y,
        image=Images.TransParentImage[0],anchor="nw",
        tag=f"ShowImageMaximized_{NowTime}"
    )
    Widget.create_image(
        x + Width * 2,y,
        image=Images.TransParentImage[0],anchor="nw",
        tag=f"ShowImageClosed_{NowTime}"
    )
    Widget.create_image(
        x,y,
        image=Images.TransParentImage[0],anchor="nw",
        tag=f"EventImageMinimized_{NowTime}"
    )
    Widget.create_image(
        x + Width,y,
        image=Images.TransParentImage[0],anchor="nw",
        tag=f"EventImageMaximized_{NowTime}"
    )
    Widget.create_image(
        x + Width * 2,y,
        image=Images.TransParentImage[0],anchor="nw",
        tag=f"EventImageClosed_{NowTime}"
    )
    
    def EventImageMinimized_Enter(e:Event,t:bool=False):
        if not t:
            Thread(target=EventImageMinimized_Enter,args=(e,True)).start()
            return ModuleNotFoundError
        IsIn[0] = True
        WhoAnimationing[0] = True
        if focus.value:
            SetFocus(focus.value)
            animationIms = Images.MouseInImagesAnimation[1] + [Images.MouseInImages[1]]
            for im in animationIms:
                WhoAnimationing[0] = True
                sleep(_animationSleeptime / len(animationIms))
                Widget.itemconfigure(f"ShowImageMinimized_{NowTime}",image=im)
                Widget.update()
        else:
            SetFocus(focus.value)
            Widget.itemconfigure(f"Minimized_{NowTime}",fill="#000000")
            animationIms = Images.MouseInImagesAnimation[0] + [Images.MouseInImages[0]]
            for im in animationIms:
                WhoAnimationing[0] = True
                sleep(_animationSleeptime / len(animationIms))
                Widget.itemconfigure(f"ShowImageMinimized_{NowTime}",image=im)
                Widget.update()
        WhoAnimationing[0] = False
    
    def EventImageMinimized_Leave(e:Event,t:bool=False):
        if not t:
            Thread(target=EventImageMinimized_Leave,args=(e,True)).start()
            return None
        if not IsIn[0]:
            return None
        if focus.value:
            SetFocus(focus.value)
            animationIms = Images.MouseInImagesAnimation[1] + [Images.MouseInImages[1]]
            animationIms = animationIms[::-1]
            for im in animationIms:
                while True:
                    if not WhoAnimationing[0]:
                        break
                    sleep(0.02)
                sleep(_animationSleeptime / len(animationIms))
                Widget.itemconfigure(f"ShowImageMinimized_{NowTime}",image=im)
                Widget.update()
        else:
            SetFocus(focus.value)
            animationIms = Images.MouseInImagesAnimation[0] + [Images.MouseInImages[0]]
            animationIms = animationIms[::-1]
            for im in animationIms:
                while True:
                    if not WhoAnimationing[0]:
                        break
                    sleep(0.02)
                sleep(_animationSleeptime / len(animationIms))
                Widget.itemconfigure(f"ShowImageMinimized_{NowTime}",image=im)
                Widget.update()
        IsIn[0] = False
    
    def EventImageMinimized_Button_1(e:Event):
        Widget.itemconfigure(f"ShowImageMinimized_{NowTime}",image=Images.MouseInDownImages[0])
        
    def EventImageMaximized_Enter(e:Event,t:bool=False):
        if not t:
            Thread(target=EventImageMaximized_Enter,args=(e,True)).start()
            return None
        IsIn[1] = True
        WhoAnimationing[1] = True
        if focus.value:
            SetFocus(focus.value)
            animationIms = Images.MouseInImagesAnimation[1] + [Images.MouseInImages[1]]
            for im in animationIms:
                WhoAnimationing[1] = True
                sleep(_animationSleeptime / len(animationIms))
                Widget.itemconfigure(f"ShowImageMaximized_{NowTime}",image=im)
                Widget.update()
        else:
            SetFocus(focus.value)
            SetMaximizedColor("#000000")
            animationIms = Images.MouseInImagesAnimation[0] + [Images.MouseInImages[0]]
            for im in animationIms:
                WhoAnimationing[1] = True
                sleep(_animationSleeptime / len(animationIms))
                Widget.itemconfigure(f"ShowImageMaximized_{NowTime}",image=im)
                Widget.update()
        WhoAnimationing[1] = False
    
    def EventImageMaximized_Leave(e:Event,t:bool=False):
        if not t:
            Thread(target=EventImageMaximized_Leave,args=(e,True)).start()
            return None
        if not IsIn[1]:
            return None
        if focus.value:
            SetFocus(focus.value)
            animationIms = Images.MouseInImagesAnimation[1] + [Images.MouseInImages[1]]
            animationIms = animationIms[::-1]
            for im in animationIms:
                while True:
                    if not WhoAnimationing[1]:
                        break
                    sleep(0.02)
                sleep(_animationSleeptime / len(animationIms))
                Widget.itemconfigure(f"ShowImageMaximized_{NowTime}",image=im)
                Widget.update()
        else:
            SetFocus(focus.value)
            animationIms = Images.MouseInImagesAnimation[0] + [Images.MouseInImages[0]]
            animationIms = animationIms[::-1]
            for im in animationIms:
                while True:
                    if not WhoAnimationing[1]:
                        break
                    sleep(0.02)
                sleep(_animationSleeptime / len(animationIms))
                Widget.itemconfigure(f"ShowImageMaximized_{NowTime}",image=im)
                Widget.update()
        IsIn[1] = False
    
    def EventImageMaximized_Button_1(e:Event):
        Widget.itemconfigure(f"ShowImageMaximized_{NowTime}",image=Images.MouseInDownImages[0])
        
    def EventImageClosed_Enter(e:Event,t:bool=False):
        if not t:
            Thread(target=EventImageClosed_Enter,args=(e,True)).start()
            return None
        IsIn[2] = True
        WhoAnimationing[2] = True
        if focus.value:
            SetFocus(focus.value)
            animationIms = Images.MouseInImagesAnimation[2] + [Images.MouseInImages[2]]
            for im in animationIms:
                WhoAnimationing[2] = True
                sleep(_animationSleeptime / len(animationIms))
                Widget.itemconfigure(f"ShowImageClosed_{NowTime}",image=im)
                Widget.update()
        else:
            SetFocus(focus.value)
            Widget.itemconfigure(f"Closed_{NowTime}",fill="#ffffff")
            animationIms = Images.MouseInImagesAnimation[2] + [Images.MouseInImages[2]]
            for im in animationIms:
                WhoAnimationing[2] = True
                sleep(_animationSleeptime / len(animationIms))
                Widget.itemconfigure(f"ShowImageClosed_{NowTime}",image=im)
                Widget.update()
        WhoAnimationing[2] = False
    
    def EventImageClosed_Leave(e:Event,t:bool=False):
        if not t:
            Thread(target=EventImageClosed_Leave,args=(e,True)).start()
            return None
        if not IsIn[2]:
            return None
        if focus.value:
            SetFocus(focus.value)
            animationIms = Images.MouseInImagesAnimation[2] + [Images.MouseInImages[2]]
            animationIms = animationIms[::-1]
            for im in animationIms:
                while True:
                    if not WhoAnimationing[2]:
                        break
                    sleep(0.02)
                sleep(_animationSleeptime / len(animationIms))
                Widget.itemconfigure(f"ShowImageClosed_{NowTime}",image=im)
                Widget.update()
        else:
            SetFocus(focus.value)
            animationIms = Images.MouseInImagesAnimation[2] + [Images.MouseInImages[2]]
            animationIms = animationIms[::-1]
            for im in animationIms:
                while True:
                    if not WhoAnimationing[2]:
                        break
                    sleep(0.02)
                sleep(_animationSleeptime / len(animationIms))
                Widget.itemconfigure(f"ShowImageClosed_{NowTime}",image=im)
                Widget.update()
        IsIn[2] = False
    
    def EventImageClosed_Button_1(e:Event):
        Widget.itemconfigure(f"ShowImageClosed_{NowTime}",image=Images.MouseInDownImages[1])
        
    WidgetBindFunIdMap.update({f"EventImageMinimized_{NowTime}":[
        Widget.tag_bind(f"EventImageMinimized_{NowTime}","<Enter>",EventImageMinimized_Enter,add=True),
        Widget.tag_bind(f"EventImageMinimized_{NowTime}","<Leave>",EventImageMinimized_Leave,add=True),
        Widget.tag_bind(f"EventImageMinimized_{NowTime}","<Button-1>",EventImageMinimized_Button_1,add=True),
        Widget.tag_bind(f"EventImageMinimized_{NowTime}","<ButtonRelease-1>",lambda e:(
            (x < e.x < x + Width and y < e.y < y + Height)
            and commands[0](),
            _TryFunc(lambda:EventImageMinimized_Leave(e))
        ),add=True)
    ]})
    
    WidgetBindFunIdMap.update({f"EventImageMaximized_{NowTime}":[
        Widget.tag_bind(f"EventImageMaximized_{NowTime}","<Enter>",EventImageMaximized_Enter,add=True),
        Widget.tag_bind(f"EventImageMaximized_{NowTime}","<Leave>",EventImageMaximized_Leave,add=True),
        Widget.tag_bind(f"EventImageMaximized_{NowTime}","<Button-1>",EventImageMaximized_Button_1,add=True),
        Widget.tag_bind(f"EventImageMaximized_{NowTime}","<ButtonRelease-1>",lambda e:(
            (x + Width < e.x < x + Width * 2 and y < e.y < y + Height)
            and (commands[1][{True:1,False:0}[zoomed.value]](),SetZoomed(not zoomed.value)),
            _TryFunc(lambda:EventImageMaximized_Leave(e))
        ),add=True)
    ]})
    
    WidgetBindFunIdMap.update({f"EventImageClosed_{NowTime}":[
        Widget.tag_bind(f"EventImageClosed_{NowTime}","<Enter>",EventImageClosed_Enter,add=True),
        Widget.tag_bind(f"EventImageClosed_{NowTime}","<Leave>",EventImageClosed_Leave,add=True),
        Widget.tag_bind(f"EventImageClosed_{NowTime}","<Button-1>",EventImageClosed_Button_1,add=True),
        Widget.tag_bind(f"EventImageClosed_{NowTime}","<ButtonRelease-1>",lambda e:(
            (x + Width * 2 < e.x < x + Width * 3 and y < e.y < y + Height)
            and commands[2](),
            _TryFunc(lambda:EventImageClosed_Leave(e))
        ),add=True)
    ]})
    
    def SetFocus(v):
        focus.value = v
        if focus.value:
            Widget.itemconfigure(f"Minimized_{NowTime}",fill="white")
            SetMaximizedColor("white")
            Widget.itemconfigure(f"Closed_{NowTime}",fill="white")
        else:
            Widget.itemconfigure(f"Minimized_{NowTime}",fill="#9B9B9B")
            SetMaximizedColor("#9B9B9B")
            Widget.itemconfigure(f"Closed_{NowTime}",fill="#9B9B9B")
    
    def SetZoomed(v):
        if destroyed:
            return None
        zoomed.value = v
        if zoomed.value:
            Widget.delete(f"Maximized_{NowTime}")
            Widget.create_rectangle(
                x + Width + Width / 2 - Width / 5 + Width / 12.5,
                y + Height / 2 - Width / 12.5,
                x + Width + Width / 2 + Width / 12.5,
                y + Height / 2 + Width / 5 - Width / 12.5,
                outline="white",tag=[f"Maximized_{NowTime}",f"Maximized_{NowTime}_Block"]
            )
            Widget.create_line(
                x + Width + Width / 2 - Width / 7.5 + Width / 12.5,
                y + Height / 2 - Width / 12.5,
                x + Width  + Width / 2 - Width / 7.5 + Width / 12.5,
                y + Height / 2 - Width / 15 - Width / 12.5,
                fill="white",tag=[f"Maximized_{NowTime}",f"Maximized_{NowTime}_Line"]
            )
            Widget.create_line(
                x + Width + Width / 2 + Width / 12.5,
                y + Height / 2 + Width / 7.5 - Width / 12.5,
                x + Width + Width / 2 + Width / 12.5 + Width / 15 + 1,
                y + Height / 2 + Width / 7.5 - Width / 12.5,
                fill="white",tag=[f"Maximized_{NowTime}",f"Maximized_{NowTime}_Line"]
            )
            Widget.create_line(
                x + Width  + Width / 2 - Width / 7.5 + Width / 12.5,
                y + Height / 2 - Width / 15 - Width / 12.5,
                x + Width + Width / 2 + Width / 15 + Width / 12.5,
                y + Height / 2 - Width / 15 - Width / 12.5,
                fill="white",tag=[f"Maximized_{NowTime}",f"Maximized_{NowTime}_Line"]
            )
            Widget.create_line(
                x + Width + Width / 2 + Width / 15 + Width / 12.5,
                y + Height / 2 - Width / 15 - Width / 12.5,
                x + Width + Width / 2 + Width / 15 + Width / 12.5,
                y + Height / 2 + Width / 7.5 - Width / 12.5,
                fill="white",tag=[f"Maximized_{NowTime}",f"Maximized_{NowTime}_Line"]
            )
        else:
            Widget.delete(f"Maximized_{NowTime}")
            Widget.create_rectangle(
                x + Width + Width / 2 - Width / 9,
                y + Height / 2 - Width / 9,
                x + Width + Width / 2 + Width / 9,
                y + Height / 2 + Width / 9,
                outline="white",tag=f"Maximized_{NowTime}"
            )
        Widget.tag_raise(f"EventImageMinimized_{NowTime}")
        Widget.tag_raise(f"EventImageMaximized_{NowTime}")
        Widget.tag_raise(f"EventImageClosed_{NowTime}")
    
    def SetMaximizedColor(v):
        if zoomed.value:
            Widget.itemconfigure(f"Maximized_{NowTime}_Block",outline=v)
            Widget.itemconfigure(f"Maximized_{NowTime}_Line",fill=v)
        else:
            Widget.itemconfigure(f"Maximized_{NowTime}",outline=v)
    
    def destroy():
        nonlocal destroyed
        for tag in WidgetBindFunIdMap.keys():
            for func_id in WidgetBindFunIdMap[tag]:
                Widget.tag_unbind(tag,func_id)
        WidgetBindFunIdMap.clear()
        for tag in [
            f"Minimized_{NowTime}",
            f"Maximized_{NowTime}",
            f"Closed_{NowTime}",

            f"ShowImageMinimized_{NowTime}",
            f"ShowImageMaximized_{NowTime}",
            f"ShowImageClosed_{NowTime}",

            f"EventImageMinimized_{NowTime}",
            f"EventImageMaximized_{NowTime}",
            f"EventImageClosed_{NowTime}"
        ]:
            Widget.delete(tag)
        destroyed = True
    
    def move(dx:int|float,dy:int|float):
        nonlocal x,y
        x += dx
        y += dy
        for tag in [
            f"Minimized_{NowTime}",
            f"Maximized_{NowTime}",
            f"Closed_{NowTime}",

            f"ShowImageMinimized_{NowTime}",
            f"ShowImageMaximized_{NowTime}",
            f"ShowImageClosed_{NowTime}",

            f"EventImageMinimized_{NowTime}",
            f"EventImageMaximized_{NowTime}",
            f"EventImageClosed_{NowTime}"
        ]:
            Widget.move(tag,dx,dy)
    
    SetFocus(focus.value)
    SetZoomed(zoomed.value)
    
    Widget.tag_raise(f"Minimized_{NowTime}",f"ShowImageMinimized_{NowTime}")
    Widget.tag_raise(f"Maximized_{NowTime}",f"ShowImageMaximized_{NowTime}")
    Widget.tag_raise(f"Closed_{NowTime}",f"ShowImageClosed_{NowTime}")
    Widget.tag_raise(f"EventImageMinimized_{NowTime}")
    Widget.tag_raise(f"EventImageMaximized_{NowTime}")
    Widget.tag_raise(f"EventImageClosed_{NowTime}")
    
    return _TitleBarButtons([lambda:focus.value,SetFocus],[lambda:zoomed.value,SetZoomed],[
        [
            EventImageMinimized_Enter,
            EventImageMinimized_Leave,
            EventImageMinimized_Button_1
        ],
        [
            EventImageMaximized_Enter,
            EventImageMaximized_Leave,
            EventImageMaximized_Button_1
        ],
        [
            EventImageClosed_Enter,
            EventImageClosed_Leave,
            EventImageClosed_Button_1
        ]
    ],destroy,move)

def _test():
    global canvas
    from tkinter import Tk
    root = Tk()
    root.update()
    canvas = Canvas(root,bg="#0078d7",highlightthickness=0)
    canvas.place(x=0,y=0)
    canvas.update()
    Titbar = CreateTitleBarButtons(canvas,0,0,commands=[root.iconify,[lambda:root.state("zoom"),lambda:root.state("normal")],root.destroy])
    root.bind("<Configure>",lambda e:exec(f"canvas[\"width\"] = e.width ; canvas[\"height\"] = e.height"),add=True)
    root.bind("<FocusIn>",lambda e:(Titbar.SetFocus(True),canvas.configure(bg="#0078d7")),add=True)
    root.bind("<FocusOut>",lambda e:(Titbar.SetFocus(False),canvas.configure(bg="white")),add=True)
    root.mainloop()

if __name__ == "__main__":
    _test()