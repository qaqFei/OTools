from tkinter import Tk,Toplevel,Event

from win32api import GetCursorPos

def AddWindowChangeSizeFrame(Window:Tk|Toplevel,frame_width:int):
    mouse_style = "normal"
    start_pos = [None,None]
    def _Change_Style(style_type:str):
        nonlocal mouse_style
        bak = Window["cursor"]
        Window.configure(cursor={
            "up":"sb_v_double_arrow",
            "down":"sb_v_double_arrow",
            "left":"sb_h_double_arrow",
            "right":"sb_h_double_arrow",
            "left & up":"arrow", #Unknow use what style name ......
            "right & up":"arrow",
            "left & down":"arrow",
            "right & down":"arrow",
            "normal":bak if bak == "fleur" else "arrow"
        }[style_type])
        mouse_style = style_type
        if style_type == "normal":
            try: delattr(Window,"_window_change_size_frame_cursor_style")
            except AttributeError: pass
        else:
            try: setattr(Window,"_window_change_size_frame_cursor_style",True)
            except AttributeError: pass
    def _Moving(event:Event):
        x,y = event.x,event.y
        window_width,window_height = Window.winfo_width(),Window.winfo_height()
        frame_width_x = 2
        if y < frame_width and x > frame_width and x < window_width-frame_width:
            _Change_Style("up")
        elif y > window_height-frame_width and x > frame_width and x < window_width-frame_width:
            _Change_Style("down")
        elif x < frame_width and y > frame_width and y < window_height-frame_width:
            _Change_Style("left")
        elif x > window_width-frame_width and y > frame_width and y < window_height-frame_width:
            _Change_Style("right")
        elif x < frame_width * frame_width_x and y < frame_width * frame_width_x:
            _Change_Style("left & up")
        elif x > window_width - frame_width * frame_width_x and y < frame_width * frame_width_x:
            _Change_Style("right & up")
        elif x < frame_width * frame_width_x and y > window_height - frame_width * frame_width_x:
            _Change_Style("left & down")
        elif x > window_width - frame_width * frame_width_x and y > window_height - frame_width * frame_width_x:
            _Change_Style("right & down")
        else:
            _Change_Style("normal")
    def _Click(event:Event):
        pos = GetCursorPos()
        start_pos[0] = pos[0]
        start_pos[1] = pos[1]
    def _ClickMoving(event:Event):
        nonlocal start_pos
        if mouse_style == "normal":
            return None
        x,y = GetCursorPos()
        match mouse_style:
            case "down":
                dy = y - start_pos[1]
                ww,wh = Window.winfo_width(),Window.winfo_height()+dy
                if wh < frame_width * 2:
                    return None
                Window.geometry(f"{ww}x{wh}")
            case "up":
                dy = y - start_pos[1]
                ww,wh = Window.winfo_width(),Window.winfo_height()-dy
                wx,wy = Window.winfo_x(),Window.winfo_y()+dy
                if wh < frame_width * 2:
                    return None
                Window.geometry(f"{ww}x{wh}+{wx}+{wy}")
            case "left":
                dx = x - start_pos[0]
                ww,wh = Window.winfo_width()-dx,Window.winfo_height()
                wx,wy = Window.winfo_x()+dx,Window.winfo_y()
                if ww < frame_width * 2:
                    return None
                Window.geometry(f"{ww}x{wh}+{wx}+{wy}")
            case "right":
                dx = x - start_pos[0]
                ww,wh = Window.winfo_width()+dx,Window.winfo_height()
                if ww < frame_width * 2:
                    return None
                Window.geometry(f"{ww}x{wh}")
            case "left & up":
                dx,dy = x - start_pos[0],y - start_pos[1]
                ww,wh = Window.winfo_width()-dx,Window.winfo_height()-dy
                wx,wy = Window.winfo_x()+dx,Window.winfo_y()+dy
                if ww < frame_width * 2 or wh < frame_width * 2:
                    return None
                Window.geometry(f"{ww}x{wh}+{wx}+{wy}")
            case "right & up":
                dx,dy = x - start_pos[0],y - start_pos[1]
                ww,wh = Window.winfo_width()+dx,Window.winfo_height()-dy
                wx,wy = Window.winfo_x(),Window.winfo_y()+dy
                if ww < frame_width * 2 or wh < frame_width * 2:
                    return None
                Window.geometry(f"{ww}x{wh}+{wx}+{wy}")
            case "left & down":
                dx,dy = x - start_pos[0],y - start_pos[1]
                ww,wh = Window.winfo_width()-dx,Window.winfo_height()+dy
                wx,wy = Window.winfo_x()+dx,Window.winfo_y()
                if ww < frame_width * 2 or wh < frame_width * 2:
                    return None
                Window.geometry(f"{ww}x{wh}+{wx}+{wy}")
            case "right & down":
                dx,dy = x - start_pos[0],y - start_pos[1]
                ww,wh = Window.winfo_width()+dx,Window.winfo_height()+dy
                if ww < frame_width * 2 or wh < frame_width * 2:
                    return None
                Window.geometry(f"{ww}x{wh}")
        start_pos[0] = x
        start_pos[1] = y
    Window.bind("<Motion>",_Moving,add=True)
    Window.bind("<Button-1>",_Click,add=True)
    Window.bind("<B1-Motion>",_ClickMoving,add=True)

def _test():
    from tkinter import Label
    import SetWindowMoveWidget
    root = Tk()
    SetWindowMoveWidget.SetWindowMoveWidget(root,root)
    root.overrideredirect(True)
    root.geometry("400x300")
    Label(text="Hello World!").pack()
    root.title("Test")
    AddWindowChangeSizeFrame(root,20)
    root.mainloop()

if __name__ == "__main__":
    _test()