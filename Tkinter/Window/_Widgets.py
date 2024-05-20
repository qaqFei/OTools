from tkinter import Tk,Toplevel,Canvas,Event as tk_Event
from threading import Thread,current_thread
from time import time,sleep
from math import cos,pi
from random import randint
from ctypes import windll
import typing

from PIL import Image,ImageTk,ImageDraw
import webview as _webview
import webview.errors as _webview_errors
import win32con

import _TkinterImageDrawOptimize

_webs:list[_webview.Window] = []

def _Get_AnimationGr(
    AnimationTime:float,
    AnimationFps:int
) -> tuple[float,list[float]]:
        AnimationGrX = int(AnimationFps * AnimationTime) + 1
        AnimationGr = [0.5 * cos(x / AnimationGrX * pi) + 0.5 for x in range(0,AnimationGrX)]
        AnimationGrSum = sum(AnimationGr)
        AnimationGr = [x / AnimationGrSum for x in AnimationGr] ; del AnimationGrSum
        AnimationStepTime = AnimationTime / len(AnimationGr)
        return AnimationStepTime,AnimationGr

def _Get_EllipseImg(
    r:int,
    color:tuple[int]
) -> Image.Image:
    frame = int(r / 10)
    result = Image.new("RGBA",(r*2+frame*2,)*2,(0,0,0,0))
    draw_obj = ImageDraw.Draw(result)
    draw_obj.ellipse((frame,frame,r*2,r*2),fill=color)
    return result

def ban_threadtest_current_thread():
    obj = current_thread()
    obj.name = "MainThread"
    return obj

def WebViewWidgetExitCall(w:Tk|Toplevel):
    for web in _webs:
        web.destroy()
    w.destroy()

def _setTimeout(
    func:typing.Callable,
    timeout:float
):
    timeout /= 1000
    Thread(target=lambda:(sleep(timeout),func()),daemon=True).start()

class Carousel(Canvas):
    def __init__(
        self,
        images:list[Image.Image],
        img_size:tuple[int]|None = None,
        OptimizeRenderMissX:int|float = 2,
        *args,
        **kwargs
    ):
        self._OptimizeRenderMissX = OptimizeRenderMissX
        self._images = images
        if img_size is not None:
            self._images = [item.resize(img_size) for item in self._images]
        if len({item.size for item in self._images}) != 1:
            raise ValueError("All images must be of the same size")
        self._moving = False
        self._images = [ImageTk.PhotoImage(_TkinterImageDrawOptimize.OptimizeRenderMiss(item,self._OptimizeRenderMissX)) for item in self._images]
        self._CarouselIndex = 0
        self._AnimationTime = 1.0
        self._AnimationStepTime,self._AnimationGr = _Get_AnimationGr(self._AnimationTime,120)
        self._ButtonImgSize = int(self._images[0].width() / self._OptimizeRenderMissX / 12.5)
        self._IndexImgSize = int(self._ButtonImgSize / 3.75)
        self._IndexInImg = ImageTk.PhotoImage(_Get_EllipseImg(self._IndexImgSize,(255,255,255,216)).resize((self._IndexImgSize,)*2))
        self._IndexOutImg = ImageTk.PhotoImage(_Get_EllipseImg(self._IndexImgSize,(0,0,0,128)).resize((self._IndexImgSize,)*2))
        Canvas.__init__(self,*args,**kwargs)
        self._CanvasWidth = self._images[0].width() / self._OptimizeRenderMissX
        self._CanvasHeight = self._images[0].height() / self._OptimizeRenderMissX
        self.configure(
            width=self._CanvasWidth,
            height=self._CanvasHeight
        )
        self._draw_indeximg()
        self._draw_img(mode=2)

    def start(
        self,
        interval:float=1.5,
        _first_of_all:bool=True
    ):
        if _first_of_all:
            self._draw_img()
        Thread(target=self._next_img,daemon=True).start()
        sleep(interval + self._AnimationTime)
        Thread(target=self.start,args=(interval,False),daemon=True).start()
    
    def _get_last_index(
        self
    ):
        if self._CarouselIndex == 0:
            return len(self._images) - 1
        else:
            return self._CarouselIndex - 1
    
    def _get_next_index(
        self
    ):
        if self._CarouselIndex == len(self._images) - 1:
            return 0
        else:
            return self._CarouselIndex + 1

    def _draw_img(
        self,mode:int=1
    ):
        this_image = self._images[self._CarouselIndex]
        if mode == 1:
            self._CarouselIndex = self._get_next_index()
            self.create_image(
                self.winfo_width() - (self._images[0].width() - (self._images[0].width() / self._OptimizeRenderMissX)) / 2,
                - (self._images[0].height() - (self._images[0].height() / self._OptimizeRenderMissX)) / 2,
                image=this_image,anchor="nw",tag="_CarouselImage"
            )
        elif mode == 2:
            self.create_image(
                self.winfo_width() - (self._images[0].width() - (self._images[0].width() / self._OptimizeRenderMissX)) / 2 - self.winfo_width(),
                - (self._images[0].height() - (self._images[0].height() / self._OptimizeRenderMissX)) / 2,
                image=this_image,anchor="nw",tag="_CarouselImage"
            )
        self.tag_raise("_CarouselWidget")
        self.tag_raise("_Index")
        self.update()

    def _next_img(
        self
    ):
        if not self._moving:
            self._draw_img()
            self._move_img()
    
    def _move_img(
        self,mode:int=1
    ):
        if self._moving:
            return None
        self._moving = True
        move_length = self.winfo_width()
        for i in range(len(self._images)):
            self._CarouselIndex = self._get_last_index()
            if i != self._CarouselIndex:
                self.itemconfigure(f"_Index{i}",image=self._IndexOutImg)
            else:
                self.itemconfigure(f"_Index{i}",image=self._IndexInImg)
            self._CarouselIndex = self._get_next_index()
        for step in self._AnimationGr:
            st = time()
            self.move(
                "_CarouselImage",-move_length * step * mode,0
            )
            sleep(self._AnimationStepTime - min(time() - st,self._AnimationStepTime))
        self._remove_outofrange_img()
        self._moving = False
    
    def _remove_outofrange_img(
        self
    ):
        for item in self.find_all():
            x = self.coords(item)[0]
            if x < - self._images[0].width() / (self._OptimizeRenderMissX * 2) * 3.5:
                self.delete(item)
    
    def _draw_indeximg(
        self
    ):
        length = self._CanvasWidth / 3 / len(self._images)
        left_x = self._CanvasWidth / 2 - length * (len(self._images) - 1) / 2
        y = self._CanvasHeight * 0.9625
        for i in range(len(self._images)):
            self.create_image(
                left_x + length * i,y,
                image=self._IndexOutImg,
                tag=["_CarouselWidget","_Index",f"_Index{i}"]
            )

