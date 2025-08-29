
from . import gui06x2_tktraits as tktraits
from . import gui08x2_tktypes as tktypes
from . import gui07x2_tktools as tools
from . import gui05x1_tkext as tkext
from . import gui16x1_winapi as winapi
from . import gui14x1_wintraits as wintraits
from .gui04x1_tkliterals import *
from ..helpers import signature
import sys

#from pycore import smartscope

#import types

class context:
    app : tktypes.AppWindow = None

    @staticmethod
    def init(title=None, visible=True, iconized=False, w=800, h=600, window_class=None, **kwargs):
        if context.app is None:
            winapi.SetProcessDpiAwarenessContext(wintraits.DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2)
            if window_class is None:
                context.app = tktypes.AppWindow(**kwargs)
                #context.app.withdraw()
                #gui.tktools.set_theme('dark')
                #tools.set_theme("dark")            
                context.app.title(title)
                #context.app.geometry(f'{w}x{h}')
                #tktools.window_frame.center(app)
                #hidden=False
                #if iconized:
                #    context.app.after(300,lambda window=context.app:window.state('iconic') if winapi.GetParent(winapi.GetParent(window.winfo_id()))==0 else None)
                #    hidden=True
                #if not visible:
                #    hidden=True
                #if not hidden:
                #    context.app.after(300,lambda window=context.app:window.state('normal') if winapi.GetParent(winapi.GetParent(window.winfo_id()))==0 else None)
                
            else:
                context.app = window_class(**kwargs)
        return context.app

def run():
    context.app.mainloop()

def after(*args,**kwargs):
    return context.app.after(*args,**kwargs)


def event_generate(*args,**kwargs):
    return context.app.event_generate(*args,**kwargs)

init = context.init

