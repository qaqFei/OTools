from __future__ import annotations
from ctypes import windll
import threading
import typing
import http.server
import io
import time

from PIL import Image
import webview
import pyautogui

current_thread = threading.current_thread
screen_size = pyautogui.size()

class WebCanvas_FileServerHandler(http.server.BaseHTTPRequestHandler):
    _canvas:WebCanvas

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "image/png")
        self.end_headers()
        try:
            im = self._canvas._regims[self.path[1:]]
        except KeyError:
            self.wfile.write(b"Not Found")
            return
        temp_btyeio = io.BytesIO()
        im.save(temp_btyeio,"png")
        self.wfile.write(temp_btyeio.getvalue())

def ban_threadtest_current_thread():
    obj = current_thread()
    obj.name = "MainThread"
    return obj

webview.threading.current_thread = ban_threadtest_current_thread

class WebCanvas:
    def __init__(
        self,
        width:int,height:int,
        x:int,y:int,
        hidden:bool = False,
        debug:bool = False,
        title:str = "WebCanvas"
    ):
        self._web = webview.create_window(
            title=title,
            url=".\\web_canvas.html",
            resizable=False
        )
        self._web_init_var = {
            "width":width,
            "height":height,
            "x":x,
            "y":y
        }
        self._destroyed = False
        self.debug = debug
        self._regims = {}
        self._is_loadimg = {}
        self._JavaScript_WaitToExecute_CodeArray = []
        threading.Thread(target=webview.start,kwargs={"debug":self.debug},daemon=True).start()
        self._init()
        if hidden:
            self.withdraw()
    
    def title(
        self,title:typing.Union[str,None]
    ) -> str:
        if title is None:
            return self._web.title
        self._web.set_title(title)
        return title
    
    def winfo_screenwidth(
        self
    ) -> int:
        return screen_size.width
    
    def winfo_screenheight(
        self
    ) -> int:
        return screen_size.height
    
    def winfo_width(
        self
    ) -> int:
        return self._web.width
    
    def winfo_height(
        self
    ) -> int:
        return self._web.height
    
    def winfo_x(
        self
    ) -> int:
        return self._web.x
    
    def winfo_y(
        self
    ) -> int:
        return self._web.y
    
    def winfo_focus(
        self
    ) -> bool:
        return self._web.focus

    def winfo_hwnd(
        self
    ) -> int:
        return self._web_hwnd
    
    def winfo_legacywindowwidth(
        self
    ) -> int:
        return self._web.evaluate_js("window.innerWidth;")
    
    def winfo_legacywindowheight(
        self
    ) -> int:
        return self._web.evaluate_js("window.innerHeight;")

    def destroy(
        self
    ):
        self._web.destroy()
    
    def maximize(
        self
    ):
        self._web.maximize()
    
    def resize(
        self,
        width:int,height:int
    ):
        self._web.set_window_size(width=width,height=height)
    
    def move(
        self,
        x:int,y:int
    ):
        self._web.move(x=x,y=y)
    
    def withdraw(
        self
    ):
        self._web.hide()
    
    def deiconify(
        self
    ):
        self._web.show()
    
    def iconify(
        self
    ):
        self._web.minimize()
    
    def run_js_code(
        self,
        code:str,
        threading_:bool = False,
        add_code_array:bool = False
    ):
        if add_code_array:
            self.Add_Code_To_JavaScript_WaitToExecute_CodeArray(code)
        else:
            if threading_:
                threading.Thread(target=self._web.evaluate_js,args=(code,),daemon=True).start()
            else:
                return self._web.evaluate_js(code)
    
    def run_js_wait_code(
        self
    ):
        self._web.evaluate_js(f"JavaScript_WaitToExecute_CodeArray = {self._JavaScript_WaitToExecute_CodeArray};")
        self._web.evaluate_js("process_jswteca();")
        self._JavaScript_WaitToExecute_CodeArray.clear()
    
    def Add_Code_To_JavaScript_WaitToExecute_CodeArray(
        self,code:str
    ):
        self._JavaScript_WaitToExecute_CodeArray.append(code)
    
    def _set_style_fill_stroke(
        self,
        fillStyle:typing.Union[str,None] = None,
        strokeStyle:typing.Union[str,None] = None
    ) -> str:
        code = ""
        if fillStyle is not None:
            code += f"ctx.fillStyle = \"{fillStyle}\";"
        else:
            code += "ctx.fillStyle = \"#000000\";"
        if strokeStyle is not None:
            code += f"ctx.strokeStyle = \"{strokeStyle}\";"
        else:
            code += "ctx.strokeStyle = \"#000000\";"
        return code
    
    def _set_style_font_textAlign_textBaseline_direction(
        self,
        font:typing.Union[str,None] = None,
        textAlign:typing.Literal["start","end","left","right","center"] = "start",
        textBaseline:typing.Literal["top","hanging","middle","alphabetic","ideographic","bottom"] = "alphabetic",
        direction:typing.Literal["ltr","rtl","inherit"] = "inherit"
    ) -> str:
        code = ""
        if font is not None:
            code += f"ctx.font = \"{font}\";"
        else:
            code += "ctx.font = \"10px sans-serif\";"
        code += f"ctx.textAlign = \"{textAlign}\";"
        code += f"ctx.textBaseline = \"{textBaseline}\";"
        code += f"ctx.direction = \"{direction}\";"
        return code
    
    def _process_code_string_syntax_tostring(
        self,code:str
    ):
        r_code = ""
        for c in code:
            if c == "'":
                r_code += "\\'"
            elif c == "\"":
                r_code += "\\\""
            elif c == "`":
                r_code += "\\`"
            elif c == "\\":
                r_code += "\\\\"
            else:
                r_code += c
        return r_code
    
    def _process_code_string_syntax_tocode(
        self,code:str
    ):
        return f"'{self._process_code_string_syntax_tostring(code)}'"
    
    def create_rectangle(
        self,
        x0:typing.Union[int,float],y0:typing.Union[int,float],
        x1:typing.Union[int,float],y1:typing.Union[int,float],
        fillStyle:typing.Union[str,None] = None,
        strokeStyle:typing.Union[str,None] = None,
        threading_:bool = False,
        wait_execute:bool = False
    ):
        code = self._set_style_fill_stroke(fillStyle,strokeStyle) + f"\
            ctx.fillRect({x0},{y0},{x1-x0},{y1-y0});\
        "
        self.run_js_code(code,threading_,wait_execute)
    
    def create_line(
        self,
        x0:typing.Union[int,float],y0:typing.Union[int,float],
        x1:typing.Union[int,float],y1:typing.Union[int,float],
        lineWidth:int = 1,
        fillStyle:typing.Union[str,None] = None,
        strokeStyle:typing.Union[str,None] = None,
        threading_:bool = False,
        wait_execute:bool = False
    ):
        code = self._set_style_fill_stroke(fillStyle,strokeStyle) + f"\
            ctx.lineWidth = {lineWidth};\
            ctx.beginPath();\
            ctx.moveTo({x0},{y0});\
            ctx.lineTo({x1},{y1});\
            ctx.closePath();\
            ctx.stroke();\
            ctx.lineWidth = 1;\
        "
        self.run_js_code(code,threading_,wait_execute)
    
    def create_arc(
        self,
        x:typing.Union[int,float],y:typing.Union[int,float],
        r:typing.Union[int,float],
        start:int,end:int,
        lineWidth:int = 1,
        fillStyle:typing.Union[str,None] = None,
        strokeStyle:typing.Union[str,None] = None,
        threading_:bool = False,
        wait_execute:bool = False
    ):
        code = self._set_style_fill_stroke(fillStyle,strokeStyle) + f"\
            ctx.lineWidth = {lineWidth};\
            ctx.beginPath();\
            ctx.arc({x},{y},{r},{start},{end});\
            ctx.closePath();\
            ctx.stroke();\
            ctx.lineWidth = 1;\
        "
        self.run_js_code(code,threading_,wait_execute)
    
    def create_circle(
        self,
        x:typing.Union[int,float],y:typing.Union[int,float],
        r:typing.Union[int,float],
        lineWidth:int = 1,
        fillStyle:typing.Union[str,None] = None,
        strokeStyle:typing.Union[str,None] = None,
        threading_:bool = False,
        wait_execute:bool = False
    ):
        return self.create_arc(
            x,y,r,
            0,360,
            lineWidth,
            fillStyle,strokeStyle,
            threading_,
            wait_execute
        )

    def create_text(
        self,
        text:str,
        x:typing.Union[int,float],y:typing.Union[int,float],
        font:typing.Union[str,None] = None,
        textAlign:typing.Literal["start","end","left","right","center"] = "start",
        textBaseline:typing.Literal["top","hanging","middle","alphabetic","ideographic","bottom"] = "alphabetic",
        direction:typing.Literal["ltr","rtl","inherit"] = "inherit",
        fillStyle:typing.Union[str,None] = None,
        strokeStyle:typing.Union[str,None] = None,
        threading_:bool = False,
        wait_execute:bool = False
    ):
        text = self._process_code_string_syntax_tostring(text)
        code = self._set_style_fill_stroke(fillStyle,strokeStyle) + self._set_style_font_textAlign_textBaseline_direction(font,textAlign,textBaseline,direction) + f"\
            ctx.fillText(\"{text}\",{x},{y});\
        "
        self.run_js_code(code,threading_,wait_execute)
    
    def create_polygon(
        self,points:typing.Iterator[typing.Tuple[typing.Union[int,float],typing.Union[int,float]]],
        fillStyle:typing.Union[str,None] = None,
        strokeStyle:typing.Union[str,None] = None,
        threading_:bool = False,
        wait_execute:bool = False
    ):
        code = self._set_style_fill_stroke(fillStyle,strokeStyle) + f"\
            ctx.beginPath();\
        "
        for index,point in enumerate(points):
            if index == 0:
                code += f"ctx.moveTo({point[0]},{point[1]});"
            else:
                code += f"ctx.lineTo({point[0]},{point[1]});"
        code += f"\
            ctx.closePath();\
            ctx.stroke();\
            ctx.fill();\
        "
        self.run_js_code(code,threading_,wait_execute)
    
    def create_image(
        self,
        imgname:str,
        x:typing.Union[int,float],y:typing.Union[int,float],
        width:typing.Union[int,float],height:typing.Union[int,float],
        threading_:bool = False,
        wait_execute:bool = False
    ):
        if imgname not in self._is_loadimg:
            raise ValueError("Image not found.")
        if not self._is_loadimg[imgname]:
            self._load_img(imgname)
        code = f"\
            if ({imgname}_img.complete){chr(123)}\
                ctx.drawImage({imgname}_img,{x},{y},{width},{height});\
            {chr(125)}\
            else{chr(123)}\
                {imgname}_img_onloadfuncs.push([{x},{y},{width},{height}]);\
            {chr(125)}\
        "
        self.run_js_code(code,threading_,wait_execute)

    def clear_rectangle(
        self,
        x0:typing.Union[int,float],y0:typing.Union[int,float],
        x1:typing.Union[int,float],y1:typing.Union[int,float],
        threading_:bool = False,
        wait_execute:bool = False
    ):
        self.run_js_code(f"ctx.clearRect({x0},{y0},{x1-x0},{y1-y0});",threading_,wait_execute)
    
    def clear_canvas(
        self,
        threading_:bool = False,
        wait_execute:bool = False
    ):
        self.run_js_code("ctx.clearRect(0,0,canvas_ele.width,canvas_ele.height);",threading_,wait_execute)
    
    def reg_img(
        self,im:Image.Image,
        name:str
    ):
        self._regims.update({name:im})
        self._is_loadimg[name] = False
    
    def load_allimg(
        self
    ):
        for imgname in self._regims:
            self._load_img(imgname)
        while True:
            complete_list:typing.List[bool] = self.run_js_code("["+",".join([f"{item}_img.complete" for item in self._regims])+"]")
            if list(set(complete_list)) == [True]:
                break
            time.sleep(0.2)
    
    def reg_event(
        self,name:str,
        callback:typing.Callable[[]]
    ):
        setattr(self._web.events,name,getattr(self._web.events,name) + callback)
    
    def loop_to_close(
        self
    ):
        while True:
            if self._destroyed:
                return None
            time.sleep(0.05)
    
    def shutdown_fileserver(
        self
    ):
        self._file_server.shutdown()
    
    def _closed_callback(
        self
    ):
        self._destroyed = True
    
    def _load_img(
        self,imgname:str
    ):
        code = f"\
        if (!window.{imgname}_img){chr(123)}\
            {imgname}_img = document.createElement('img');\
            {imgname}_img.src = 'http://127.0.0.1:{self._web_port + 1}/{imgname}';\
            {imgname}_img.loading = \"eager\";\
            {imgname}_img_onloadfuncs = new Array();\
            {imgname}_img.onload = function(){chr(123)}\
                for (code of {imgname}_img_onloadfuncs){chr(123)}\
                    ctx.drawImage({imgname}_img,code[0],code[1],code[2],code[3]);\
                {chr(125)}\
            {chr(125)}\
        {chr(125)}\
        "
        self.run_js_code(code)
        self._is_loadimg[imgname] = True

    def _init(
        self
    ):
        self._web.set_window_size(width=self._web_init_var["width"],height=self._web_init_var["height"])
        self._web.move(x=self._web_init_var["x"],y=self._web_init_var["y"])
        self._web_init_var = None
        self._web.events.closed += self._closed_callback
        
        while True:
            self._web_hwnd = windll.user32.FindWindowW(None,self._web.title)
            if self._web_hwnd != 0:
                break
        
        self._web_port = int(self._web._server.address.split(":")[2].split("/")[0])
        WebCanvas_FileServerHandler._canvas = self
        self._file_server = http.server.HTTPServer(("localhost",self._web_port + 1),WebCanvas_FileServerHandler)
        threading.Thread(target=lambda:self._file_server.serve_forever(poll_interval=0),daemon=True).start()
        