class WebView:
    def __init__(
        self,master:Tk|Toplevel,url:str,
        width:int,height:int,
        x:int,y:int,debug:bool=False
    ):
        self._event_list = []
        self._master_focus = True
        self._master = master
        self._width = width
        self._height = height
        self._x = x
        self._y = y
        self._web_title = f"Tkinter_WebView_{randint(0,2**31)}"
        self._web = _webview.create_window(
            title=self._web_title,
            url=url,
            hidden=True,resizable=False
        )
        _webs.append(self._web)
        Thread(target=_webview.start,kwargs={"debug":debug}).start()
        self._init_hwnd()
        self._init_web()
        self._init()
        self._master.bind("<FocusIn>",self._master_focus_in,add=True)
        self._master.bind("<FocusOut>",self._master_focus_out,add=True)
    
    def _master_focus_in(
        self,e:tk_Event
    ):
        self._master_focus = True
    
    def _master_focus_out(
        self,e:tk_Event
    ):
        self._master_focus = False

    def _init_hwnd(
        self
    ):
        while True:
            self._web_hwnd = windll.user32.FindWindowW(None,self._web_title)
            if self._web_hwnd != 0:
                break
        self._master.update()
        self._master_hwnd = int(self._master.frame(),16)
    
    def _init_web_msg_reg(
        self
    ):
        try:
            self._web.evaluate_js('''
                function _pywebview_event_callback(e,event_type){
                    Object._msg = e;
                    Object._event_type = event_type;
                    Object._exists_msg = true;
                }
                _pywebview_event_callback._is_pywebview_listener_function = true;
                function add_event_listener(ele,event_type,_is_first_call=true){
                    if (ele[event_type] == null){
                        ele[event_type] = (e) => {_pywebview_event_callback(e,event_type)};
                    }
                    else if (! ele[event_type]._is_pywebview_listener_function){
                        callback = ele[event_type];
                        ele[event_type] = function(e){
                            callback(e);
                            _pywebview_event_callback(e,event_type);
                        }
                        ele[event_type]._is_pywebview_listener_function = true;
                    }
                    if (ele.childElementCount){
                        for (child_ele of ele.childNodes){
                            add_event_listener(child_ele);
                        }
                    }
                    if (_is_first_call){
                            setTimeout(() => {add_event_listener(ele,event_type,false);},500);
                        }
                }
                Object._exists_msg = false;
                Object._msg = null;
                Object._event_type = null;
                add_event_listener(document.body,\"onmousedown\");
            ''')
        except _webview_errors.JavascriptException:
            _setTimeout(self._init_web_msg_reg,500)
    
    def _init_web(
        self
    ):
        self._init_web_msg_reg()
        self._exec_js("True = true;")
        self._exec_js("False = false;")
        self._exec_js("None = null;")

        windll.user32.SetParent(self._web_hwnd,self._master_hwnd)
        
        windll.user32.SetWindowPos(
            self._web_hwnd,0,
            self._x,self._y,
            self._width,self._height,win32con.SWP_NOZORDER
        )

        Style = windll.user32.GetWindowLongW(self._web_hwnd,win32con.GWL_STYLE)
        Style = Style &~win32con.WS_CAPTION &~win32con.WS_SYSMENU &~win32con.WS_SIZEBOX | win32con.WS_CHILD
        windll.user32.SetWindowLongW(self._web_hwnd,win32con.GWL_STYLE,Style) ; del Style

        ExStyle = windll.user32.GetWindowLongW(self._web_hwnd,win32con.GWL_EXSTYLE)
        ExStyle = ExStyle | win32con.WS_EX_NOACTIVATE
        windll.user32.SetWindowLongW(self._web_hwnd,win32con.GWL_EXSTYLE,ExStyle) ; del ExStyle

        windll.user32.ShowWindow(self._web_hwnd,1)
        self._master.focus_force()

        Thread(target=self._event_loop,daemon=True).start()
    
    def _init(
        self
    ):
        self._exec_js("main_ele = document.body;")

    def _exec_js(
        self,code:str
    ):
        return self._web.evaluate_js(code)
    
    def reg_event(
        self,ele:str,
        event:str,func:typing.Callable,
        run_in_thread:bool=False
    ) -> str:
        self._exec_js(f"add_event_listener({ele},\"{event}\");")
        self._event_list.append(
            {
                "ele":ele,
                "event":event,
                "callback":func,
                "run_in_thread":run_in_thread
            }
        )
    
    def _event_loop(
        self
    ) -> typing.NoReturn:
        while True:
            sleep(1 / 120)
            if self._exec_js("Object._exists_msg"):
                self._exec_js("Object._exists_msg = false;")
                msg_type = self._exec_js("Object._event_type;")
                random_msg_varname = randint(0,2**31)
                self._exec_js(f"Object._{random_msg_varname}_msg = Object._msg;")
                for event in self._event_list:
                    if event["event"] == msg_type:
                        if event["run_in_thread"]:
                            Thread(target=event["callback"],args=(event,self._exec_js(f"Object._{random_msg_varname}_msg;"))).start()
                        else:
                            event["callback"](event,self._exec_js(f"Object._{random_msg_varname}_msg;"))
                self._exec_js(f"Object._{random_msg_varname}_msg = null;")
                self._exec_js(f"delete Object._{random_msg_varname}_msg;")
    
    def _update_web_rect(
        self
    ):
        windll.user32.SetWindowPos(
            self._web_hwnd,0,
            self._x,self._y,
            self._width,self._height,
            win32con.SWP_NOZORDER|win32con.SWP_NOACTIVATE
        )
    
    def hide(
        self
    ):
        windll.user32.ShowWindow(self._web_hwnd,0)
    
    def show(
        self
    ):
        windll.user32.ShowWindow(self._web_hwnd,8)
    
    def resize(
        self,
        width:int|None=None,
        height:int|None=None
    ):
        if type(width) != int or type(height) != int:
            raise TypeError("width and height must be int")
        self._width = width if width is not None else self._width
        self._height = height if height is not None else self._height
        self._update_web_rect()
    
    def move(
        self,
        x:int|None=None,
        y:int|None=None
    ):
        if type(x) != int or type(y) != int:
            raise TypeError("x and y must be int")
        self._x = x if x is not None else self._x
        self._y = y if y is not None else self._y
        self._update_web_rect()
    
    def set_style(
        self,ele:str,
        name:str,value:str
    ):
        self._exec_js(f"{ele}.style[\"{name}\"] = {value};")
    
    def get_style(
        self,ele:str,
        name:str
    ) -> typing.Any:
        return self._exec_js(f"{ele}.style[\"{name}\"];")
    
    def set_filter(
        self,ele:str,
        value:str
    ):
        self.set_style(ele,"filter",f"\"{value}\"")
    
    def get_filter(
        self,ele:str
    ) -> typing.Any:
        return self.get_style(ele,"filter")
    
    def set_blur(
        self,ele:str,
        value_px:float
    ):
        self.set_filter(ele,f"{self.get_filter(ele)} blur({value_px}px)")
    
    def get_blur(
        self,ele:str
    ) -> float|None:
        try:
            filter:str = self.get_filter(ele)
            blur = filter[filter.index("blur"):]
            blur = blur.split("(")[1].split(")")[0].replace("px","")
            return float(blur)
        except Exception:
            return None
    
    def set_brightness(
        self,ele:str,
        value:float
    ):
        "0~infty %"
        self.set_filter(ele,f"{self.get_filter(ele)} brightness({value}%)")
    
    def get_brightness(
        self,ele:str
    ) -> float|None:
        try:
            filter:str = self.get_filter(ele)
            brightness = filter[filter.index("brightness"):]
            brightness = brightness.split("(")[1].split(")")[0].replace("%","")
            return float(brightness)
        except Exception:
            return None

    def set_contrast(
        self,ele:str,
        value:float
    ):
        "0~infty %"
        self.set_filter(ele,f"{self.get_filter(ele)} contrast({value}%)")
    
    def get_contrast(
        self,ele:str
    ) -> float|None:
        try:
            filter:str = self.get_filter(ele)
            contrast = filter[filter.index("contrast"):]
            contrast = contrast.split("(")[1].split(")")[0].replace("%","")
            return float(contrast)
        except Exception:
            return None
    
    def set_grayscale(
        self,ele:str,
        value:float
    ):
        "0~100 %"
        self.set_filter(ele,f"{self.get_filter(ele)} grayscale({value}%)")
    
    def get_grayscale(
        self,ele:str
    ) -> float|None:
        try:
            filter:str = self.get_filter(ele)
            grayscale = filter[filter.index("grayscale"):]
            grayscale = grayscale.split("(")[1].split(")")[0].replace("%","")
            return float(grayscale)
        except Exception:
            return None
    
    def get_widget_hwnd(
        self
    ) -> int:
        return self._web_hwnd
    
    def get_main_ele(
        self
    ) -> typing.Any:
        return self._exec_js("main_ele;")
    
    def get_event_list(
        self
    ) -> list:
        return self._event_list

    def destroy(
        self
    ):
        _webs.remove(self._web)
        self._web.destroy()
        self.destroy = lambda:None

    @property
    def widget_width(
        self
    ) -> int:
        return self._width
    
    @property
    def widget_height(
        self
    ) -> int:
        return self._height
    
    @property
    def widget_x(
        self
    ) -> int:
        return self._x
    
    @property
    def widget_y(
        self
    ) -> int:
        return self._y

