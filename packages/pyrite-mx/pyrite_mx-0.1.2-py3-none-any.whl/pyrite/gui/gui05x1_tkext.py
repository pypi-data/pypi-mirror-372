from tkinter import Misc
from typing import Any, Literal
from . import gui01x0_tktraits as tktraits
from . import gui02x0_tktypes as tktypes
from . import gui03x0_tktools as tktools
from .gui04x1_tkliterals import *

class VerticalScrolledFrame(tktypes.Frame):
    class MyCanvas(tktypes.Canvas):
        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args,**kwargs)
        def yview(self,*args):
            super().yview(*args)
        def yview_scroll(self,*args,**kwargs):
            super().yview_scroll(*args,**kwargs)
            
        def yview_moveto(self,*args,**kwargs):
            super().yview_moveto(*args,**kwargs)

    class MyScrollbar(tktypes.Scrollbar):
        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args,**kwargs)
        def set(self,first,last):
            super().set(first,last)
            f, l = self.get()
            if f <= 0.0 or l >= 1.0:
                self.event_generate('<<scroll_limit_reached>>', when="tail")


    def __init__(self, master, *args, **kw):
        tktypes.Frame.__init__(self, master, *args, **kw)

        self.cw = 0
        self.sw = 0
        self.sh = 0
        self.inner_frame = tktypes.Frame(self)
        self.inner_frame.pack(side=tkside.TOP, fill=tkfill.X)
        self.inner_frame.pack_propagate(False)
        self.pack_propagate(False)

        # Create a canvas object and a vertical scrollbar for scrolling it.
        vscrollbar = self.MyScrollbar(self.inner_frame, orient=tkorient.VERTICAL)
        vscrollbar.pack(side=tkside.RIGHT, fill=tkfill.Y, expand=tkexpand.NO, anchor=tkanchor.N)
        self.canvas = tktypes.Canvas(self.inner_frame, bd=0, highlightthickness=0, 
                                width = 0, height = 0,
                                yscrollcommand=vscrollbar.set)
        self.canvas.pack(side=tkside.LEFT, fill=tkfill.BOTH, expand=tkexpand.YES, anchor=tkanchor.N)
        #self.canvas.pack_propagate(False)
        vscrollbar.config(command = self.canvas.yview)
        self.vscrollbar = vscrollbar
        # Reset the view
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        # Create a frame inside the canvas which will be scrolled with it.
        self.interior = tktypes.Frame(self.canvas,height=0)
        self.interior.bind('<Configure>', self._configure_interior)
        self.canvas.bind('<Configure>', self._configure_canvas)
        self.bind('<Configure>', self._configure_inner_frame)
        #self.vscrollbar.bind('<<scroll_limit_reached>>', self._scroll_limit_reached)
        self.interior_id = self.canvas.create_window(0, 0, window=self.interior, anchor=tkanchor.NW)
        self.after_id = None
        self.last_scroll = (-1,-1)

        self.rebind()

    def scroll(self,target):
        if target == 'top':
            self.canvas.yview_moveto(0)

    def _scroll_limit_reached(self, event):
        return
        lfirst, llast = self.last_scroll
        first, last = self.vscrollbar.get()
        l, t, r, b = self.canvas.bbox('all')
        ih =  self.inner_frame.winfo_height()
        h = b - t
        print('_scroll_limit_reached: ', (first, last), (lfirst, llast), (l,t,r,b), ih)
        self.last_scroll = (first,last)
        if first<=0:         
            if self.after_id is not None:
                self.after_cancel(self.after_id)  
            self.after_id = self.after(300,lambda self=self:self.canvas.yview_scroll(24/h, 'units'))
        elif last>=1:
            if self.after_id is not None:
                self.after_cancel(self.after_id)  
            self.after_id = self.after(300,lambda self=self:self.canvas.yview_scroll(-24/h,'units'))

    def __refresh(self, height=None):
        if height is None:
            height = self.winfo_height()
        bbl, bbt, bbr, bbb = self.canvas.bbox("all")
        #self.canvas.config(scrollregion=(bbl,bbt-17,bbr,bbb+16))
        bbh = bbb - bbt
        h = height
        if h > bbh:
            h = bbh
            self.canvas.config(scrollregion=(bbl,bbt,bbr,bbb))
        else:
            #self.canvas.config(scrollregion=(bbl,bbt-17,bbr,bbb+16))
            self.canvas.config(scrollregion=(bbl,bbt-25,bbr,bbb+24))
        self.inner_frame.config(height=h)
        #print(f'VerticalScrolledFrame.__refresh: bbl={bbl}, bbt={bbt}, bbr={bbr}, bbb={bbb}, bbh={bbh}, h={h}')

    def _configure_inner_frame(self, event):
        if event.widget.winfo_id() == self.winfo_id():
            self.__refresh(event.height)
            #bbl, bbt, bbr, bbb = self.canvas.bbox("all")
            #bbh = bbb - bbt
            #h = event.height
            #if h > bbh:
            #    h = bbh
            #self.inner_frame.config(height=h)

    def _configure_interior(self, event):
        #print(f'_configure_interior {event.widget.winfo_name()} ~ {self.winfo_name()}')
        #self.canvas.config(scrollregion=self.canvas.bbox("all"))
        self.__refresh()

    def _configure_canvas(self, event):
        #print(f'_configure_canvas {event.widget.winfo_name()} ~ {self.winfo_name()}')
        self.canvas.itemconfigure(self.interior_id, width=self.canvas.winfo_width())

    def on_mouse_wheel(self, event):
        self.canvas.yview_scroll(int(-event.delta/120),"units")
        return "break" 
    
    def rebind(self):
        def recursive_bind(widget,event,handler):
            widget.bind(event,handler)
            for ww in widget.winfo_children():
                recursive_bind(ww,event,handler)
        recursive_bind(self.interior,"<MouseWheel>", self.on_mouse_wheel)