if __name__ == "__main__":
    from sys import argv
    import random
    wc = WebCanvas(1920 // 2,1080 // 2,100,100,debug=True)
    n = 100
    wc.reg_img(Image.open(argv[1]).resize((int(1920 / 4),int(1080 / 4))),"test")
    for i in range(n):
        wc.create_rectangle(random.randint(0,50),random.randint(0,50),random.randint(51,100),random.randint(51,100),fillStyle=f"rgb{(random.randint(0,255),random.randint(0,255),random.randint(0,255))}",wait_execute=True)
        wc.create_line(random.randint(0,250),random.randint(0,250),random.randint(0,250),random.randint(0,250),lineWidth=random.randint(0,12),strokeStyle=f"rgb{(random.randint(0,255),random.randint(0,255),random.randint(0,255))}",wait_execute=True)
        wc.create_arc(random.randint(0,150),random.randint(0,150),random.randint(0,25),0,random.randint(0,360),lineWidth=random.randint(0,12),strokeStyle=f"rgb{(random.randint(0,255),random.randint(0,255),random.randint(0,255))}",wait_execute=True)
        wc.create_circle(random.randint(150,350),random.randint(150,350),random.randint(0,25),lineWidth=random.randint(0,12),strokeStyle=f"rgb{(random.randint(0,255),random.randint(0,255),random.randint(0,255))}",wait_execute=True)
        wc.create_text("\"`'Hello World!'`\"",random.randint(150,350),random.randint(150,350),wait_execute=True)
        if (i + 1) % int(n / 10) == 0:
            print(f"{i + 1} / {n}")
    wc.run_js_wait_code()
    wc.create_image("test",200,200,1920/4,1080/4)
    wc.loop_to_close()
    windll.kernel32.ExitProcess(0)