class VideoPlayer(WebView):
    def _init(
        self
    ):
        self.loaded = False
        self.controlsList = ["nodownload","noplaybackrate"]
        self._exec_js("main_ele = document.getElementsByName(\"media\")[0];")
        self._exec_js("main_ele.setAttribute(\"disablepictureinpicture\",null);")
        self.set_style("main_ele","width","\"100%\"")
        self.set_style("main_ele","height","\"100%\"")
        self.update_controlsList()
        self.pause()
        self.reg_event("main_ele","onload",lambda e,obj:self.__setattr__("loaded",True))
    
    def is_loop(
        self
    ) -> bool:
        return self._exec_js("main_ele.loop;")
    
    def set_loop(
        self,value:bool
    ):
        self._exec_js(f"main_ele.loop = {value};")
    
    def loaded_callback(
        self,func:typing.Callable
    ):
        if not self.loaded:
            _setTimeout(func,200)
        else:
            func()
    
    def hide_controls(
        self
    ):
        self._exec_js("main_ele.removeAttribute(\"controls\");")
    
    def show_controls(
        self
    ):
        self._exec_js("main_ele.setAttribute(\"controls\",null);")
    
    def has_controls(
        self
    ) -> bool:
        return self._exec_js("main_ele.hasAttribute(\"controls\");")

    def update_controlsList(
        self
    ):
        if set([type(item) for item in self.controlsList]) != {str}:
            raise TypeError("controlsList must be list of string")
        self._exec_js(f"main_ele.setAttribute(\"controlsList\",\"{" ".join(self.controlsList)}\");")
    
    def get_controlsList(
        self
    ) -> list[str]|None:
        cl:str|None = self._exec_js("main_ele.getAttribute(\"controlsList\");")
        if cl is None:
            return None
        try:
            return cl.split(" ")
        except Exception:
            return None

    def play(
        self
    ):
        self._exec_js("main_ele.play();")
    
    def pause(
        self
    ):
        self._exec_js("main_ele.pause();")
    
    def set_volume(
        self,volume:float|int
    ):
        "0.0 ~ 1.0"
        self._exec_js(f"main_ele.volume = {volume};")
    
    def get_volume(
        self
    ) -> float|int:
        "0.0 ~ 1.0"
        return self._exec_js("main_ele.volume;")

    def set_speed(
        self,speed:float|int
    ):
        self._exec_js(f"main_ele.playbackRate = {speed};")
    
    def get_speed(
        self
    ) -> float|int:
        return self._exec_js("main_ele.playbackRate;")
    
    def set_pos(
        self,pos:float|int
    ):
        self._exec_js(f"main_ele.currentTime = {pos};")
    
    def get_pos(
        self
    ) -> float|int:
        return self._exec_js("main_ele.currentTime;")

    def get_playing(
        self
    ) -> bool:
        return not self._exec_js("main_ele.paused;")

    def get_duration(
        self
    ) -> float|None:
        return self._exec_js("main_ele.duration;")
    
    def set_background(
        self,value:str
    ) -> str:
        return self._exec_js(f"main_ele.style.background = \"{value}\";")

    def get_background(
        self
    ) -> str:
        return self._exec_js("main_ele.style.background;")

