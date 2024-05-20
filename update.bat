@echo off

del .\Tkinter\Window\_TkinterImageDrawOptimize.py
del .\Tkinter\Widget\_TkinterImageDrawOptimize.py
del .\Tkinter\Window\_Widgets.py

echo f | xcopy .\Pillow\TkinterImageDrawOptimize.py .\Tkinter\Window\_TkinterImageDrawOptimize.py
echo f | xcopy .\Pillow\TkinterImageDrawOptimize.py .\Tkinter\Widget\_TkinterImageDrawOptimize.py
echo f | xcopy .\Tkinter\Widget\Widgets.py .\Tkinter\Window\_Widgets.py

pause