class AudioPlayer(VideoPlayer):
    def _init(
        self
    ):
        VideoPlayer._init(self)
        self.set_background("#ffffff")

class ImageWidget(WebView):
    def _init(
        self
    ):
        self._exec_js("main_ele = document.getElementsByTagName(\"img\")[0];")

_webview.threading.current_thread = ban_threadtest_current_thread

__all__ = (
    "WebViewWidgetExitCall",
    "Carousel",
    "WebView",
    "VideoPlayer",
    "AudioPlayer",
    "ImageWidget"
)

#def _test():
#    from tkinter import Tk
#    root = Tk()
#    root.resizable(False,False)
#    car = Carousel([Image.open(f"{i}.jpg") for i in range(1,7)],(1920//3,1080//3),highlightthickness=0)
#    car.pack()
#    Thread(target=car.start).start()
#    root.mainloop()

#def _test():
#    root = Tk()
#    w,h = int(root.winfo_screenwidth() * 0.75),int(root.winfo_screenheight() * 0.75)
#    root.protocol("WM_DELETE_WINDOW",lambda:WebViewWidgetExitCall(root))
#    root.geometry(f"{w}x{h}")
#    player = WebView(root,"https://www.desmos.com/calculator?lang=zh-CN",w,h,0,0)
#    root.bind("<Configure>",lambda e:player.resize(e.width,e.height))
#    root.mainloop()

#def _test():
#    root = Tk()
#    w,h = int(root.winfo_screenwidth() * 0.75),int(root.winfo_screenheight() * 0.75)
#    root.protocol("WM_DELETE_WINDOW",lambda:WebViewWidgetExitCall(root))
#    root.geometry(f"{w}x{h}")
#    player = VideoPlayer(root,"./test.mp4",w,h,0,0)
#    root.bind("<Configure>",lambda e:player.resize(e.width,e.height))
#    root.mainloop()

def _test():
    root = Tk()
    w,h = int(root.winfo_screenwidth() * 0.25),int(root.winfo_screenheight() * 0.25)
    root.protocol("WM_DELETE_WINDOW",lambda:WebViewWidgetExitCall(root))
    root.geometry(f"{w}x{h}")
    player = AudioPlayer(root,"./test.mp3",w,h,0,0)
    player.set_background("rgb(0,120,215)")
    player.set_loop(True)
    root.bind("<Configure>",lambda e:player.resize(e.width,e.height))
    root.mainloop()

#def _test():
#    root = Tk()
#    w,h = int(root.winfo_screenwidth() * 0.75),int(root.winfo_screenheight() * 0.75)
#    root.protocol("WM_DELETE_WINDOW",lambda:WebViewWidgetExitCall(root))
#    root.geometry(f"{w}x{h}")
#    img = ImageWidget(root,"./test.jpg",w,h,0,0)
#    root.bind("<Configure>",lambda e:img.resize(e.width,e.height))
#    root.mainloop()

if __name__ == "__main__":
    _test()